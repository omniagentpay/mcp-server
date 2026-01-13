from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.wallets.models import Wallet
from app.utils.exceptions import PaymentError
import uuid
import structlog

logger = structlog.get_logger(__name__)

class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_wallet(self, wallet_id: uuid.UUID) -> Optional[Wallet]:
        """Simple read for balance checks."""
        result = await self.db.execute(select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()

    async def get_wallet_for_update(self, wallet_id: uuid.UUID) -> Optional[Wallet]:
        """
        Retrieves wallet with a row-level lock (SELECT FOR UPDATE).
        Ensures thread-safe/transaction-safe balance updates.
        """
        query = (
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_wallet(self, user_id: str, currency: str = "USD") -> Wallet:
        wallet = Wallet(user_id=user_id, currency=currency)
        self.db.add(wallet)
        await self.db.flush() # Flush to get ID, but don't commit here
        return wallet

    async def update_balance(self, wallet_id: uuid.UUID, amount_delta: float):
        """
        Atomic balance update. 
        Note: This is intended to be called within a transaction 
        that also creates a ledger entry.
        """
        # We use a row-level lock check before updating
        wallet = await self.get_wallet_for_update(wallet_id)
        if not wallet:
            raise PaymentError(f"Wallet {wallet_id} not found for balance update")

        new_balance = float(wallet.balance) + amount_delta
        if new_balance < 0:
            raise PaymentError(f"Insufficient funds in wallet {wallet_id}")

        wallet.balance = new_balance
        # No commit here - caller manages the transaction
        logger.info("balance_updated", wallet_id=str(wallet_id), delta=amount_delta, new_balance=new_balance)
