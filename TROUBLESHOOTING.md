# Troubleshooting Payment Intent Errors

## Error: "No adapter found for recipient"

This error occurs when the OmniAgentPay SDK's PaymentRouter cannot find a suitable adapter for the recipient address.

### Common Causes

1. **Wallet doesn't exist or network mismatch**
   - The wallet must exist and have a blockchain set
   - The recipient address format must match the wallet's blockchain
   - Ethereum wallets (0x...) require EVM-compatible addresses

2. **Address format issues**
   - Ethereum addresses must be exactly 42 characters: `0x` + 40 hex characters
   - Example: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
   - Can be lowercase, uppercase, or checksummed (mixed case)

3. **Network configuration**
   - Wallet's blockchain must match the network configuration
   - Check wallet creation: `create_agent_wallet` should set correct blockchain

### Solutions

#### 1. Verify Wallet Exists

```bash
# First create a wallet
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_agent_wallet",
      "arguments": {"agent_name": "test_agent"}
    },
    "id": 1
  }' | jq
```

#### 2. Use Valid Ethereum Address Format

Ensure the address:
- Starts with `0x`
- Has exactly 40 hex characters after `0x`
- Total length: 42 characters

**Valid examples:**
- `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb` ✅
- `0x742d35cc6634c0532925a3b844bc9e7595f0beb` ✅ (lowercase)
- `0x742D35CC6634C0532925A3B844BC9E7595F0BEB` ✅ (uppercase)

**Invalid examples:**
- `742d35Cc6634C0532925a3b844Bc9e7595f0bEb` ❌ (missing 0x)
- `0x742d35Cc6634C0532925a3b844Bc9e7595f0bE` ❌ (too short, 39 chars)
- `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbb` ❌ (too long, 41 chars)

#### 3. Test with simulate_payment First

Always test with `simulate_payment` before creating intents:

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
        "from_wallet_id": "YOUR_WALLET_ID",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 2
  }' | jq
```

If simulation fails with "No adapter found", the same will happen with `create_payment_intent`.

#### 4. Check Server Logs

The server logs will show:
- Wallet lookup results
- Network detection
- Adapter matching attempts

Look for:
- `wallet_info` - Shows wallet blockchain
- `create_payment_intent_error` - Shows detailed error

### Workflow

1. **Create wallet** → Get `wallet_id`
2. **Check balance** → Verify wallet has funds
3. **Simulate payment** → Test routing/adapter matching
4. **Create intent** → Only if simulation succeeds
5. **Confirm intent** → Execute payment

### Alternative: Use pay_recipient Instead

If `create_payment_intent` continues to fail, try `pay_recipient` which uses the same routing:

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
        "from_wallet_id": "YOUR_WALLET_ID",
        "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "amount": "10.50",
        "currency": "USD"
      }
    },
    "id": 3
  }' | jq
```

This will give you more detailed error messages about what's failing.
