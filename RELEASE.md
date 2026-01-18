# Release Notes

## Version 0.1.0 - Initial Release

**Release Date:** 2024

### Overview

First production-ready release of OmniAgentPay MCP Server. This FastMCP-based server exposes payment tools via Model Context Protocol (MCP), enabling AI agents to securely manage wallets and execute payments with built-in guardrails.

### Features

#### Core Functionality
- **FastMCP Integration**: Stateless HTTP-based MCP server for horizontal scaling
- **OmniAgentPay SDK**: Full integration with OmniAgentPay payment orchestration
- **Circle Payments**: USDC payment processing via Circle API
- **Guardrails**: Built-in budget limits, rate limiting, and recipient whitelisting

#### Payment Tools
- `create_agent_wallet`: Create managed wallets for AI agents
- `simulate_payment`: Validate payments without moving funds
- `pay_recipient`: Execute payments to blockchain addresses
- `create_payment_intent`: Create payment intents for later confirmation
- `confirm_payment_intent`: Confirm and capture payment intents
- `check_balance`: Query USDC wallet balances

#### Guard Management
- `remove_recipient_guard`: Remove recipient restrictions
- `add_recipient_to_whitelist`: Manage allowed recipient addresses

#### Security
- Bearer token authentication (optional)
- JWT token support
- Stateless design for security
- Input validation via Pydantic schemas
- Global exception handling

#### Observability
- Structured logging with `structlog`
- Correlation ID tracking
- Request/response logging
- Health check endpoint

### Technical Stack

- **Python**: 3.11+
- **FastMCP**: 0.9.0+
- **FastAPI**: 0.109.0+
- **Pydantic**: 2.5.3+
- **OmniAgentPay SDK**: 0.0.1+

### Installation

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Circle API credentials
```

### Configuration

Required environment variables:

```bash
# Payment Configuration
CIRCLE_API_KEY=your_circle_api_key
ENTITY_SECRET=your_entity_secret
ENVIRONMENT=dev  # or "prod"

# Authentication (optional)
MCP_AUTH_ENABLED=true
MCP_AUTH_TOKEN=your_bearer_token
# OR
MCP_JWT_SECRET=your_jwt_secret

# Guard Policies
OMNIAGENTPAY_DAILY_BUDGET=1000.0
OMNIAGENTPAY_HOURLY_BUDGET=200.0
OMNIAGENTPAY_TX_LIMIT=500.0
OMNIAGENTPAY_RATE_LIMIT_PER_MIN=5
OMNIAGENTPAY_WHITELISTED_RECIPIENTS=address1,address2
```

### Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The MCP server will be available at:
- **MCP Endpoint**: `http://localhost:8000/mcp/`
- **Health Check**: `http://localhost:8000/health`
- **Webhooks**: `http://localhost:8000/api/v1/webhooks/circle`

### API Usage

#### List Available Tools

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

#### Execute a Tool

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

### Client Compatibility

This server is compatible with:
- **Claude Desktop** (via HTTP transport)
- **ChatGPT** (via MCP protocol)
- **Gemini** (via MCP protocol)
- **Custom MCP clients**

### Deployment

#### Production Checklist

- [ ] Set `ENVIRONMENT=prod`
- [ ] Configure `CIRCLE_API_KEY` and `ENTITY_SECRET`
- [ ] Enable authentication (`MCP_AUTH_ENABLED=true`)
- [ ] Set secure `MCP_AUTH_TOKEN` or `MCP_JWT_SECRET`
- [ ] Configure HTTPS via reverse proxy
- [ ] Set up structured logging aggregation
- [ ] Configure CORS origins if needed
- [ ] Set appropriate guard policy limits

#### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Breaking Changes

None - this is the initial release.

### Known Issues

- Webhook signature verification requires `OMNIAGENTPAY_WEBHOOK_SECRET` to be configured
- Rate limiting is per-process (not shared across instances)
- Guard policies are applied at the SDK level

### Migration Guide

N/A - initial release.

### Upgrade Instructions

N/A - initial release.

### Support

For issues, questions, or contributions, please refer to the main README.md file.

### Changelog

#### 0.1.0 (Initial Release)
- Initial FastMCP server implementation
- Payment tools integration
- Authentication support
- Guard management tools
- Webhook handlers
- Structured logging
- Health check endpoint
