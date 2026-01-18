# Debugging Authentication Issues

## Common Issues

### 1. Token Not Set in Environment

Check if token is configured:

```bash
# Check .env file
cat .env | grep MCP_AUTH_TOKEN

# Or check environment variable
echo $MCP_AUTH_TOKEN
```

### 2. Token Mismatch

The token in your curl command must **exactly match** the token in `.env`:

```bash
# In .env
MCP_AUTH_TOKEN=your_actual_token_here

# In curl (must match exactly)
-H "Authorization: Bearer your_actual_token_here"
```

### 3. Whitespace Issues

Tokens are automatically stripped, but check for:
- Extra spaces
- Newlines
- Quotes in .env file

### 4. Check Server Logs

The server logs will show:
- `token_verification_attempt` - When a token is being verified
- `static_token_verified` - When token matches
- `static_token_mismatch` - When token doesn't match
- `token_verification_failed` - When verification fails

## Quick Test

```bash
# 1. Get your token from .env
TOKEN=$(grep MCP_AUTH_TOKEN .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")

# 2. Test with the token
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | jq
```

## Verify Token Configuration

```bash
python3 << 'EOF'
from app.core.config import settings
if settings.MCP_AUTH_TOKEN:
    token = settings.MCP_AUTH_TOKEN.get_secret_value()
    print(f"Token configured: {token[:10]}... (length: {len(token)})")
else:
    print("Token NOT configured!")
EOF
```

## Disable Auth Temporarily (for testing)

In `.env`:
```bash
MCP_AUTH_ENABLED=false
MCP_REQUIRE_AUTH=false
```

Then restart server and test without Authorization header.
