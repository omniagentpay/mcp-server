import uuid
from sqlalchemy import String, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Wallet(Base):
    """
    Wallet model representing user accounts.
    Enforces non-negative balance at the database level.
    """
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    
    # Financial data with high precision
    balance: Mapped[float] = mapped_column(
        Numeric(precision=20, scale=8), 
        default=0.0,
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_positive_balance"),
    )
