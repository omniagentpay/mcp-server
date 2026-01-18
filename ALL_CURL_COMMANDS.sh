#!/bin/bash
# Complete FastMCP Server - All Curl Commands
# Run this script or copy individual commands

# ============================================
# SETUP: Extract token from .env
# ============================================
TOKEN=$(grep MCP_AUTH_TOKEN .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
BASE_URL="http://localhost:8000/mcp/"

if [ -z "$TOKEN" ]; then
    echo "❌ Error: MCP_AUTH_TOKEN not found in .env"
    echo "Run: ./setup_auth_token.sh"
    exit 1
fi

echo "✅ Using token: ${TOKEN:0:20}..."
echo ""

# Common headers
HEADERS=(
  -H "Content-Type: application/json"
  -H "Accept: application/json, text/event-stream"
  -H "Authorization: Bearer $TOKEN"
)

# ============================================
# 1. LIST ALL TOOLS
# ============================================
echo "1️⃣  List All Available Tools"
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

# ============================================
# 2. CREATE AGENT WALLET
# ============================================
echo "2️⃣  Create Agent Wallet"
echo "----------------------------------------"
echo "⚠️  Save the wallet_id from the response!"
curl -X POST "$BASE_URL" \
  "${HEADERS[@]}" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {
        "agent_name": "test_agent_'$(date +%s)'"
      }
    },
    "id": 2
  }' | jq
echo ""
echo ""

# ============================================
# 3. CHECK BALANCE
# ============================================
echo "3️⃣  Check Balance"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet_id from step 2"
read -p "Enter wallet_id (or press Enter to skip): " WALLET_ID
if [ -n "$WALLET_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"check_balance\",
          \"arguments\": {
            \"wallet_id\": \"$WALLET_ID\"
          }
        },
        \"id\": 3
      }" | jq
fi
echo ""
echo ""

# ============================================
# 4. SIMULATE PAYMENT
# ============================================
echo "4️⃣  Simulate Payment"
echo "----------------------------------------"
echo "⚠️  Replace FROM_WALLET_ID with actual wallet_id"
read -p "Enter wallet_id (or press Enter to skip): " FROM_WALLET_ID
if [ -n "$FROM_WALLET_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"simulate_payment\",
          \"arguments\": {
            \"from_wallet_id\": \"$FROM_WALLET_ID\",
            \"to_address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
            \"amount\": \"10.50\",
            \"currency\": \"USD\"
          }
        },
        \"id\": 4
      }" | jq
fi
echo ""
echo ""

# ============================================
# 5. PAY RECIPIENT
# ============================================
echo "5️⃣  Pay Recipient"
echo "----------------------------------------"
echo "⚠️  Replace FROM_WALLET_ID with actual wallet_id"
echo "⚠️  Make sure simulation passed before executing payment"
read -p "Enter wallet_id (or press Enter to skip): " PAY_WALLET_ID
if [ -n "$PAY_WALLET_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"pay_recipient\",
          \"arguments\": {
            \"from_wallet_id\": \"$PAY_WALLET_ID\",
            \"to_address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
            \"amount\": \"10.50\",
            \"currency\": \"USD\"
          }
        },
        \"id\": 5
      }" | jq
fi
echo ""
echo ""

# ============================================
# 6. CREATE PAYMENT INTENT
# ============================================
echo "6️⃣  Create Payment Intent"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet_id"
read -p "Enter wallet_id (or press Enter to skip): " INTENT_WALLET_ID
if [ -n "$INTENT_WALLET_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"create_payment_intent\",
          \"arguments\": {
            \"wallet_id\": \"$INTENT_WALLET_ID\",
            \"recipient\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
            \"amount\": \"25.00\",
            \"currency\": \"USD\",
            \"metadata\": {
              \"purpose\": \"test payment intent\",
              \"description\": \"Testing payment intent creation\"
            }
          }
        },
        \"id\": 6
      }" | jq
fi
echo ""
echo ""

# ============================================
# 7. CONFIRM PAYMENT INTENT
# ============================================
echo "7️⃣  Confirm Payment Intent"
echo "----------------------------------------"
echo "⚠️  Replace INTENT_ID with actual intent_id from step 6"
read -p "Enter intent_id (or press Enter to skip): " INTENT_ID
if [ -n "$INTENT_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"confirm_payment_intent\",
          \"arguments\": {
            \"intent_id\": \"$INTENT_ID\"
          }
        },
        \"id\": 7
      }" | jq
fi
echo ""
echo ""

# ============================================
# 8. REMOVE RECIPIENT GUARD
# ============================================
echo "8️⃣  Remove Recipient Guard"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet_id"
read -p "Enter wallet_id (or press Enter to skip): " GUARD_WALLET_ID
if [ -n "$GUARD_WALLET_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"remove_recipient_guard\",
          \"arguments\": {
            \"wallet_id\": \"$GUARD_WALLET_ID\"
          }
        },
        \"id\": 8
      }" | jq
fi
echo ""
echo ""

# ============================================
# 9. ADD RECIPIENT TO WHITELIST
# ============================================
echo "9️⃣  Add Recipient to Whitelist"
echo "----------------------------------------"
echo "⚠️  Replace WALLET_ID with actual wallet_id"
read -p "Enter wallet_id (or press Enter to skip): " WHITELIST_WALLET_ID
if [ -n "$WHITELIST_WALLET_ID" ]; then
    curl -X POST "$BASE_URL" \
      "${HEADERS[@]}" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
          \"name\": \"add_recipient_to_whitelist\",
          \"arguments\": {
            \"wallet_id\": \"$WHITELIST_WALLET_ID\",
            \"addresses\": [
              \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",
              \"0x8ba1f109551bD432803012645Hac136c22C929\"
            ]
          }
        },
        \"id\": 9
      }" | jq
fi
echo ""
echo ""

echo "=========================================="
echo "✅ All commands completed!"
echo "=========================================="
