from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models here for Alembic autogenerate support
from app.wallets.models import Wallet
from app.ledger.models import LedgerEntry
