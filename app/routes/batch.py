"""
Batch and custom analysis endpoints
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.models import BatchAnalysisRequest, AnalysisResponse
from app.utils import get_timestamp
from armor_workflow import FinGuardOrchestrator


router = APIRouter(prefix="/analyze", tags=["Batch Analysis"])
logger = logging.getLogger(__name__)
orchestrator = FinGuardOrchestrator()


@router.post("/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """Analyze multiple items in batch mode"""
    try:
        logger.info(f"Processing batch analysis with {len(request.inputs)} items")
        
        batch_results = []
        for item in request.inputs:
            result = orchestrator.process_input(
                user_input=item.get("input", ""),
                media_type=item.get("media_type", "TEXT"),
                mode=request.mode,
                metadata=item.get("metadata")
            )
            batch_results.append(result)
        
        return {
            "batch_size": len(batch_results),
            "results": batch_results,
            "completed_at": get_timestamp()
        }
    
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom")
async def analyze_custom(request: Dict[str, Any]):
    """Analyze with custom request format and parameters"""
    try:
        logger.info("Processing custom analysis request")
        
        result = orchestrator.process_input(
            user_input=request.get("input", ""),
            media_type=request.get("media_type", "TEXT").upper(),
            mode=request.get("mode", "COMMAND").upper(),
            metadata=request.get("metadata")
        )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        logger.error(f"Custom analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
