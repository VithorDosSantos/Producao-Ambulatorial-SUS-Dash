#!/bin/bash
echo "=== Railway Start Script ==="
echo "PORT environment variable: ${PORT}"
echo "Starting uvicorn on 0.0.0.0:${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

