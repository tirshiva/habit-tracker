# Habit Tracker

A habit tracking application built with React, FastAPI, PostgreSQL, and Redis, following microservices architecture principles.

## Architecture

- **Frontend**: React with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Winston, Sentry
- **Deployment**: AWS (EC2, RDS, S3)

## Database Schema

### Tables
1. **Users** - User accounts and authentication
2. **Habits** - User habit definitions
3. **Habit Completions** - Daily completion records
4. **User Preferences** - User settings and preferences
5. **Streaks** - Computed/cached streak data

## Project Structure

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
## Contributing

Contributions are welcome! Please read our contributing guidelines first.

## Author

Shivanshu Tiwari


