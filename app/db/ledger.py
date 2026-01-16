import uuid
from typing import Any, Dict, Optional
from sqlalchemy import String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class PaymentLedger(Base):
    """
    PostgreSQL schema for a high-integrity, immutable payment ledger.
    Stores all payment attempts: simulated, blocked, and executed.
    """
    __tablename__ = "payment_ledger"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id"), index=True)
    
    # OmniAgentPay References
    omni_ledger_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, doc="Reference to OmniAgentPay ledger ID")
    simulation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, doc="Reference to the required simulation ID")
    
    # Payment Details
    amount: Mapped[float] = mapped_column(Numeric(precision=20, scale=8), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    
    # Type: blocked, simulated, executed
    entry_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # success, failed, blocked
    
    # Audit & Security
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    recipient_address: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Payloads
    request_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, doc="The original MCP tool input")
    response_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, doc="The final response (sanitized for AI)")
    
    # Metadata
    reason: Mapped[Optional[str]] = mapped_column(String(255), doc="Reason for blocking or failure")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self) -> str:
        return f"<PaymentLedger(id={self.id}, type={self.entry_type}, status={self.status}, amount={self.amount})>"
