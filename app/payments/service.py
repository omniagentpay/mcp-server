from typing import List
from app.payments.providers import PaymentProvider
from app.payments.guards import PaymentGuard
from app.wallets.service import WalletService
from app.ledger.service import LedgerService
from app.utils.exceptions import PaymentError
import structlog
import uuid

logger = structlog.get_logger(__name__)

class PaymentService:
    def __init__(
        self, 
        wallet_service: WalletService, 
        ledger_service: LedgerService,
        guards: List[PaymentGuard],
        providers: dict[str, PaymentProvider]
    ):
        self.wallet_service = wallet_service
        self.ledger_service = ledger_service
        self.guards = guards
        self.providers = providers

    async def execute_guarded_payment(
        self, 
        amount: float, 
        currency: str, 
        source_wallet_id: str,
        destination: str,
        provider_type: str = "direct"
    ):
        logger.info("payment_initiated", amount=amount, currency=currency, source=source_wallet_id)
        
        source_uuid = uuid.UUID(source_wallet_id)

        # 1. Validate payment intent and wallet existence (with lock for atomic check)
        wallet = await self.wallet_service.get_wallet_for_update(source_uuid)
        if not wallet:
            raise PaymentError(f"Source wallet {source_wallet_id} not found")
        
        if wallet.balance < amount:
            raise PaymentError(f"Insufficient funds in source wallet")

        # 2. Run guard checks
        for guard in self.guards:
            await guard.validate(amount, source_wallet_id, recipient=destination)

        # 3. Select payment provider
        provider = self.providers.get(provider_type)
        if not provider:
            raise PaymentError(f"Unsupported payment provider: {provider_type}")

        # 4. Record transaction in ledger (Initial pending state)
        await self.ledger_service.record_transaction(
            wallet_id=wallet.id,
            amount=-amount,
            entry_type="debit",
            description=f"Payment to {destination}",
            status="pending",
            provider=provider_type,
            intent={"amount": amount, "currency": currency, "destination": destination}
        )

        # 5. Call provider
        try:
            provider_response = await provider.initiate_transfer(amount, currency, destination)
            
            # 6. Finalize ledger/wallet updates
            # Atomic update within the same transaction
            await self.ledger_service.record_transaction(
                wallet_id=wallet.id,
                amount=-amount,
                entry_type="debit",
                description=f"Payment completion: {destination}",
                status="completed",
                provider=provider_type,
                result=provider_response
            )
            
            # Use service update for consistency
            await self.wallet_service.update_balance(wallet.id, -amount)
            await self.ledger_service.db.commit()
            
            return provider_response
        except Exception as e:
            logger.error("payment_provider_failed", error=str(e))
            # Handle rollback/failed state in ledger if necessary
            raise PaymentError(f"Payment provider failed: {str(e)}")
