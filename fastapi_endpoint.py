"""
FinGuard FastAPI Application
Multi-Agent Security Analysis System powered by ArmorIQ

This module initializes and configures the FastAPI application with all routes,
middleware, and exception handlers for the FinGuard security analysis system.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.utils import setup_logger
from app.routes import health, analysis, batch, reports


# Initialize logger
logger = setup_logger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("FinGuard FastAPI application started")
    yield
    # Shutdown
    logger.info("FinGuard FastAPI application shutdown")


# Create FastAPI application
app = FastAPI(
    title="FinGuard API",
    description="Multi-Agent Security Analysis System powered by ArmorIQ",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(batch.router)
app.include_router(reports.router)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper formatting"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
