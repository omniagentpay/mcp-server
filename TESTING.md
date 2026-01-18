# Testing the FastMCP Server

## Quick Start

### 1. Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at:
- **MCP Endpoint**: `http://localhost:8000/mcp/`
- **Health Check**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs` (FastAPI Swagger UI)

### 2. Configure Authentication (Optional)

If authentication is enabled, set your token:

```bash
export MCP_AUTH_TOKEN="your_bearer_token_here"
```

Or add to `.env`:
```bash
MCP_AUTH_ENABLED=true
MCP_AUTH_TOKEN=your_bearer_token_here
```

## Testing Methods

### Method 1: Using the Test Script

Run the automated test script:

```bash
# Without auth
python test_fastmcp.py

# With auth token
MCP_AUTH_TOKEN=your_token python test_fastmcp.py
```

### Method 2: Using curl

#### List Available Tools

```bash
# Without auth
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# With auth
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

#### Call a Tool (check_balance)

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "check_balance",
      "arguments": {
        "wallet_id": "your_wallet_id"
      }
    },
    "id": 2
  }'
```

#### Create Agent Wallet

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {
        "agent_name": "test_agent"
      }
    },
    "id": 3
  }'
```

#### Simulate Payment

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "simulate_payment",
      "arguments": {
        "from_wallet_id": "wallet_123",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 4
  }'
```

### Method 3: Using Python httpx

```python
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            },
            headers={"Authorization": "Bearer your_token"}  # if auth enabled
        )
        print(response.json())

asyncio.run(test())
```

### Method 4: Using MCP Client Libraries

#### Claude Desktop / ChatGPT

Configure MCP server in your client settings:

```json
{
  "mcpServers": {
    "omniagentpay": {
      "url": "http://localhost:8000/mcp/",
      "auth": {
        "type": "bearer",
        "token": "your_token"
      }
    }
  }
}
```

## Available Tools

1. **create_agent_wallet** - Create wallet with guardrails
2. **check_balance** - Get USDC balance
3. **simulate_payment** - Validate payment without execution
4. **pay_recipient** - Execute payment (requires simulation first)
5. **create_payment_intent** - Create payment intent
6. **confirm_payment_intent** - Confirm payment intent
7. **remove_recipient_guard** - Remove recipient restrictions
8. **add_recipient_to_whitelist** - Update recipient whitelist

## Testing Workflow

### 1. Basic Connectivity Test

```bash
# Health check
curl http://localhost:8000/health

# List tools
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### 2. Authentication Test

```bash
# Should fail without token (if auth enabled)
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Should succeed with token
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### 3. Payment Flow Test

```bash
# 1. Create wallet
# 2. Check balance
# 3. Simulate payment
# 4. Execute payment (if simulation passes)
```

## Troubleshooting

### Server won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check logs for import errors

### Authentication errors
- Verify `MCP_AUTH_TOKEN` is set correctly
- Check `MCP_AUTH_ENABLED` setting in config
- Ensure token matches what's configured

### Tool execution errors
- Check OmniAgentPay SDK is properly configured
- Verify Circle API keys are set
- Check wallet IDs are valid
- Review server logs for detailed error messages

## Expected Responses

### Success Response
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "wallet": {
      "wallet_id": "...",
      "address": "...",
      "blockchain": "..."
    }
  },
  "id": 1
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Tool execution failed",
    "data": {
      "detail": "Error details here"
    }
  },
  "id": 1
}
```
