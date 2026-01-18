#!/bin/sh
# Startup script for Cloud Run
# Cloud Run sets PORT environment variable automatically

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
