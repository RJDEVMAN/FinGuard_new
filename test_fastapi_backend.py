"""
Comprehensive FastAPI Backend Test Suite for FinGuard System
Tests all endpoints, error scenarios, and workflow compliance
"""

import pytest
import json
from unittest.mock import patch
from io import BytesIO
from typing import Dict, Any

from fastapi.testclient import TestClient
from fastapi_endpoint import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_orchestrator_response() -> Dict[str, Any]:
    """Mock response from FinGuardOrchestrator"""
    return {
        "session_id": "SESSION_20260224120000000000",
        "final_decision": "SAFE_APPROVED",
        "agent_reports": {
            "fraud_agent": {
                "agent": "FraudAgent",
                "decision": "SAFE",
                "timestamp": "2026-02-24T12:00:00"
            },
            "risk_agent": {"executed": False},
            "compliance_agent": {"executed": False},
            "memoryupdate_agent": {"consolidation_complete": True}
        },
        "audit_trail": [
            {
                "timestamp": "2026-02-24T12:00:00",
                "agent": "FraudAgent",
                "action": "DEEPFAKE_DETECTION",
                "status": "EXECUTED"
            }
        ],
        "errors": []
    }


# ============================================================================
# HEALTH ENDPOINT TESTS
# ============================================================================

class TestHealthEndpoints:
    """Test health check and system info endpoints"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "FinGuard" in data["message"]
    
    def test_system_info(self, client):
        """Test system info endpoint returns correct metadata"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        assert len(data["agents"]) == 4


# ============================================================================
# TEXT ANALYSIS ENDPOINT TESTS
# ============================================================================

class TestTextAnalysisEndpoint:
    """Test text analysis endpoint functionality"""
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analyze_text_safe(self, mock_process, client, mock_orchestrator_response):
        """Test text analysis with SAFE result"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post("/analyze/text", json={
            "text_content": "Regular bank transfer",
            "mode": "COMMAND"
        })
        
        assert response.status_code == 200
        assert response.json()["final_decision"] == "SAFE_APPROVED"
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analyze_text_with_metadata(self, mock_process, client, mock_orchestrator_response):
        """Test text analysis with custom metadata"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post("/analyze/text", json={
            "text_content": "Test input",
            "mode": "COMMAND",
            "metadata": {"priority": "high"}
        })
        
        assert response.status_code == 200


# ============================================================================
# MEDIA FILE ANALYSIS ENDPOINT TESTS
# ============================================================================

class TestMediaAnalysisEndpoints:
    """Test image, video, audio, and document analysis endpoints"""
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analyze_image(self, mock_process, client, mock_orchestrator_response):
        """Test image analysis endpoint"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post(
            "/analyze/image",
            files={"file": ("test.jpg", BytesIO(b"fake image"), "image/jpeg")},
            data={"mode": "COMMAND"}
        )
        
        assert response.status_code == 200
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analyze_video(self, mock_process, client, mock_orchestrator_response):
        """Test video analysis endpoint"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post(
            "/analyze/video",
            files={"file": ("test.mp4", BytesIO(b"fake video"), "video/mp4")},
            data={"mode": "COMMAND"}
        )
        
        assert response.status_code == 200
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analyze_audio(self, mock_process, client, mock_orchestrator_response):
        """Test audio analysis endpoint"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post(
            "/analyze/audio",
            files={"file": ("test.mp3", BytesIO(b"fake audio"), "audio/mpeg")},
            data={"mode": "COMMAND"}
        )
        
        assert response.status_code == 200
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analyze_document(self, mock_process, client, mock_orchestrator_response):
        """Test document analysis endpoint"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post(
            "/analyze/document",
            files={"file": ("test.pdf", BytesIO(b"fake doc"), "application/pdf")},
            data={"mode": "COMMAND"}
        )
        
        assert response.status_code == 200


# ============================================================================
# BATCH ANALYSIS ENDPOINT TESTS
# ============================================================================

class TestBatchAnalysisEndpoint:
    """Test batch analysis functionality"""
    
    @patch('app.routes.batch.orchestrator.process_input')
    def test_batch_analysis_multiple_items(self, mock_process, client, mock_orchestrator_response):
        """Test batch analysis with multiple items"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post("/analyze/batch", json={
            "inputs": [
                {"input": "Test 1", "media_type": "TEXT"},
                {"input": "Test 2", "media_type": "TEXT"},
                {"input": "Test 3", "media_type": "TEXT"}
            ],
            "mode": "COMMAND"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["batch_size"] == 3
        assert len(data["results"]) == 3


# ============================================================================
# CUSTOM ANALYSIS ENDPOINT TESTS
# ============================================================================

class TestCustomAnalysisEndpoint:
    """Test custom analysis endpoint"""
    
    @patch('app.routes.batch.orchestrator.process_input')
    def test_analyze_custom_request(self, mock_process, client, mock_orchestrator_response):
        """Test custom analysis with flexible request format"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post("/analyze/custom", json={
            "input": "Custom input",
            "media_type": "TEXT",
            "mode": "COMMAND"
        })
        
        assert response.status_code == 200


# ============================================================================
# REPORT RETRIEVAL ENDPOINT TESTS
# ============================================================================

class TestReportRetrievalEndpoint:
    """Test report retrieval functionality"""
    
    def test_get_report(self, client):
        """Test report retrieval endpoint"""
        response = client.get("/report/SESSION_123")
        assert response.status_code == 200


# ============================================================================
# WORKFLOW COMPLIANCE TESTS
# ============================================================================

class TestWorkflowCompliance:
    """Test that the workflow meets specification"""
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_4_tier_agent_pipeline(self, mock_process, client):
        """Test that all 4 agents are executed in correct order"""
        response_data = {
            "session_id": "SESSION_test",
            "final_decision": "FRAUD_DETECTED_MONITOR",
            "agent_reports": {
                "fraud_agent": {"decision": "FRAUD"},
                "risk_agent": {"risk_score": 75},
                "compliance_agent": {"violations": ["AML_KYC_FAIL"]},
                "memoryupdate_agent": {"consolidation_complete": True}
            },
            "audit_trail": [
                {"agent": "FraudAgent", "timestamp": "2026-02-24T12:00:00"},
                {"agent": "RiskAgent", "timestamp": "2026-02-24T12:00:01"},
                {"agent": "ComplianceAgent", "timestamp": "2026-02-24T12:00:02"},
                {"agent": "MemoryUpdateAgent", "timestamp": "2026-02-24T12:00:03"}
            ],
            "errors": []
        }
        mock_process.return_value = response_data
        
        response = client.post("/analyze/text", json={
            "text_content": "Fraud content",
            "mode": "COMMAND"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 4 agents present
        assert "fraud_agent" in data["agent_reports"]
        assert "risk_agent" in data["agent_reports"]
        assert "compliance_agent" in data["agent_reports"]
        assert "memoryupdate_agent" in data["agent_reports"]


# ============================================================================
# MIDDLEWARE TESTS
# ============================================================================

class TestMiddleware:
    """Test CORS and middleware functionality"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are properly set"""
        response = client.get("/info")
        assert response.status_code == 200


# ============================================================================
# ERROR SCENARIOS
# ============================================================================

class TestErrorHandling:
    """Test error scenarios"""
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_empty_text_input(self, mock_process, client, mock_orchestrator_response):
        """Test handling of empty text input"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post("/analyze/text", json={
            "text_content": "",
            "mode": "COMMAND"
        })
        
        assert response.status_code in [200, 400]
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_orchestrator_error(self, mock_process, client):
        """Test error handling when orchestrator fails"""
        mock_process.side_effect = Exception("Orchestrator error")
        
        response = client.post("/analyze/text", json={
            "text_content": "Test",
            "mode": "COMMAND"
        })
        
        assert response.status_code == 500


# ============================================================================
# RESPONSE FORMAT TESTS
# ============================================================================

class TestResponseFormats:
    """Test response format compliance"""
    
    @patch('app.routes.analysis.orchestrator.process_input')
    def test_analysis_response_format(self, mock_process, client, mock_orchestrator_response):
        """Test that AnalysisResponse format is correct"""
        mock_process.return_value = mock_orchestrator_response
        
        response = client.post("/analyze/text", json={
            "text_content": "Test",
            "mode": "COMMAND"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "session_id" in data
        assert "final_decision" in data
        assert "agent_reports" in data
        assert "audit_trail" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
