#!/bin/bash
# Complete FastMCP Server Test Suite
# Replace YOUR_TOKEN with your actual bearer token

TOKEN="YOUR_TOKEN"  # Replace with your token from .env
BASE_URL="http://localhost:8000/mcp/"

echo "=========================================="
echo "FastMCP Payment Server - Complete Test Suite"
echo "=========================================="
echo ""

# Common headers
HEADERS=(
  -H "Content-Type: application/json"
  -H "Accept: application/json, text/event-stream"
  -H "Authorization: Bearer $TOKEN"
)

# 1. List All Tools
echo "1️⃣  Testing: List All Tools"
echo "----------------------------------------"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }' | jq
echo ""
echo ""

# 2. Create Agent Wallet
echo "2️⃣  Testing: Create Agent Wallet"
echo "----------------------------------------"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {
        "agent_name": "test_agent_001"
      }
    },
    "id": 2
  }' | jq
echo ""
echo ""

# 3. Check Balance (replace WALLET_ID with actual wallet ID from step 2)
echo "3️⃣  Testing: Check Balance"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet ID from step 2"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "check_balance",
      "arguments": {
        "wallet_id": "WALLET_ID"
      }
    },
    "id": 3
  }' | jq
echo ""
echo ""

# 4. Simulate Payment
echo "4️⃣  Testing: Simulate Payment"
echo "----------------------------------------"
echo "⚠️  Replace FROM_WALLET_ID with actual wallet ID"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "simulate_payment",
      "arguments": {
        "from_wallet_id": "FROM_WALLET_ID",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 4
  }' | jq
echo ""
echo ""

# 5. Pay Recipient (requires simulation first)
echo "5️⃣  Testing: Pay Recipient"
echo "----------------------------------------"
echo "⚠️  Replace FROM_WALLET_ID with actual wallet ID"
echo "⚠️  Make sure simulation passed before executing payment"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "pay_recipient",
      "arguments": {
        "from_wallet_id": "FROM_WALLET_ID",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 5
  }' | jq
echo ""
echo ""

# 6. Create Payment Intent
echo "6️⃣  Testing: Create Payment Intent"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet ID"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_payment_intent",
      "arguments": {
        "wallet_id": "WALLET_ID",
        "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "25.00",
        "currency": "USD",
        "metadata": {
          "purpose": "test payment intent",
          "description": "Testing payment intent creation"
        }
      }
    },
    "id": 6
  }' | jq
echo ""
echo ""

# 7. Confirm Payment Intent (replace INTENT_ID with actual intent ID from step 6)
echo "7️⃣  Testing: Confirm Payment Intent"
echo "----------------------------------------"
echo "⚠️  Replace INTENT_ID with actual intent ID from step 6"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "confirm_payment_intent",
      "arguments": {
        "intent_id": "INTENT_ID"
      }
    },
    "id": 7
  }' | jq
echo ""
echo ""

# 8. Remove Recipient Guard
echo "8️⃣  Testing: Remove Recipient Guard"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet ID"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "remove_recipient_guard",
      "arguments": {
        "wallet_id": "WALLET_ID"
      }
    },
    "id": 8
  }' | jq
echo ""
echo ""

# 9. Add Recipient to Whitelist
echo "9️⃣  Testing: Add Recipient to Whitelist"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet ID"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_recipient_to_whitelist",
      "arguments": {
        "wallet_id": "WALLET_ID",
        "addresses": [
          "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
          "0x8ba1f109551bD432803012645Hac136c22C929"
        ]
      }
    },
    "id": 9
  }' | jq
echo ""
echo ""

echo "=========================================="
echo "✅ Test suite completed!"
echo "=========================================="
