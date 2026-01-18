# FastMCP Server - Curl Commands (With Authentication)

Replace `YOUR_TOKEN` with your actual bearer token from `.env` or environment variable.

## Setup

```bash
# Set your token (or use the value from .env)
export TOKEN="your_actual_token_here"
```

## 1. List All Available Tools

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

## 2. Create Agent Wallet

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {
        "agent_name": "test_agent"
      }
    },
    "id": 2
  }'
```

## 3. Check Balance

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "check_balance",
      "arguments": {
        "wallet_id": "your_wallet_id_here"
      }
    },
    "id": 3
  }'
```

## 4. Simulate Payment

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
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

## 5. Pay Recipient

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "pay_recipient",
      "arguments": {
        "from_wallet_id": "wallet_123",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 5
  }'
```

## 6. Create Payment Intent

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_payment_intent",
      "arguments": {
        "wallet_id": "wallet_123",
        "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD",
        "metadata": {
          "purpose": "test payment"
        }
      }
    },
    "id": 6
  }'
```

## 7. Confirm Payment Intent

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "confirm_payment_intent",
      "arguments": {
        "intent_id": "your_intent_id_here"
      }
    },
    "id": 7
  }'
```

## 8. Remove Recipient Guard

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "remove_recipient_guard",
      "arguments": {
        "wallet_id": "wallet_123"
      }
    },
    "id": 8
  }'
```

## 9. Add Recipient to Whitelist

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_recipient_to_whitelist",
      "arguments": {
        "wallet_id": "wallet_123",
        "addresses": [
          "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
          "0x8ba1f109551bD432803012645Hac136c22C929"
        ]
      }
    },
    "id": 9
  }'
```

## Quick Test Script

Save this as `test.sh` and make it executable:

```bash
#!/bin/bash
TOKEN="YOUR_TOKEN"  # Replace with your token

# List tools
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | jq
```

## Using Environment Variable

```bash
# Set token
export TOKEN="your_token_here"

# Use in curl
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

## Pretty Print JSON Responses

Add `| jq` to pretty print responses:

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | jq
```

## Common Errors

### 401 Unauthorized
- Check that `Authorization: Bearer YOUR_TOKEN` header is included
- Verify token matches `MCP_AUTH_TOKEN` in `.env`
- Ensure `MCP_AUTH_ENABLED=true` in config

### 404 Not Found
- Verify server is running: `curl http://localhost:8000/health`
- Check endpoint path is `/mcp/` (with trailing slash)

### Invalid JSON-RPC
- Ensure `jsonrpc: "2.0"` is included
- Check `method` and `params` structure matches examples above

### 406 Not Acceptable
- **Required**: Add `Accept: application/json, text/event-stream` header
- FastMCP's streamable HTTP transport requires both content types in Accept header
- Example: `-H "Accept: application/json, text/event-stream"`
