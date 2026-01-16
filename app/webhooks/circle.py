import structlog
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.core.config import settings
from app.db.session import get_db
from app.ledger.service import LedgerService
from app.wallets.service import WalletService

router = APIRouter()
logger = structlog.get_logger(__name__)

async def verify_circle_signature(request: Request, signature: str):
    """
    Verifies the Ed25519 signature from Circle.
    In a real implementation, this would use the OmniAgentPay SDK
    to verify the signature against the settings.OMNIAGENTPAY_WEBHOOK_SECRET.
    """
    if settings.ENVIRONMENT == "dev":
        return True # Skip verification in dev if needed
        
    body = await request.body()
    # SDK Simulation:
    # is_valid = omni_sdk.verify_signature(
    #     payload=body, 
    #     signature=signature, 
    #     secret=settings.OMNIAGENTPAY_WEBHOOK_SECRET.get_secret_value()
    # )
    # if not is_valid: raise HTTPException(status_code=401)
    return True

@router.post("/circle")
async def circle_webhook(
    request: Request,
    x_circle_signature: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Circle webhooks for payment events.
    """
    await verify_circle_signature(request, x_circle_signature)
    
    payload = await request.json()
    event_type = payload.get("type")
    logger.info("circle_webhook_received", event_type=event_type, payload=payload)

    ledger_service = LedgerService(db)
    wallet_service = WalletService(db)

    try:
        if event_type == "payment.sent":
            await handle_payment_sent(payload, ledger_service, wallet_service)
        elif event_type == "payment.received":
            await handle_payment_received(payload, ledger_service, wallet_service)
        elif event_type == "transaction.failed":
            await handle_transaction_failed(payload, ledger_service)
        else:
            logger.info("unhandled_event_type", event_type=event_type)

        await db.commit()
        return {"status": "processed"}

    except Exception as e:
        logger.error("webhook_processing_failed", error=str(e), event_type=event_type)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def handle_payment_sent(payload: Dict[str, Any], ledger: LedgerService, wallets: WalletService):
    """Mark a pending payment as completed in the ledger."""
    # Logic to match internal transaction and update status
    logger.info("handling_payment_sent", data=payload)
    # implementation details...

async def handle_payment_received(payload: Dict[str, Any], ledger: LedgerService, wallets: WalletService):
    """Record a new credit to a wallet from an external source."""
    logger.info("handling_payment_received", data=payload)
    # implementation details...

async def handle_transaction_failed(payload: Dict[str, Any], ledger: LedgerService):
    """Mark a ledger entry as failed and potentially trigger alerts."""
    logger.info("handling_transaction_failed", data=payload)
    # implementation details...
