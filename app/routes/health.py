"""
Health check and system information endpoints
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models import HealthResponse


router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if FinGuard system is operational"""
    try:
        return {
            "status": "healthy",
            "message": "FinGuard system is operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def system_info():
    """Get system information and configuration"""
    return {
        "system": "FinGuard Multi-Agent, Financial Defense Security System",
        "version": "1.0.0",
        "powered_by": "ArmorIQ",
        "agents": [
            "FraudAgent (Primary)",
            "RiskAgent (Secondary)",
            "ComplianceAgent (Tertiary)",
            "MemoryUpdateAgent (Final)"
        ],
        "supported_media_types": ["text", "image", "audio", "video", "document"],
        "supported_modes": ["ASK", "COMMAND"]
    }
