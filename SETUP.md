# Complete Setup Guide

This guide will walk you through setting up the Habit Tracker application from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
- **Git**
- **Node.js** 18+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **PostgreSQL** client tools (optional, for direct database access)
- **Redis** client tools (optional, for direct cache access)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd habit-tracker
```

## Step 2: Environment Configuration

### Backend Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```env
   # Database
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/habit_tracker
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-secure-password
   POSTGRES_DB=habit_tracker

   # Redis
   REDIS_URL=redis://redis:6379/0

   # JWT - Generate a secure secret key
   SECRET_KEY=your-super-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # AWS (for production)
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=habit-tracker-assets

   # Sentry (optional)
   SENTRY_DSN=your-sentry-dsn

   # Rate Limiting
   RATE_LIMIT_PER_MINUTE=60

   # Application
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

### Frontend Environment Variables

1. Navigate to frontend directory:
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

2. Edit `.env.local`:
   ```env
   REACT_APP_API_URL=http://localhost:8000/api/v1
   REACT_APP_SENTRY_DSN=your-sentry-dsn
   ```

## Step 3: Docker Setup

### Using Docker Compose (Recommended for Development)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Run database migrations:**
   ```bash
   docker-compose exec api python -m alembic upgrade head
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Prometheus: http://localhost:9090

### Individual Service Management

**Start specific services:**
```bash
docker-compose up -d postgres redis
docker-compose up -d api
docker-compose up -d frontend
```

**Stop services:**
```bash
docker-compose down
```

**Rebuild services:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Step 4: Local Development Setup

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp ../.env.example .env
   # Edit .env with local database URL:
   # DATABASE_URL=postgresql://postgres:postgres@localhost:5432/habit_tracker
   # REDIS_URL=redis://localhost:6379/0
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

## Step 5: Database Management

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### Database Access

**Using Docker:**
```bash
docker-compose exec postgres psql -U postgres -d habit_tracker
```

**Using local PostgreSQL:**
```bash
psql -h localhost -U postgres -d habit_tracker
```

## Step 6: Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Step 7: Production Deployment

### AWS EC2 Setup

1. **Launch EC2 instance:**
   - Choose Ubuntu 22.04 LTS
   - Configure security groups (ports 80, 443, 22, 8000)
   - Create key pair

2. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Docker:**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo usermod -aG docker $USER
   ```

4. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd habit-tracker
   ```

5. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

6. **Start services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### RDS Setup

1. **Create RDS PostgreSQL instance:**
   - Engine: PostgreSQL 15
   - Instance class: db.t3.micro (for testing)
   - Storage: 20GB
   - Master username/password

2. **Update DATABASE_URL in .env:**
   ```env
   DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/habit_tracker
   ```

### S3 Setup

1. **Create S3 bucket:**
   - Bucket name: habit-tracker-assets
   - Region: us-east-1
   - Configure CORS if needed

2. **Update .env:**
   ```env
   S3_BUCKET_NAME=habit-tracker-assets
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   ```

## Step 8: Monitoring Setup

### Prometheus

Prometheus is already configured in `docker-compose.yml`. Access at:
- http://localhost:9090

### Sentry

1. **Create Sentry account:**
   - Go to https://sentry.io
   - Create a new project
   - Get DSN

2. **Update .env:**
   ```env
   SENTRY_DSN=your-sentry-dsn
   ```

### Logging

Logs are stored in:
- Backend: `backend/logs/habit_tracker.log`
- Docker: `docker-compose logs -f api`

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec api python -c "from app.database import engine; engine.connect()"
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

### Port Conflicts

If ports are already in use:
1. Change ports in `docker-compose.yml`
2. Or stop conflicting services

### Migration Issues

```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec api python -m alembic upgrade head
```

## Next Steps

1. Create your first user account
2. Add habits
3. Start tracking completions
4. View analytics and streaks

## Support

For issues or questions:
- Check the README.md
- Review logs: `docker-compose logs`
- Check API docs: http://localhost:8000/docs

