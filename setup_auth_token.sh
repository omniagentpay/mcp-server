#!/bin/bash
# Quick script to generate and configure MCP Auth Token

echo "🔐 FastMCP Authentication Token Setup"
echo "======================================"
echo ""

# Generate secure token
TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "Generated token: $TOKEN"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    touch .env
fi

# Check if MCP_AUTH_TOKEN already exists
if grep -q "MCP_AUTH_TOKEN" .env 2>/dev/null; then
    echo "⚠️  MCP_AUTH_TOKEN already exists in .env"
    CURRENT=$(grep "MCP_AUTH_TOKEN" .env | head -1 | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
    echo "Current token: ${CURRENT:0:20}..."
    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing token."
        exit 0
    fi
    # Remove old token line
    sed -i '/MCP_AUTH_TOKEN=/d' .env
fi

# Add token configuration
echo "📝 Adding token to .env..."
echo "" >> .env
echo "# FastMCP Authentication" >> .env
echo "MCP_AUTH_ENABLED=true" >> .env
echo "MCP_AUTH_TOKEN=$TOKEN" >> .env
echo "MCP_REQUIRE_AUTH=true" >> .env

echo ""
echo "✅ Token configured successfully!"
echo ""
echo "Your bearer token: $TOKEN"
echo ""
echo "Use it in curl commands like this:"
echo "  -H \"Authorization: Bearer $TOKEN\""
echo ""
echo "⚠️  Don't forget to restart your server:"
echo "   uvicorn app.main:app --reload"
echo ""
