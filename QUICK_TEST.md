# Quick Test Command

## Required Headers

FastMCP requires these headers for all requests:

```bash
-H "Content-Type: application/json"
-H "Accept: application/json, text/event-stream"  # REQUIRED!
-H "Authorization: Bearer YOUR_TOKEN"  # If auth enabled
```

## Test List Tools

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

## Common Error: 406 Not Acceptable

If you get `406 Not Acceptable`, you're missing the `Accept` header:

```bash
# ❌ Wrong - Missing Accept header
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# ✅ Correct - Includes Accept header
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```
