from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.ledger.models import LedgerEntry
import uuid

class LedgerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_transaction(
        self, 
        wallet_id: uuid.UUID, 
        amount: float, 
        entry_type: str, 
        description: str,
        status: str = "pending",
        provider: Optional[str] = None,
        intent: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> LedgerEntry:
        """
        Create a new immutable ledger entry.
        """
        entry = LedgerEntry(
            wallet_id=wallet_id,
            amount=amount,
            entry_type=entry_type,
            description=description,
            status=status,
            provider=provider,
            intent=intent,
            result=result
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_entry(self, entry_id: uuid.UUID) -> Optional[LedgerEntry]:
        result = await self.db.execute(select(LedgerEntry).where(LedgerEntry.id == entry_id))
        return result.scalar_one_or_none()

    async def get_wallet_history(
        self, 
        wallet_id: uuid.UUID, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[LedgerEntry]:
        """
        Retrieve transaction history for a wallet, ordered by creation time.
        """
        query = (
            select(LedgerEntry)
            .where(LedgerEntry.wallet_id == wallet_id)
            .order_by(LedgerEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # No update or delete methods exist to preserve immutability.
