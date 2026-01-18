# OmniAgentPay MCP Server

Production-ready FastMCP server exposing OmniAgentPay payment tools via Model Context Protocol (MCP).

**Version:** 0.1.0 | [Release Notes](RELEASE.md) | [Testing Guide](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

## Tech Stack
- Python 3.11+
- FastMCP (MCP protocol implementation)
- FastAPI (web framework)
- Pydantic v2
- Structlog
- OmniAgentPay SDK

## Project Structure
- `app/main.py`: FastAPI entrypoint with FastMCP server mounted
- `app/core`: Configuration (`pydantic-settings`), logging (`structlog`), and security
- `app/mcp`: 
  - `fastmcp_server.py`: FastMCP server with all payment tools
  - `auth.py`: Bearer token and JWT authentication provider
- `app/payments`: OmniAgentPay SDK integration and payment orchestration
- `app/webhooks`: Webhook handlers for Circle payment events

## Getting Started

### 1. Environment Setup
Create a `.env` file with required configuration:
```bash
# Payment Configuration
CIRCLE_API_KEY=your_circle_api_key
ENTITY_SECRET=your_entity_secret
ENVIRONMENT=dev  # or "prod"

# FastMCP Authentication (optional but recommended)
MCP_AUTH_ENABLED=true
MCP_AUTH_TOKEN=your_static_bearer_token  # For simple API clients
# OR
MCP_JWT_SECRET=your_jwt_secret  # For JWT-based auth

# Guard Policies
OMNIAGENTPAY_DAILY_BUDGET=1000.0
OMNIAGENTPAY_HOURLY_BUDGET=200.0
OMNIAGENTPAY_TX_LIMIT=500.0
OMNIAGENTPAY_RATE_LIMIT_PER_MIN=5
OMNIAGENTPAY_WHITELISTED_RECIPIENTS=address1,address2
```

### 2. Installation
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## MCP API Reference

### Endpoint
- **Base URL:** `http://localhost:8000/mcp/`
- **Protocol:** MCP over HTTP (stateless)

### Authentication
If `MCP_AUTH_ENABLED=true`, include Bearer token in requests:
```bash
Authorization: Bearer <your_token>
```

### Available Tools

#### Payment Operations
- `create_agent_wallet(agent_name: str)` - Create wallet with guardrails
- `simulate_payment(from_wallet_id, to_address, amount, currency)` - Validate payment
- `pay_recipient(from_wallet_id, to_address, amount, currency)` - Execute payment
- `create_payment_intent(wallet_id, recipient, amount, currency, metadata)` - Create intent
- `confirm_payment_intent(intent_id)` - Confirm intent

#### Read-Only Operations
- `check_balance(wallet_id)` - Get USDC balance

#### Guard Management
- `remove_recipient_guard(wallet_id)` - Remove recipient restrictions
- `add_recipient_to_whitelist(wallet_id, addresses)` - Update whitelist

### Example Usage

#### List Tools
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

#### Check Balance
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
        "wallet_id": "wallet_123"
      }
    },
    "id": 2
  }'
```

## Client Compatibility

This server is compatible with all MCP clients:
- **Claude Desktop** (via HTTP transport)
- **ChatGPT** (via MCP protocol)
- **Gemini** (via MCP protocol)
- **Custom MCP clients**

## Deployment

### Production Considerations
1. **Stateless HTTP**: Already configured for horizontal scaling
2. **Authentication**: Enable `MCP_AUTH_ENABLED=true` and set secure tokens
3. **HTTPS**: Use reverse proxy (nginx/traefik) with TLS
4. **Environment Variables**: Store secrets securely (AWS Secrets Manager, etc.)
5. **Monitoring**: Add structured logging and metrics

### Docker Example
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security

- All payment operations are protected by OmniAgentPay SDK guardrails
- Authentication required for all tools (if enabled)
- Bearer token or JWT verification supported
- Stateless design prevents session-based attacks
- Input validation via Pydantic schemas

## Documentation

- **[RELEASE.md](RELEASE.md)**: Release notes, version history, and upgrade instructions
- **[TESTING.md](TESTING.md)**: Testing guide and examples
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues and solutions
- **[SETUP_AUTH.md](SETUP_AUTH.md)**: Authentication setup guide

## License

See [LICENSE](LICENSE) file for details.
