# Quick Start Guide

## Docker Container Restart Steps

### Quick Restart (No Code Changes)
```bash
docker-compose restart
```

### Restart After Code Changes
```bash
# Stop containers
docker-compose down

# Rebuild and start
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### Restart Specific Service
```bash
# Restart API only
docker-compose restart api

# Restart Frontend only
docker-compose restart frontend

# Restart Database (⚠️ be careful)
docker-compose restart postgres
```

### Full Clean Restart (Removes All Data)
```bash
# ⚠️ WARNING: This deletes all data
docker-compose down -v
docker-compose up -d --build
```

## Common Issues & Solutions

### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Check if ports are in use
netstat -tulpn | grep -E ':(3000|8000|5432|6379)'

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Database Migration Issues
```bash
# Check migration status
docker-compose exec api alembic current

# Run migrations manually
docker-compose exec api alembic upgrade head

# Check database connection
docker-compose exec api python -c "from app.database import engine; engine.connect()"
```

### Frontend Not Updating
```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Clear browser cache
# Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### API Not Responding
```bash
# Check API logs
docker-compose logs api

# Check if API is running
curl http://localhost:8000/health

# Restart API
docker-compose restart api
```

## Production Deployment Checklist

1. **Environment Variables**
   - [ ] Copy `.env.example` to `.env.production`
   - [ ] Update all production values
   - [ ] Set strong SECRET_KEY (min 32 chars)
   - [ ] Configure RDS endpoint
   - [ ] Configure ElastiCache endpoint

2. **AWS Resources**
   - [ ] RDS PostgreSQL created
   - [ ] ElastiCache Redis created
   - [ ] EC2 instance launched
   - [ ] Security Groups configured
   - [ ] Domain/DNS configured (optional)

3. **Deployment**
   - [ ] Code pushed to repository
   - [ ] SSH into EC2 instance
   - [ ] Clone repository
   - [ ] Copy `.env.production` to `.env`
   - [ ] Run `docker-compose -f docker-compose.prod.yml up -d --build`

4. **Verification**
   - [ ] API health check: `curl http://your-domain/api/v1/health`
   - [ ] Frontend loads: `http://your-domain`
   - [ ] Database migrations completed
   - [ ] Logs show no errors

5. **Monitoring**
   - [ ] CloudWatch alarms configured
   - [ ] Logs being collected
   - [ ] Health checks passing

## Useful Commands

```bash
# View all running containers
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Execute command in container
docker-compose exec api bash
docker-compose exec postgres psql -U postgres -d habit_tracker

# Check resource usage
docker stats

# Clean up unused resources
docker system prune
```

## Next Steps

- Read [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed AWS deployment guide
- Check [README.md](./README.md) for project overview
- Review environment variables in `.env.example`

