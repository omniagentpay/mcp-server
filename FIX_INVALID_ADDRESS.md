# Fix: Invalid Ethereum Address Format

## Problem

The address `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb` is **invalid** because:
- **Length**: 41 characters
- **Required**: 42 characters (0x + 40 hex characters)
- **Actual hex part**: 39 characters
- **Required hex part**: 40 characters

## Solution

Use a **valid 42-character Ethereum address**. Here are examples:

### Valid Addresses (42 characters each):

```bash
# Example 1: Full 40 hex chars
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0

# Example 2: Another valid address
0x8ba1f109551bD432803012645Hac136c22C929

# Example 3: Test address
0x1234567890123456789012345678901234567890
```

### How to Verify Address Length

```bash
# Quick check
echo "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb" | wc -c
# Should output: 42 (including newline) or 41 (without)

# Python check
python3 << 'EOF'
import re
address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
pattern = re.compile(r"^0x[a-fA-F0-9]{40}$")
print(f"Length: {len(address)}")
print(f"Valid: {pattern.match(address) is not None}")
EOF
```

## Updated Curl Commands

Replace the invalid address in all curl commands:

### Before (Invalid):
```bash
"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

### After (Valid - add one character):
```bash
"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
```

Or use a different valid address:
```bash
"to_address": "0x8ba1f109551bD432803012645Hac136c22C929"
```

## Quick Fix Script

```bash
# Replace invalid address in curl commands
sed -i 's/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0/g' ALL_CURL_COMMANDS_COPY_PASTE.md
```

## Why This Matters

The SDK's `TransferAdapter` uses this regex pattern:
```python
EVM_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
```

This requires:
- `^0x` - Starts with "0x"
- `[a-fA-F0-9]{40}` - Exactly 40 hex characters
- `$` - End of string

Your address has only 39 hex characters, so it doesn't match.

## Test with Valid Address

```bash
# Set token
TOKEN=$(grep MCP_AUTH_TOKEN .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
WALLET_ID="your_wallet_id"

# Use valid 42-character address
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
        \"to_address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0\",
        \"amount\": \"10.50\",
        \"currency\": \"USD\"
      }
    },
    \"id\": 4
  }" | jq
```

## Generate Valid Test Addresses

```bash
# Generate random valid Ethereum address format
python3 << 'EOF'
import secrets
# Generate 40 hex characters
hex_part = secrets.token_hex(20)  # 20 bytes = 40 hex chars
address = f"0x{hex_part}"
print(f"Valid test address: {address}")
print(f"Length: {len(address)} (should be 42)")
EOF
```
