from abc import ABC, abstractmethod
from typing import Set, Optional
import structlog
from app.utils.exceptions import (
    BudgetExceededError, 
    UnauthorizedRecipientError, 
    RateLimitExceededError
)

logger = structlog.get_logger(__name__)

class PaymentGuard(ABC):
    @abstractmethod
    async def validate(self, amount: float, wallet_id: str, recipient: Optional[str] = None):
        """
        Validate if a payment can proceed.
        Raises specialized GuardValidationError if checks fail.
        """
        pass

class BudgetGuard(PaymentGuard):
    def __init__(self, per_transaction_limit: float, daily_limit: float):
        self.per_transaction_limit = per_transaction_limit
        self.daily_limit = daily_limit

    async def validate(self, amount: float, wallet_id: str, recipient: Optional[str] = None):
        # 1. Per-transaction check
        if amount > self.per_transaction_limit:
            logger.warn("guard_violation", guard="BudgetGuard", reason="per_transaction_limit", amount=amount)
            raise BudgetExceededError(f"Amount {amount} exceeds per-transaction limit of {self.per_transaction_limit}")
        
        # 2. Daily limit check (Logic placeholder for ledger/DB query)
        # current_daily_total = await get_daily_total(wallet_id)
        # if current_daily_total + amount > self.daily_limit:
        #     raise BudgetExceededError("Daily spending limit reached")
        
        logger.info("guard_passed", guard="BudgetGuard", amount=amount)

class AllowlistGuard(PaymentGuard):
    def __init__(self, approved_recipients: Set[str]):
        self.approved_recipients = approved_recipients

    async def validate(self, amount: float, wallet_id: str, recipient: Optional[str] = None):
        if not recipient or recipient not in self.approved_recipients:
            logger.warn("guard_violation", guard="AllowlistGuard", recipient=recipient)
            raise UnauthorizedRecipientError(recipient or "Unknown")
        
        logger.info("guard_passed", guard="AllowlistGuard", recipient=recipient)

class RateLimitGuard(PaymentGuard):
    def __init__(self, max_requests_per_minute: int):
        self.max_requests_per_minute = max_requests_per_minute
        # Placeholder for state tracking (e.g. Redis or local cache)

    async def validate(self, amount: float, wallet_id: str, recipient: Optional[str] = None):
        # Implementation of rate limiting logic
        # if too_many_requests:
        #     raise RateLimitExceededError()
        logger.info("guard_passed", guard="RateLimitGuard")
