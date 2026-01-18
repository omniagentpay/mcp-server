"""FastMCP server implementation for OmniAgentPay SDK."""
from typing import Any, Dict, List, Optional
import structlog
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from app.core.config import settings
from app.mcp.auth import get_auth_provider
from app.payments.omni_client import OmniAgentPaymentClient
from app.payments.service import get_payment_orchestrator
from app.utils.exceptions import PaymentError, GuardValidationError

logger = structlog.get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="OmniAgentPay MCP Server",
    instructions="Production-ready MCP server exposing OmniAgentPay payment tools",
    auth=get_auth_provider() if settings.MCP_REQUIRE_AUTH else None,
)


# Payment Tools (Write Operations)
@mcp.tool()
async def create_agent_wallet(agent_name: str) -> Dict[str, Any]:
    """
    Create a new managed wallet for an AI agent with default guardrails.
    
    Args:
        agent_name: The name of the agent for whom the wallet is created
        
    Returns:
        Dictionary containing wallet_id, address, blockchain, and status
    """
    logger.info("mcp_tool_call", tool="create_agent_wallet", agent_name=agent_name)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.create_agent_wallet(agent_name)
        return {"status": "success", "wallet": result}
    except Exception as e:
        logger.error("create_wallet_tool_failed", error=str(e))
        raise ToolError(f"Failed to create wallet: {str(e)}")


@mcp.tool()
async def simulate_payment(
    from_wallet_id: str,
    to_address: str,
    amount: str,
    currency: str = "USD"
) -> Dict[str, Any]:
    """
    Simulate a payment to validate guardrails and estimate success without moving funds.
    
    Args:
        from_wallet_id: Source wallet ID
        to_address: Recipient blockchain address
        amount: Amount to simulate (numeric string)
        currency: Currency code (default: USD)
        
    Returns:
        Simulation result with validation status and estimated fees
    """
    logger.info("mcp_tool_call", tool="simulate_payment", from_wallet_id=from_wallet_id, amount=amount)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.simulate_payment(
            from_wallet_id=from_wallet_id,
            to_address=to_address,
            amount=amount,
            currency=currency
        )
        return {"status": "success", "simulation": result}
    except GuardValidationError as e:
        logger.warn("simulation_guard_violation", error=str(e))
        raise ToolError(f"Payment simulation blocked by security policy: {str(e)}")
    except Exception as e:
        logger.error("simulate_payment_tool_failed", error=str(e))
        raise ToolError(f"Simulation failed: {str(e)}")


@mcp.tool()
async def pay_recipient(
    from_wallet_id: str,
    to_address: str,
    amount: str,
    currency: str = "USD"
) -> Dict[str, Any]:
    """
    Send a payment to a recipient address. Requires a prior simulation.
    
    This tool executes a guarded payment flow:
    1. Validates input
    2. Runs simulation (required)
    3. Executes payment if simulation passes
    
    Args:
        from_wallet_id: Source wallet ID
        to_address: Recipient blockchain address
        amount: Amount to send (numeric string)
        currency: Currency code (default: USD)
        
    Returns:
        Payment result with transaction ID and status
    """
    logger.info("mcp_tool_call", tool="pay_recipient", from_wallet_id=from_wallet_id, amount=amount)
    try:
        orchestrator = await get_payment_orchestrator()
        result = await orchestrator.pay({
            "from_wallet_id": from_wallet_id,
            "to_address": to_address,
            "amount": amount,
            "currency": currency
        })
        return result
    except GuardValidationError as e:
        logger.warn("payment_guard_violation", error=str(e))
        raise ToolError(f"Payment blocked by security policy: {str(e)}")
    except PaymentError as e:
        logger.error("payment_error", error=str(e))
        raise ToolError(f"Payment processing failed: {str(e)}")
    except Exception as e:
        logger.error("pay_recipient_tool_failed", error=str(e))
        raise ToolError(f"Payment execution failed: {str(e)}")


@mcp.tool()
async def create_payment_intent(
    wallet_id: str,
    recipient: str,
    amount: str,
    currency: str = "USD",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a payment intent for later confirmation.
    
    Args:
        wallet_id: Source wallet ID
        recipient: Recipient address or identifier
        amount: Amount for the intent (numeric string)
        currency: Currency code (default: USD)
        metadata: Optional metadata for the intent (e.g., purpose, description)
        
    Returns:
        Payment intent result with intent_id and status
    """
    logger.info("mcp_tool_call", tool="create_payment_intent", wallet_id=wallet_id, amount=amount)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.create_payment_intent(
            wallet_id=wallet_id,
            recipient=recipient,
            amount=amount,
            currency=currency,
            metadata=metadata
        )
        return {"status": "success", "intent": result}
    except Exception as e:
        logger.error("create_intent_tool_failed", error=str(e))
        raise ToolError(f"Failed to create payment intent: {str(e)}")


@mcp.tool()
async def confirm_payment_intent(intent_id: str) -> Dict[str, Any]:
    """
    Confirm and capture a previously created payment intent.
    
    Args:
        intent_id: The ID of the payment intent to confirm
        
    Returns:
        Confirmation result with transaction details
    """
    logger.info("mcp_tool_call", tool="confirm_payment_intent", intent_id=intent_id)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.confirm_intent(intent_id)
        return {"status": "success", "confirmation": result}
    except Exception as e:
        logger.error("confirm_intent_tool_failed", error=str(e))
        raise ToolError(f"Failed to confirm payment intent: {str(e)}")


# Read-Only Tools
@mcp.tool()
async def check_balance(wallet_id: str) -> Dict[str, Any]:
    """
    Check the current USDC balance of a Circle wallet (the actual balance used for payments).
    
    Args:
        wallet_id: Circle wallet ID to check
        
    Returns:
        Balance information including USDC balance and currency
    """
    logger.info("mcp_tool_call", tool="check_balance", wallet_id=wallet_id)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.get_wallet_usdc_balance(wallet_id)
        return {"status": "success", **result}
    except Exception as e:
        logger.error("check_balance_tool_failed", error=str(e))
        raise ToolError(f"Failed to check balance: {str(e)}")


# Guard Management Tools
@mcp.tool()
async def remove_recipient_guard(wallet_id: str) -> Dict[str, Any]:
    """
    Remove the recipient whitelist guard from a wallet to allow payments to any address.
    
    Args:
        wallet_id: Wallet ID to remove recipient guard from
        
    Returns:
        Status of guard removal operation
    """
    logger.info("mcp_tool_call", tool="remove_recipient_guard", wallet_id=wallet_id)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.remove_recipient_guard(wallet_id)
        return {"status": "success", **result}
    except Exception as e:
        logger.error("remove_recipient_guard_tool_failed", error=str(e))
        raise ToolError(f"Failed to remove recipient guard: {str(e)}")


@mcp.tool()
async def add_recipient_to_whitelist(
    wallet_id: str,
    addresses: List[str]
) -> Dict[str, Any]:
    """
    Add recipient addresses to the whitelist for a wallet.
    
    Args:
        wallet_id: Wallet ID
        addresses: List of recipient addresses to whitelist
        
    Returns:
        Status of whitelist update operation
    """
    logger.info("mcp_tool_call", tool="add_recipient_to_whitelist", wallet_id=wallet_id, addresses=addresses)
    try:
        client = await OmniAgentPaymentClient.get_instance()
        result = await client.add_recipient_to_whitelist(wallet_id, addresses)
        return {"status": "success", **result}
    except Exception as e:
        logger.error("add_recipient_to_whitelist_tool_failed", error=str(e))
        raise ToolError(f"Failed to update recipient whitelist: {str(e)}")
