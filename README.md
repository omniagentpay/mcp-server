# MCP Payment Server

Production-ready FastAPI project for Model Context Protocol (MCP) Server.

## Tech Stack
- Python 3.11
- FastAPI
- PostgreSQL (SQLAlchemy 2.0 Async)
- Alembic
- Pydantic v2
- Structlog

## Project Structure
- `app/main.py`: Entrypoint with lifespan and hardened middleware.
- `app/core`: Configuration (`pydantic-settings`), logging (`structlog`), and security.
- `app/db`: Database session and base models.
- `app/mcp`: 
  - `router.py`: FastAPI `APIRouter` for JSON-RPC 2.0.
  - `registry.py`: Abstract `BaseTool` and dynamic registration.
  - `handlers.py`: Concrete tool implementations (`pay`, `check_balance`, etc.).
- `app/payments`: Business logic, composite `PaymentGuard` system, and `PaymentProvider` adapters.
- `app/wallets`: Transaction-safe balance management with row-level locking.
- `app/ledger`: Immutable, append-only financial audit trail.

## Getting Started
1. **Environment:** Create `.env` from the provided example.
2. **Setup:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Database:**
   ```bash
   export PYTHONPATH=.
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```
4. **Run:**
   ```bash
   uvicorn app.main:app --reload
   ```

## MCP API Reference
All tool calls use a single `APIRouter` endpoint:
- **Endpoint:** `POST /api/v1/mcp/rpc`
- **Method:** JSON-RPC 2.0 compatible.

Example:
```json
{
  "jsonrpc": "2.0",
  "method": "list_tools",
  "id": 1
}
```
