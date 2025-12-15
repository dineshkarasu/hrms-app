"""
HRMS FastAPI Application
Main entry point for the Human Resource Management System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import employees, departments, leaves
from database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup: Initialize database
    import os
    environment = os.getenv("ENVIRONMENT", "dev").upper()
    print(f"🚀 Starting HRMS API in {environment} environment")
    print(f"🌍 Environment: {environment}")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print(f"👋 Shutting down HRMS API ({environment})...")


app = FastAPI(
    title="HRMS API",
    description="Human Resource Management System - API for managing employees, departments, and leave requests with PostgreSQL",
    version="2.0.0",
    contact={
        "name": "HRMS Development Team",
        "email": "support@hrms.example.com",
    },
    lifespan=lifespan
)

# CORS middleware configuration
# Environment-aware CORS origins
import os
environment = os.getenv("ENVIRONMENT", "dev")

# Configure allowed origins based on environment
if environment.lower() == "prod" or environment.lower() == "production":
    allowed_origins = [
        "https://dinesh-app1.zamait.in",
        "http://dinesh-app1.zamait.in",
        "https://hrms.zamait.in",
        "https://api.hrms.zamait.in"
    ]
elif environment.lower() == "staging":
    allowed_origins = [
        "https://staging.hrms.zamait.in",
        "https://staging-api.hrms.zamait.in"
    ]
elif environment.lower() == "test":
    allowed_origins = [
        "https://test.hrms.zamait.in",
        "https://test-api.hrms.zamait.in"
    ]
else:  # dev
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
        "http://web",
        "http://web:80",
        "*"  # Allow all origins in development
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["Departments"])
app.include_router(leaves.router, prefix="/api/v1/leaves", tags=["Leave Management"])


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to HRMS API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    import os
    environment = os.getenv("ENVIRONMENT", "dev")
    return {
        "status": "healthy",
        "service": "HRMS API",
        "environment": environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
