"""
Report retrieval endpoints
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models import ReportResponse


router = APIRouter(tags=["Reports"])
logger = logging.getLogger(__name__)


@router.get("/report/{session_id}")
async def get_report(session_id: str):
    """Retrieve analysis report for specific session"""
    try:
        logger.info(f"Fetching report for session: {session_id}")
        
        return {
            "session_id": session_id,
            "status": "Report retrieval not implemented in this version",
            "note": "Use session_id from analysis response to track results"
        }
    
    except Exception as e:
        logger.error(f"Report retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
