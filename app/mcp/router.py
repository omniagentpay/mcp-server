from fastapi import APIRouter, Depends, Request
from app.mcp.schemas import MCPRequest, MCPResponse
from app.mcp.registry import registry
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/rpc", response_model=MCPResponse)
async def mcp_rpc_endpoint(request: MCPRequest):
    logger.info("mcp_request", method=request.method, id=request.id)
    
    try:
        if request.method == "list_tools":
            result = [t.model_dump() for t in registry.get_definitions()]
        else:
            result = await registry.call(request.method, request.params or {})
        
        return MCPResponse(result=result, id=request.id)
    except Exception as e:
        logger.error("mcp_error", error=str(e), method=request.method, id=request.id)
        return MCPResponse(
            error={"code": -32603, "message": str(e)},
            id=request.id
        )

