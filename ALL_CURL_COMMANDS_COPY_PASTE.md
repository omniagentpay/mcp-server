# All FastMCP Curl Commands - Copy & Paste Ready

**First, set your token:**
```bash
cd /home/arslan/Documents/hackathon/omni_agent_pay/mcp_server
TOKEN=$(grep MCP_AUTH_TOKEN .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
```

Then use these commands (replace `WALLET_ID` with actual values):

---

## 1. List All Tools

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | jq
```

---

## 2. Create Agent Wallet

```bash
curl -X POST http://localhost:8000/mcp/ \
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
    "id": 2
  }' | jq
```

**Save the `wallet_id` from response!**

---

## 3. Check Balance

```bash
# Replace WALLET_ID with actual wallet_id
WALLET_ID="your_wallet_id_here"

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
    \"id\": 3
  }" | jq
```

---

## 4. Simulate Payment

```bash
# Replace WALLET_ID with actual wallet_id
WALLET_ID="your_wallet_id_here"

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
    \"id\": 4
  }" | jq
```

---

## 5. Pay Recipient

```bash
# Replace WALLET_ID with actual wallet_id
WALLET_ID="your_wallet_id_here"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"pay_recipient\",
      \"arguments\": {
        \"from_wallet_id\": \"$WALLET_ID\",
        \"to_address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
        \"amount\": \"10.50\",
        \"currency\": \"USD\"
      }
    },
    \"id\": 5
  }" | jq
```

---

## 6. Create Payment Intent

```bash
# Replace WALLET_ID with actual wallet_id
WALLET_ID="your_wallet_id_here"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"create_payment_intent\",
      \"arguments\": {
        \"wallet_id\": \"$WALLET_ID\",
        \"recipient\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
        \"amount\": \"25.00\",
        \"currency\": \"USD\",
        \"metadata\": {
          \"purpose\": \"test payment\",
          \"description\": \"Testing payment intent\"
        }
      }
    },
    \"id\": 6
  }" | jq
```

**Save the `intent_id` from response!**

---

## 7. Confirm Payment Intent

```bash
# Replace INTENT_ID with actual intent_id
INTENT_ID="your_intent_id_here"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"confirm_payment_intent\",
      \"arguments\": {\"intent_id\": \"$INTENT_ID\"}
    },
    \"id\": 7
  }" | jq
```

---

## 8. Remove Recipient Guard

```bash
# Replace WALLET_ID with actual wallet_id
WALLET_ID="your_wallet_id_here"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"remove_recipient_guard\",
      \"arguments\": {\"wallet_id\": \"$WALLET_ID\"}
    },
    \"id\": 8
  }" | jq
```

---

## 9. Add Recipient to Whitelist

```bash
# Replace WALLET_ID with actual wallet_id
WALLET_ID="your_wallet_id_here"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"add_recipient_to_whitelist\",
      \"arguments\": {
        \"wallet_id\": \"$WALLET_ID\",
        \"addresses\": [
          \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
          \"0x8ba1f109551bD432803012645Hac136c22C929\"
        ]
      }
    },
    \"id\": 9
  }" | jq
```

---

## Complete Test Flow (Copy All)

```bash
# Setup
cd /home/arslan/Documents/hackathon/omni_agent_pay/mcp_server
TOKEN=$(grep MCP_AUTH_TOKEN .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")

# 1. List tools
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | jq

# 2. Create wallet (save wallet_id)
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
    "id": 2
  }')

WALLET_ID=$(echo $WALLET_RESPONSE | jq -r '.result.structuredContent.intent.wallet_id // .result.structuredContent.wallet.wallet_id // empty')
echo "Wallet ID: $WALLET_ID"

# 3. Check balance
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
    \"id\": 3
  }" | jq

# 4. Simulate payment
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
    \"id\": 4
  }" | jq
```

---

## Quick Reference

**Required Headers (all requests):**
```bash
-H "Content-Type: application/json"
-H "Accept: application/json, text/event-stream"  # REQUIRED!
-H "Authorization: Bearer $TOKEN"
```

**Base URL:**
```bash
http://localhost:8000/mcp/
```

**JSON-RPC Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {...}
  },
  "id": 1
}
```
