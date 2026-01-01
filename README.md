# Habit Tracker - Microservices Architecture

A comprehensive habit tracking application built with React, FastAPI, PostgreSQL, and Redis, following microservices architecture principles.

## 🏗️ Architecture

- **Frontend**: React with TypeScript
- **Backend**: FastAPI (Python) with microservices
- **Database**: PostgreSQL
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Winston, Sentry
- **Deployment**: AWS (EC2, RDS, S3)

## 📊 Database Schema

### Tables
1. **Users** - User accounts and authentication
2. **Habits** - User habit definitions
3. **Habit Completions** - Daily completion records
4. **User Preferences** - User settings and preferences
5. **Streaks** - Computed/cached streak data

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/tirshiva/habit-tracker.git
   cd habit-tracker
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api python -m alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Redis: localhost:6379
   - PostgreSQL: localhost:5432

### Local Development Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API endpoint
   ```

4. **Start development server**
   ```bash
   npm start
   ```

## 📁 Project Structure

```
habit-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   ├── habits/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   ├── completions/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── models.py
│   │   ├── analytics/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   ├── security.py
│   │   │   ├── rate_limiter.py
│   │   │   └── schemas.py
│   │   └── jobs/
│   │       ├── __init__.py
│   │       ├── streak_calculator.py
│   │       └── reminder_scheduler.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── .env.example
└── README.md
```

## 🔐 Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/habit_tracker
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=habit_tracker

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=habit-tracker-assets

# Sentry
SENTRY_DSN=your-sentry-dsn

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_SENTRY_DSN=your-sentry-dsn
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 CI/CD

The project includes GitHub Actions workflows for:
- Automated testing
- Docker image building
- Deployment to AWS

## 📈 Monitoring

- **Prometheus**: Metrics collection at `/metrics`
- **Winston**: Structured logging
- **Sentry**: Error tracking and monitoring

## 🚢 Deployment

### AWS Deployment

1. **EC2 Setup**
   - Launch EC2 instance
   - Configure security groups
   - Install Docker

2. **RDS Setup**
   - Create PostgreSQL RDS instance
   - Update DATABASE_URL in .env

3. **S3 Setup**
   - Create S3 bucket for static assets
   - Configure bucket policies

4. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

