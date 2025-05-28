#!/bin/sh
set -e

# Apply Alembic database migrations automatically
echo "Applying database migrations..."
if alembic upgrade head; then
    echo "Database migrations applied successfully."
else
    echo "ERROR: Database migrations failed. Please check the output above for details. Exiting."
    exit 1
fi

# Start FastAPI server
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload 