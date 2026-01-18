#!/usr/bin/env python3
"""Test script for FastMCP server."""
import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
MCP_PATH = "/mcp/"


async def test_mcp_request(method: str, params: Dict[str, Any] = None, auth_token: str = None) -> Dict[str, Any]:
    """Make an MCP JSON-RPC request."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"  # Required by FastMCP streamable HTTP
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    if params:
        payload["params"] = params
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{MCP_PATH}",
            json=payload,
            headers=headers,
            timeout=30.0
        )
        return response.json()


async def test_list_tools(auth_token: str = None):
    """Test listing available tools."""
    print("\n=== Testing: List Tools ===")
    result = await test_mcp_request("tools/list", auth_token=auth_token)
    print(json.dumps(result, indent=2))
    return result


async def test_check_balance(wallet_id: str, auth_token: str = None):
    """Test check_balance tool."""
    print(f"\n=== Testing: check_balance (wallet_id={wallet_id}) ===")
    result = await test_mcp_request(
        "tools/call",
        params={
            "name": "check_balance",
            "arguments": {"wallet_id": wallet_id}
        },
        auth_token=auth_token
    )
    print(json.dumps(result, indent=2))
    return result


async def test_create_wallet(agent_name: str, auth_token: str = None):
    """Test create_agent_wallet tool."""
    print(f"\n=== Testing: create_agent_wallet (agent_name={agent_name}) ===")
    result = await test_mcp_request(
        "tools/call",
        params={
            "name": "create_agent_wallet",
            "arguments": {"agent_name": agent_name}
        },
        auth_token=auth_token
    )
    print(json.dumps(result, indent=2))
    return result


async def test_simulate_payment(from_wallet_id: str, to_address: str, amount: str, auth_token: str = None):
    """Test simulate_payment tool."""
    print(f"\n=== Testing: simulate_payment ===")
    print(f"  From: {from_wallet_id}")
    print(f"  To: {to_address}")
    print(f"  Amount: {amount}")
    result = await test_mcp_request(
        "tools/call",
        params={
            "name": "simulate_payment",
            "arguments": {
                "from_wallet_id": from_wallet_id,
                "to_address": to_address,
                "amount": amount,
                "currency": "USD"
            }
        },
        auth_token=auth_token
    )
    print(json.dumps(result, indent=2))
    return result


async def main():
    """Run all tests."""
    print("FastMCP Server Test Suite")
    print("=" * 50)
    
    # Get auth token from environment or use None
    import os
    auth_token = os.getenv("MCP_AUTH_TOKEN")
    
    if auth_token:
        print(f"Using auth token: {auth_token[:10]}...")
    else:
        print("No auth token provided (set MCP_AUTH_TOKEN env var)")
    
    try:
        # Test 1: List tools
        tools_result = await test_list_tools(auth_token=auth_token)
        
        if "error" in tools_result:
            print(f"\n❌ Error listing tools: {tools_result['error']}")
            return
        
        tools = tools_result.get("result", [])
        print(f"\n✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.get('name', 'unknown')}")
        
        # Test 2: Create wallet (if you have test credentials)
        # Uncomment to test:
        # wallet_result = await test_create_wallet("test_agent", auth_token=auth_token)
        # if "result" in wallet_result:
        #     wallet_id = wallet_result["result"].get("wallet", {}).get("wallet_id")
        #     if wallet_id:
        #         # Test 3: Check balance
        #         await test_check_balance(wallet_id, auth_token=auth_token)
        
        print("\n✅ Basic tests completed!")
        print("\nTo test payment tools, uncomment the wallet creation test above.")
        
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to server.")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("   Start it with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
