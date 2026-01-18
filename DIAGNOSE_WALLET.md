# Diagnosing "No Adapter Found" Error

## Root Cause

The error "No adapter found for recipient" occurs when the SDK's PaymentRouter cannot determine which adapter to use. This happens when:

1. **Wallet doesn't exist** - The router tries to get the wallet to determine its network, but if the wallet doesn't exist, it can't route properly
2. **Network detection fails** - The wallet's blockchain string can't be converted to a Network enum
3. **Address format mismatch** - The recipient address format doesn't match the wallet's network

## Quick Diagnosis

### Step 1: Verify Wallet Exists

```bash
# Try to get wallet info (this will fail if wallet doesn't exist)
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "check_balance",
      "arguments": {"wallet_id": "YOUR_WALLET_ID"}
    },
    "id": 1
  }' | jq
```

If this fails with "Wallet not found", the wallet_id is invalid.

### Step 2: Create a Fresh Wallet

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
      "arguments": {"agent_name": "test_agent_$(date +%s)"}
    },
    "id": 2
  }' | jq
```

**Save the `wallet_id` from the response!**

### Step 3: Test with Fresh Wallet

Use the wallet_id from step 2:

```bash
WALLET_ID="wallet_id_from_step_2"

curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
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

## Common Issues

### Issue 1: Wallet Created Outside SDK

If you created the wallet using Circle's API directly or another tool, the SDK's wallet service might not be able to retrieve it properly. **Solution**: Always create wallets using `create_agent_wallet` tool.

### Issue 2: Wrong Wallet ID Format

Wallet IDs from Circle API should be UUIDs. Verify the format matches what `create_agent_wallet` returns.

### Issue 3: Network Mismatch

If your wallet is on ARC_TESTNET but you're trying to pay to an Ethereum mainnet address, routing will fail. **Solution**: Ensure wallet and recipient are on compatible networks.

## Expected Behavior

After creating a wallet with `create_agent_wallet`:
1. Wallet should be stored in SDK's wallet service
2. Router should be able to retrieve wallet and detect network
3. TransferAdapter should recognize EVM addresses (0x...)
4. Simulation should succeed (if balance/guards allow)

## Still Failing?

Check server logs for:
- `wallet_found` - Confirms wallet was retrieved
- `wallet_not_found` - Wallet lookup failed
- `wallet_network` - Shows detected blockchain

If wallet exists but still fails, the issue is likely in the SDK's adapter matching logic. Check:
1. SDK version compatibility
2. Network configuration matches wallet's blockchain
3. Address format is exactly 42 characters (0x + 40 hex)
