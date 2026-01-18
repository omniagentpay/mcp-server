# Migration to FastMCP

This document describes the migration from custom MCP implementation to FastMCP.

## What Changed

### New FastMCP Implementation
- **`app/mcp/fastmcp_server.py`**: FastMCP server with all payment tools as `@mcp.tool` decorated functions
- **`app/mcp/auth.py`**: Bearer token and JWT authentication provider for FastMCP
- **`app/main.py`**: Updated to mount FastMCP HTTP app at `/mcp/` endpoint

### Configuration Updates
- Added FastMCP authentication settings to `app/core/config.py`:
  - `MCP_AUTH_ENABLED`: Enable/disable authentication
  - `MCP_AUTH_TOKEN`: Static Bearer token for API clients
  - `MCP_JWT_SECRET`: JWT secret for token verification
  - `MCP_REQUIRE_AUTH`: Require auth for all tools

### Dependencies
- Added `fastmcp>=0.9.0` to `requirements.txt` and `pyproject.toml`

## Legacy Files (Kept for Reference)
The following files are no longer used but kept for reference:
- `app/mcp/router.py`: Old custom MCP router
- `app/mcp/registry.py`: Old tool registry system
- `app/mcp/tools.py`: Old tool implementations (now in `fastmcp_server.py`)
- `app/mcp/schemas.py`: Old MCP request/response schemas

## Key Differences

### Old Implementation
- Custom JSON-RPC 2.0 router
- Manual tool registry system
- Custom error handling
- Endpoint: `/api/v1/mcp/rpc`

### New FastMCP Implementation
- Standard FastMCP server
- Native `@mcp.tool` decorators
- Built-in MCP protocol handling
- Endpoint: `/mcp/`
- Stateless HTTP for horizontal scaling
- Standard MCP authentication

## Benefits

1. **Standard Protocol**: Uses official FastMCP library, ensuring compatibility
2. **Better Auth**: Built-in authentication providers (Bearer, JWT, OAuth)
3. **Stateless**: Supports horizontal scaling out of the box
4. **Less Code**: No need to maintain custom MCP protocol implementation
5. **Client Compatibility**: Works with all MCP clients (Claude, ChatGPT, Gemini)

## Migration Checklist

- [x] Add FastMCP dependency
- [x] Create FastMCP server with tools
- [x] Implement authentication provider
- [x] Update main.py to mount FastMCP app
- [x] Update configuration with auth settings
- [x] Update README with new API documentation
- [ ] Update tests to use FastMCP (optional)
- [ ] Remove legacy files (optional, after verification)

## Testing

To test the new implementation:

```bash
# Start server
uvicorn app.main:app --reload

# Test tool listing (if auth disabled)
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Test with auth (if enabled)
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

## Environment Variables

Add to `.env`:
```bash
# FastMCP Authentication
MCP_AUTH_ENABLED=true
MCP_AUTH_TOKEN=your_static_bearer_token
# OR for JWT
MCP_JWT_SECRET=your_jwt_secret
MCP_REQUIRE_AUTH=true
```
