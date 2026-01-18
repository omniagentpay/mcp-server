import asyncio
import structlog
from decimal import Decimal
from typing import Any, Dict, List, Optional
from omniagentpay import OmniAgentPay
from omniagentpay.core.types import Network
from app.core.config import settings
from app.payments.interfaces import AbstractPaymentClient

logger = structlog.get_logger(__name__)

class OmniAgentPaymentClient(AbstractPaymentClient):
    """
    Production-ready wrapper for the OmniAgentPay SDK.
    Ensures singleton access and enforces security guardrails.
    """
    
    _instance: Optional["OmniAgentPaymentClient"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        # SDK client instantiation (exactly once via singleton)
        # Parameter names are circle_api_key and entity_secret
        network = Network.ARC_TESTNET if settings.ENVIRONMENT == "dev" else Network.ETH
        
        self._client = OmniAgentPay(
            circle_api_key=settings.CIRCLE_API_KEY.get_secret_value() if settings.CIRCLE_API_KEY else "",
            entity_secret=settings.ENTITY_SECRET.get_secret_value() if settings.ENTITY_SECRET else "",
            network=network
        )
        logger.info("OmniAgentPay SDK initialized")

    @classmethod
    async def get_instance(cls) -> "OmniAgentPaymentClient":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def create_agent_wallet(self, agent_name: str) -> Dict[str, Any]:
        """Creates a wallet and automatically applies all configured guard policies."""
        logger.info("creating_guarded_wallet", agent=agent_name)
        
        # 1. Create wallet
        wallet = await self._client.create_wallet(name=agent_name)
        wallet_id = wallet.id # Fix: SDK uses .id

        # 2. Attach security guards using SDK methods
        await self._client.add_budget_guard(
            wallet_id=wallet_id,
            daily_limit=settings.OMNIAGENTPAY_DAILY_BUDGET,
            hourly_limit=settings.OMNIAGENTPAY_HOURLY_BUDGET
        )
        await self._client.add_rate_limit_guard(
            wallet_id=wallet_id,
            max_per_minute=settings.OMNIAGENTPAY_RATE_LIMIT_PER_MIN
        )
        await self._client.add_single_tx_guard(
            wallet_id=wallet_id,
            max_amount=settings.OMNIAGENTPAY_TX_LIMIT
        )
        # Only add recipient guard if whitelist is not empty
        # Empty whitelist would block all payments
        if settings.OMNIAGENTPAY_WHITELISTED_RECIPIENTS:
            await self._client.add_recipient_guard(
                wallet_id=wallet_id,
                addresses=settings.OMNIAGENTPAY_WHITELISTED_RECIPIENTS
            )

        return {
            "wallet_id": wallet_id,
            "address": wallet.address,
            "blockchain": wallet.blockchain,
            "status": wallet.state
        }

    async def add_default_guards(self, wallet_id: str) -> Dict[str, Any]:
        """Helper to re-apply default guards if needed."""
        # Attach security guards using SDK methods
        await self._client.add_budget_guard(
            wallet_id=wallet_id,
            daily_limit=settings.OMNIAGENTPAY_DAILY_BUDGET,
            hourly_limit=settings.OMNIAGENTPAY_HOURLY_BUDGET
        )
        await self._client.add_rate_limit_guard(
            wallet_id=wallet_id,
            max_per_minute=settings.OMNIAGENTPAY_RATE_LIMIT_PER_MIN
        )
        await self._client.add_single_tx_guard(
            wallet_id=wallet_id,
            max_amount=settings.OMNIAGENTPAY_TX_LIMIT
        )
        # Only add recipient guard if whitelist is not empty
        if settings.OMNIAGENTPAY_WHITELISTED_RECIPIENTS:
            await self._client.add_recipient_guard(
                wallet_id=wallet_id,
                addresses=settings.OMNIAGENTPAY_WHITELISTED_RECIPIENTS
            )
        return {"status": "guards_applied", "wallet_id": wallet_id}

    async def simulate_payment(
        self, 
        from_wallet_id: str, 
        to_address: str, 
        amount: str, 
        currency: str = "USD"
    ) -> Dict[str, Any]:
        # Ensure wallet exists - router needs it for network detection
        try:
            wallet_info = await self._client.get_wallet(from_wallet_id)
            logger.info("wallet_found", 
                       wallet_id=from_wallet_id, 
                       blockchain=wallet_info.blockchain,
                       address=wallet_info.address)
        except Exception as wallet_err:
            logger.error("wallet_not_found", wallet_id=from_wallet_id, error=str(wallet_err))
            raise Exception(
                f"Wallet not found: {from_wallet_id}. "
                f"Please verify the wallet_id is correct. "
                f"Create a wallet using 'create_agent_wallet' tool if needed."
            ) from wallet_err
        
        result = await self._client.simulate(
            wallet_id=from_wallet_id,
            recipient=to_address,
            amount=amount,
            currency=currency
        )
        # Fix: Use correct attributes for SimulationResult
        return {
            "status": "success",
            "validation_passed": result.would_succeed,
            "estimated_fee": str(result.estimated_fee) if result.estimated_fee else "0",
            "reason": result.reason if not result.would_succeed else None
        }

    async def execute_payment(
        self, 
        from_wallet_id: str, 
        to_address: str, 
        amount: str, 
        currency: str = "USD"
    ) -> Dict[str, Any]:
        result = await self._client.pay(
            wallet_id=from_wallet_id,
            recipient=to_address,
            amount=amount,
            currency=currency
        )
        # Fix: Use correct attributes for PaymentResult
        return {
            "transfer_id": result.transaction_id,
            "status": result.status,
            "tx_hash": result.blockchain_tx,
            "amount": str(result.amount)
        }

    async def create_payment_intent(
        self, 
        wallet_id: str,
        recipient: str,
        amount: str, 
        currency: str = "USD", 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Pre-check balance before creating intent for faster failure and clearer errors
        try:
            balance_info = await self.get_wallet_usdc_balance(wallet_id)
            balance = Decimal(balance_info.get('usdc_balance', '0'))
            amount_decimal = Decimal(str(amount))
            
            if balance < amount_decimal:
                raise Exception(
                    f"Insufficient balance: Wallet has {balance} USDC, but {amount_decimal} USDC is required. "
                    f"Please fund the wallet before creating payment intents."
                )
        except Exception as balance_error:
            # If it's already a balance error, re-raise it
            error_msg = str(balance_error).lower()
            if "insufficient" in error_msg or "no usdc" in error_msg or "balance" in error_msg:
                raise balance_error
            # If balance check itself failed, log but continue (simulation will catch it)
            logger.warning("balance_precheck_failed", error=str(balance_error))
        
        # Extract purpose and exclude it from kwargs to avoid duplicate argument
        purpose = None
        kwargs = {}
        if metadata:
            purpose = metadata.get("purpose")
            kwargs = {k: v for k, v in metadata.items() if k != "purpose"}
        
        try:
            # Verify wallet exists and get its network for better error messages
            try:
                wallet_info = await self._client.wallet.get_wallet(wallet_id)
                logger.debug("wallet_info", wallet_id=wallet_id, blockchain=wallet_info.blockchain if wallet_info else None)
            except Exception as wallet_err:
                logger.warning("wallet_lookup_failed", wallet_id=wallet_id, error=str(wallet_err))
            
            result = await self._client.create_payment_intent(
                wallet_id=wallet_id,
                recipient=recipient,
                amount=amount,
                purpose=purpose,
                **kwargs
            )
            # Fix: Use correct attributes for PaymentIntent
            return {
                "intent_id": result.id,
                "status": result.status,
                "amount": str(result.amount)
            }
        except Exception as e:
            error_msg = str(e)
            logger.error("create_payment_intent_error", 
                        wallet_id=wallet_id, 
                        recipient=recipient[:20] if recipient else None,
                        error=error_msg)
            # Provide helpful message for insufficient balance
            if "no USDC balance" in error_msg.lower() or "balance check failed" in error_msg.lower():
                # Get wallet balance for better error message
                try:
                    balance_info = await self.get_wallet_usdc_balance(wallet_id)
                    balance = balance_info.get('usdc_balance', '0')
                    raise Exception(
                        f"Authorization failed: Wallet has no USDC balance. "
                        f"Current balance: {balance} USDC. "
                        f"Please fund the wallet with USDC before creating payment intents. "
                        f"Use 'check_balance' tool to verify wallet balance."
                    ) from e
                except Exception as nested_e:
                    # If balance check fails, return original error with context
                    if "no USDC balance" not in str(nested_e).lower():
                        raise nested_e
                    raise Exception(
                        f"Authorization failed: Wallet has no USDC balance. "
                        f"Please fund the wallet with USDC before creating payment intents. "
                        f"Use 'check_balance' tool to verify wallet balance."
                    ) from e
            raise

    async def confirm_intent(self, intent_id: str) -> Dict[str, Any]:
        try:
            result = await self._client.confirm_payment_intent(intent_id=intent_id)
            # Return comprehensive payment result
            return {
                "intent_id": intent_id,
                "status": result.status,
                "success": result.success,
                "transaction_id": result.transaction_id,
                "blockchain_tx": result.blockchain_tx,
                "amount": str(result.amount),
                "recipient": result.recipient,
                "message": "Payment executed successfully" if result.success else f"Payment execution failed: {result.error or 'Unknown error'}"
            }
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error messages
            if "no USDC balance" in error_msg.lower() or "balance check failed" in error_msg.lower() or "insufficient balance" in error_msg.lower():
                # Try to get intent details for better error message
                try:
                    intent = await self._client.get_payment_intent(intent_id)
                    if intent:
                        balance_info = await self.get_wallet_usdc_balance(intent.wallet_id)
                        balance = balance_info.get('usdc_balance', '0')
                        raise Exception(
                            f"Payment confirmation failed: Wallet has insufficient USDC balance. "
                            f"Required: {intent.amount} USDC, Current balance: {balance} USDC. "
                            f"Please fund the wallet before confirming the payment intent."
                        ) from e
                except Exception:
                    pass
            
            if "not found" in error_msg.lower():
                raise Exception(f"Payment intent not found: {intent_id}. Please check the intent_id and try again.") from e
            
            if "cannot be confirmed" in error_msg.lower() or "status" in error_msg.lower():
                raise Exception(f"Cannot confirm payment intent: {error_msg}. The intent may have already been confirmed or cancelled.") from e
            
            raise

    async def get_wallet_usdc_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get the actual Circle wallet USDC balance."""
        try:
            balance = await self._client.get_balance(wallet_id)
            return {
                "wallet_id": wallet_id,
                "usdc_balance": str(balance),
                "currency": "USDC"
            }
        except Exception as e:
            # If wallet has no USDC, return 0 instead of error
            error_msg = str(e).lower()
            if "no usdc balance" in error_msg or "has no usdc" in error_msg:
                return {
                    "wallet_id": wallet_id,
                    "usdc_balance": "0",
                    "currency": "USDC",
                    "note": "Wallet has no USDC balance. Funds need to be deposited to the wallet address."
                }
            raise

    async def remove_recipient_guard(self, wallet_id: str) -> Dict[str, Any]:
        """Remove the recipient guard from a wallet to allow payments to any address."""
        try:
            # Remove guard by name "recipient"
            removed = await self._client._guard_manager.remove_guard(wallet_id, "recipient")
            if removed:
                return {"status": "success", "message": "Recipient guard removed. Wallet can now pay to any address."}
            else:
                return {"status": "info", "message": "Recipient guard not found on this wallet."}
        except Exception as e:
            raise Exception(f"Failed to remove recipient guard: {str(e)}") from e

    async def add_recipient_to_whitelist(self, wallet_id: str, addresses: List[str]) -> Dict[str, Any]:
        """Add recipient addresses to the whitelist. Removes and re-adds the guard with updated addresses."""
        try:
            # Get current guards to check if recipient guard exists
            guard_names = await self._client.list_guards(wallet_id)
            
            # Remove existing recipient guard if it exists
            if "recipient" in guard_names:
                await self._client._guard_manager.remove_guard(wallet_id, "recipient")
            
            # Add recipient guard with new addresses
            await self._client.add_recipient_guard(
                wallet_id=wallet_id,
                mode="whitelist",
                addresses=addresses
            )
            
            return {
                "status": "success",
                "message": f"Recipient guard updated. Whitelisted addresses: {addresses}",
                "whitelisted_addresses": addresses
            }
        except Exception as e:
            raise Exception(f"Failed to update recipient whitelist: {str(e)}") from e
