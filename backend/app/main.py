from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import make_asgi_app
from app.config import settings
from app.shared.rate_limiter import get_rate_limiter
from app.auth.routes import router as auth_router
from app.habits.routes import router as habits_router
from app.completions.routes import router as completions_router
from app.analytics.routes import router as analytics_router
from app.jobs.streak_calculator import start_streak_calculator
from app.jobs.reminder_scheduler import start_reminder_scheduler
from app.logging_config import setup_logging
import os

# Setup logging
os.makedirs('logs', exist_ok=True)
setup_logging()

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )

# Initialize FastAPI app
app = FastAPI(
    title="Habit Tracker API",
    description="A comprehensive habit tracking API with microservices architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
limiter = get_rate_limiter()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses"""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def startup_event():
    """Startup event - initialize database connection and background jobs"""
    from app.database import check_database_connection
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_database_connection():
        logger.error("Database connection check failed on startup!")
        raise RuntimeError("Database connection failed on startup")
    logger.info("Database connection verified successfully")
    
    # Initialize background jobs
    start_streak_calculator()
    start_reminder_scheduler()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Habit Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check"""
    from app.database import check_database_connection
    
    db_status = check_database_connection()
    if db_status:
        return {
            "status": "healthy",
            "database": "connected"
        }
    else:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(habits_router, prefix="/api/v1/habits", tags=["Habits"])
app.include_router(completions_router, prefix="/api/v1/completions", tags=["Completions"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error", "message": str(exc)}
    )

