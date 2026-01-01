#!/bin/bash
set -e

echo "=== Habit Tracker API Startup ==="

# Check if required environment variables are set
if [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
  echo "ERROR: Required database environment variables are not set"
  echo "POSTGRES_HOST: ${POSTGRES_HOST:-NOT SET}"
  echo "POSTGRES_USER: ${POSTGRES_USER:-NOT SET}"
  echo "POSTGRES_DB: ${POSTGRES_DB:-NOT SET}"
  exit 1
fi

echo "Waiting for database to be ready..."
echo "Connecting to: ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}/${POSTGRES_DB} as ${POSTGRES_USER}"

# Wait for postgres to be ready (max 60 seconds)
MAX_WAIT=60
WAIT_COUNT=0
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q' 2>/dev/null; do
  WAIT_COUNT=$((WAIT_COUNT + 1))
  if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo "ERROR: PostgreSQL is still unavailable after ${MAX_WAIT} seconds"
    exit 1
  fi
  >&2 echo "PostgreSQL is unavailable - sleeping (${WAIT_COUNT}/${MAX_WAIT})"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"

# Run database migrations
echo "Running database migrations..."
if ! alembic upgrade head; then
  echo "ERROR: Database migrations failed"
  exit 1
fi

echo "Migrations completed successfully!"

# Start the application
echo "Starting application..."
exec "$@"

