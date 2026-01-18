#!/usr/bin/env python3
"""Startup script for Cloud Run that handles PORT environment variable."""
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Get PORT from environment (Cloud Run sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting OmniAgentPay MCP Server on {host}:{port}")
    print(f"Environment: {os.environ.get('ENVIRONMENT', 'not set')}")
    
    # Start uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info"
    )
