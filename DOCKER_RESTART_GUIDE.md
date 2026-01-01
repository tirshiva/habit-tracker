# Docker Container Restart Guide

## ✅ Good News: Everything is Automatic!

Your Docker setup is configured to handle database connections and migrations **automatically**. You can simply run `docker-compose up` without worrying about manual steps.

## How It Works

### 1. **Database Connection** ✅ Automatic
- Docker Compose uses `depends_on` with health checks
- The API container waits for PostgreSQL and Redis to be healthy before starting
- Connection strings are automatically configured via environment variables
- **You don't need to do anything manually**

### 2. **Database Migrations** ✅ Automatic
- The `entrypoint.sh` script runs automatically when the API container starts
- It waits for the database to be ready (up to 60 seconds)
- Then automatically runs `alembic upgrade head` to apply migrations
- **You don't need to run migrations manually**

### 3. **Data Persistence** ✅ Automatic
- Database data is stored in Docker volumes (`postgres_data`, `redis_data`)
- Data persists across container restarts
- **Your data is safe when restarting**

## Simple Restart Commands

### Just Restart (No Code Changes)
```bash
docker-compose restart
```
This keeps everything running and just restarts the containers. Database connections are maintained.

### Restart After Code Changes
```bash
docker-compose down
docker-compose up -d
```
This stops containers, then starts them fresh. Migrations run automatically.

### Restart with Rebuild (After Dockerfile Changes)
```bash
docker-compose down
docker-compose up -d --build
```
This rebuilds images and starts containers. Migrations run automatically.

## What Happens Automatically

When you run `docker-compose up`:

1. **PostgreSQL starts** → Health check ensures it's ready
2. **Redis starts** → Health check ensures it's ready  
3. **API starts** → Entrypoint script runs:
   - ✅ Waits for database (up to 60 seconds)
   - ✅ Runs migrations automatically (`alembic upgrade head`)
   - ✅ Starts the FastAPI application
4. **Frontend starts** → Waits for API to be ready

## Verification

After restarting, verify everything is working:

```bash
# Check all containers are running
docker-compose ps

# Check API logs (should show migrations completed)
docker-compose logs api | grep -i migration

# Test API health
curl http://localhost:8000/health

# Test database connection
docker-compose exec api python -c "from app.database import engine; engine.connect(); print('Database connected!')"
```

## Common Scenarios

### Scenario 1: Simple Restart
**Question:** "I just want to restart the containers"
**Answer:** 
```bash
docker-compose restart
```
✅ No manual steps needed - everything is automatic

### Scenario 2: Code Changes
**Question:** "I changed some Python/React code"
**Answer:**
```bash
docker-compose down
docker-compose up -d
```
✅ Migrations run automatically, no manual steps

### Scenario 3: New Migration File
**Question:** "I added a new Alembic migration"
**Answer:**
```bash
docker-compose down
docker-compose up -d
```
✅ The new migration runs automatically via entrypoint.sh

### Scenario 4: Dockerfile Changes
**Question:** "I changed the Dockerfile"
**Answer:**
```bash
docker-compose down
docker-compose up -d --build
```
✅ Images rebuild, migrations run automatically

## Troubleshooting

### If Migrations Don't Run

Check the entrypoint script is being used:
```bash
docker-compose logs api | head -20
```

You should see:
```
=== Habit Tracker API Startup ===
Waiting for database to be ready...
PostgreSQL is up - executing migrations
Running database migrations...
Migrations completed successfully!
```

### If Database Connection Fails

Check database is ready:
```bash
docker-compose exec postgres pg_isready -U postgres
```

Check environment variables:
```bash
docker-compose exec api env | grep POSTGRES
```

### If You Need to Run Migrations Manually

Only if automatic migration fails:
```bash
docker-compose exec api alembic upgrade head
```

## Important Notes

1. **Data Persistence**: Your database data is stored in Docker volumes, so it persists across restarts
2. **No Manual Steps**: You never need to manually:
   - Connect to the database
   - Run migrations
   - Configure connection strings
3. **Health Checks**: Docker Compose waits for services to be healthy before starting dependent services
4. **Automatic Retries**: The entrypoint script retries database connection up to 60 times (60 seconds)

## Summary

**You can simply run:**
```bash
docker-compose up -d
```

**Everything else is handled automatically:**
- ✅ Database connections
- ✅ Migrations
- ✅ Service dependencies
- ✅ Health checks

No manual intervention needed! 🎉

