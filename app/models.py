"""
Pydantic models for FinGuard API requests and responses
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class TextAnalysisRequest(BaseModel):
    """Request model for text analysis endpoint"""
    text_content: str
    mode: str = "COMMAND"
    metadata: Optional[Dict[str, Any]] = None


class MediaAnalysisRequest(BaseModel):
    """Request model for media file analysis"""
    file_name: str
    media_type: str
    mode: str = "COMMAND"
    metadata: Optional[Dict[str, Any]] = None


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    inputs: list[Dict[str, Any]]
    mode: str = "COMMAND"


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoints"""
    session_id: str
    final_decision: str
    agent_reports: Dict[str, Any]
    audit_trail: list
    errors: Optional[list] = None


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis"""
    batch_size: int
    results: list[Dict[str, Any]]
    completed_at: str


class ReportResponse(BaseModel):
    """Response model for report retrieval"""
    session_id: str
    status: str
    note: Optional[str] = None
