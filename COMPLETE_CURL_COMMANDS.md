# Complete FastMCP Server - All Curl Commands

**Replace `YOUR_TOKEN` with your actual bearer token**

## Required Headers (All Requests)

```bash
-H "Content-Type: application/json"
-H "Accept: application/json, text/event-stream"  # REQUIRED for FastMCP
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## 1. List All Available Tools

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

---

## 2. Create Agent Wallet

Creates a new wallet with default guardrails.

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {
        "agent_name": "my_agent"
      }
    },
    "id": 2
  }'
```

**Response includes:** `wallet_id`, `address`, `blockchain`, `status`

---

## 3. Check Balance

Get USDC balance for a wallet.

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

**Replace:** `your_wallet_id_here` with actual wallet ID from step 2

---

## 4. Simulate Payment

Validate payment without executing (REQUIRED before payment).

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
        "from_wallet_id": "your_wallet_id",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 4
  }'
```

**Replace:**
- `your_wallet_id` with actual wallet ID
- `to_address` with recipient address
- `amount` with payment amount

---

## 5. Pay Recipient

Execute payment (requires simulation first).

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
        "from_wallet_id": "your_wallet_id",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 5
  }'
```

**⚠️ Important:** Run `simulate_payment` first and ensure it passes before executing payment.

---

## 6. Create Payment Intent

Create a payment intent for later confirmation.

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
        "wallet_id": "your_wallet_id",
        "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "25.00",
        "currency": "USD",
        "metadata": {
          "purpose": "test payment",
          "description": "Optional description"
        }
      }
    },
    "id": 6
  }'
```

**Response includes:** `intent_id` (use in step 7)

---

## 7. Confirm Payment Intent

Confirm and execute a previously created payment intent.

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

**Replace:** `your_intent_id_here` with intent ID from step 6

---

## 8. Remove Recipient Guard

Remove recipient whitelist restrictions (allows payments to any address).

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
        "wallet_id": "your_wallet_id"
      }
    },
    "id": 8
  }'
```

---

## 9. Add Recipient to Whitelist

Add addresses to recipient whitelist for a wallet.

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
        "wallet_id": "your_wallet_id",
        "addresses": [
          "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
          "0x8ba1f109551bD432803012645Hac136c22C929"
        ]
      }
    },
    "id": 9
  }'
```

---

## Complete Payment Flow Example

```bash
# Set your token
export TOKEN="your_token_here"

# 1. Create wallet
WALLET_RESPONSE=$(curl -s -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {"agent_name": "test_agent"}
    },
    "id": 1
  }')

# Extract wallet_id (requires jq)
WALLET_ID=$(echo $WALLET_RESPONSE | jq -r '.result.wallet.wallet_id')
echo "Created wallet: $WALLET_ID"

# 2. Check balance
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"check_balance\",
      \"arguments\": {\"wallet_id\": \"$WALLET_ID\"}
    },
    \"id\": 2
  }" | jq

# 3. Simulate payment
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"simulate_payment\",
      \"arguments\": {
        \"from_wallet_id\": \"$WALLET_ID\",
        \"to_address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
        \"amount\": \"10.50\",
        \"currency\": \"USD\"
      }
    },
    \"id\": 3
  }" | jq
```

---

## Tips

1. **Use jq for pretty output:** Add `| jq` at the end of curl commands
2. **Save responses:** Use variables to store wallet_id, intent_id, etc.
3. **Test flow:** Create wallet → Check balance → Simulate → Pay
4. **Error handling:** Check `error` field in JSON-RPC responses

---

## Quick Copy-Paste Template

```bash
TOKEN="your_token"
WALLET_ID="your_wallet_id"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "TOOL_NAME",
      "arguments": {}
    },
    "id": 1
  }' | jq
```
