"""
Text and media analysis endpoints
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, File, UploadFile
from app.models import TextAnalysisRequest, AnalysisResponse
from app.utils import encode_file_to_base64, parse_metadata, prepare_media_metadata
from armor_workflow import FinGuardOrchestrator


router = APIRouter(prefix="/analyze", tags=["Analysis"])
logger = logging.getLogger(__name__)
orchestrator = FinGuardOrchestrator()


@router.post("/text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text content for fraud and security threats"""
    try:
        logger.info(f"Processing text analysis request - Mode: {request.mode}")
        
        result = orchestrator.process_input(
            user_input=request.text_content,
            media_type="TEXT",
            mode=request.mode,
            metadata=request.metadata or {"source": "api_text_endpoint"}
        )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image")
async def analyze_image(
    file: UploadFile = File(...),
    mode: str = "COMMAND",
    metadata: Optional[str] = None
):
    """Analyze image for deepfakes and fraud indicators"""
    try:
        logger.info("Processing image analysis request")
        
        content = await file.read()
        base64_content = encode_file_to_base64(content)
        meta = parse_metadata(metadata)
        
        result = orchestrator.process_input(
            user_input=base64_content,
            media_type="IMAGE",
            mode=mode,
            metadata=prepare_media_metadata(file.filename or "image", meta)
        )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video")
async def analyze_video(
    file: UploadFile = File(...),
    mode: str = "COMMAND",
    metadata: Optional[str] = None
):
    """Analyze video for deepfakes and manipulation"""
    try:
        logger.info("Processing video analysis request")
        
        content = await file.read()
        base64_content = encode_file_to_base64(content)
        meta = parse_metadata(metadata)
        
        result = orchestrator.process_input(
            user_input=base64_content,
            media_type="VIDEO",
            mode=mode,
            metadata=prepare_media_metadata(file.filename or "video", meta)
        )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        logger.error(f"Video analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio")
async def analyze_audio(
    file: UploadFile = File(...),
    mode: str = "COMMAND",
    metadata: Optional[str] = None
):
    """Analyze audio for voice manipulation and deepfakes"""
    try:
        logger.info("Processing audio analysis request")
        
        content = await file.read()
        base64_content = encode_file_to_base64(content)
        meta = parse_metadata(metadata)
        
        result = orchestrator.process_input(
            user_input=base64_content,
            media_type="AUDIO",
            mode=mode,
            metadata=prepare_media_metadata(file.filename or "audio", meta)
        )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        logger.error(f"Audio analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document")
async def analyze_document(
    file: UploadFile = File(...),
    mode: str = "COMMAND",
    metadata: Optional[str] = None
):
    """Analyze document for tampering and authenticity"""
    try:
        logger.info("Processing document analysis request")
        
        content = await file.read()
        base64_content = encode_file_to_base64(content)
        meta = parse_metadata(metadata)
        
        result = orchestrator.process_input(
            user_input=base64_content,
            media_type="DOCUMENT",
            mode=mode,
            metadata=prepare_media_metadata(file.filename or "document", meta)
        )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
