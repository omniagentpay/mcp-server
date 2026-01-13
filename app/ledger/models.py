import uuid
from typing import Any, Dict, Optional
from sqlalchemy import String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class LedgerEntry(Base):
    """
    Immutable ledger for all financial transactions.
    Follows append-only design for audit and compliance.
    """
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id"), index=True)
    
    # Financial data
    amount: Mapped[float] = mapped_column(Numeric(precision=20, scale=8))
    entry_type: Mapped[str] = mapped_column(String(50))  # debit, credit
    
    # Transaction context
    status: Mapped[str] = mapped_column(String(50), index=True)  # pending, completed, failed
    provider: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Audit payloads
    intent: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Original request
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Provider response
    
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Note: No updated_at field because ledger entries are immutable.
    # Corrections should be new entries that reference the old one.
