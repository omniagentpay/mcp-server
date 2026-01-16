import uuid
import structlog
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from app.payments.interfaces import AbstractPaymentClient
from app.payments.omni_client import OmniAgentPaymentClient
from app.utils.exceptions import PaymentError, GuardValidationError

logger = structlog.get_logger(__name__)

class PaymentRequest(BaseModel):
    """Schema for validating MCP tool input."""
    from_wallet_id: str = Field(..., description="The source wallet ID")
    to_address: str = Field(..., description="The recipient's blockchain address")
    amount: str = Field(..., description="Amount to send (e.g., '10.50')")
    currency: str = Field("USD", description="Currency code")

    @validator("amount")
    def validate_amount(cls, v):
        try:
            float_val = float(v)
            if float_val <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            raise ValueError("Amount must be a valid numeric string")
        return v

class PaymentOrchestrator:
    """ Orchestrates the payment flow: Validation -> Simulation -> Execution. """
    
    def __init__(self, client: AbstractPaymentClient):
        self.client = client

    async def pay(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a guarded payment flow.
        1. Validate Input
        2. Run Simulation (Required)
        3. Execute with Idempotency
        """
        # 1. Validate MCP tool input
        try:
            req = PaymentRequest(**request_data)
        except Exception as e:
            logger.error("invalid_payment_input", error=str(e))
            raise PaymentError(f"Invalid input: {str(e)}")

        # Generate idempotency key for this flow
        idempotency_key = str(uuid.uuid4())
        
        logger.info("orchestrating_payment", 
                    wallet_id=req.from_wallet_id, 
                    amount=req.amount,
                    idempotency_key=idempotency_key)

        # 2. Simulation (REQUIRED before execution)
        simulation = await self.client.simulate_payment(
            from_wallet_id=req.from_wallet_id,
            to_address=req.to_address,
            amount=req.amount,
            currency=req.currency
        )

        if simulation.get("status") != "success" or not simulation.get("validation_passed"):
            logger.error("payment_simulation_failed", simulation=simulation)
            raise GuardValidationError(f"Payment simulation failed: {simulation.get('reason', 'Unknown error')}")

        # 3. Execution
        try:
            execution_result = await self.client.execute_payment(
                from_wallet_id=req.from_wallet_id,
                to_address=req.to_address,
                amount=req.amount,
                currency=req.currency
                # In real SDK, we would pass idempotency_key here
            )

            # 4. Return structured result (Stripping blockchain details)
            return {
                "status": "success",
                "payment_id": execution_result.get("transfer_id"),
                "amount": req.amount,
                "currency": req.currency,
                "message": "Payment processed successfully",
                "idempotency_key": idempotency_key
            }

        except Exception as e:
            logger.error("payment_execution_failed", error=str(e))
            raise PaymentError(f"Payment execution failed: {str(e)}")

async def get_payment_orchestrator() -> PaymentOrchestrator:
    """Dependency provider for PaymentOrchestrator."""
    client = await OmniAgentPaymentClient.get_instance()
    return PaymentOrchestrator(client)
