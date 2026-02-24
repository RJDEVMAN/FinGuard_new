# FinGuard Testing Guide & Scenarios

Complete testing guide for the FinGuard Multi-Agent Security System with practical test cases and expected outcomes.

## 🧪 Test Environment Setup

### Prerequisites
- Python 3.10+
- Virtual environment activated
- All dependencies installed
- `.env` file configured with ArmorIQ credentials
- API server running (for endpoint tests)

### Start Services

```bash
# Terminal 1: Start API Server
python -m uvicorn fastapi_endpoint:app --reload --port 8000

# Terminal 2: Run CLI tests
python armor_workflow.py
```

## 📋 Test Categories

### 1. Unit Tests - CLI Mode

#### Test 1.1: Simple Text Analysis (SAFE)
**Input**: 
- Text: "Regular bank transfer completed successfully"
- Media Type: TEXT
- Mode: COMMAND

**Expected Output**:
```json
{
  "final_decision": "SAFE_APPROVED",
  "agent_reports": {
    "fraud_agent": {
      "decision": "SAFE"
    }
  },
  "audit_trail": [...]
}
```

**Validation**: 
- ✓ No escalation to Risk Agent
- ✓ Decision is SAFE_APPROVED
- ✓ No blocked actions

---

#### Test 1.2: Fraud Detection (Text)
**Input**:
- Text: "Notice suspicious deepfake video of CEO with voice manipulation and altered timestamps"
- Media Type: TEXT
- Mode: COMMAND

**Expected Output**:
```json
{
  "final_decision": "FRAUD_DETECTED_MONITOR",
  "agent_reports": {
    "fraud_agent": {
      "decision": "FRAUD",
      "escalate_to_risk": true
    },
    "risk_agent": {
      "risk_score": 75,
      "escalate_to_compliance": true
    },
    "compliance_agent": {
      "aml_kyc_status": "VIOLATION",
      "violations": [...]
    }
  },
  "audit_trail": [...]
}
```

**Validation**:
- ✓ All 4 agents executed
- ✓ Fraud detected and escalated
- ✓ Compliance violations logged
- ✓ Complete audit trail present

---

#### Test 1.3: Check Required (Gray Area)
**Input**:
- Text: "Document appears slightly modified in footer area, confidence level uncertain"
- Media Type: TEXT
- Mode: COMMAND

**Expected Output**:
```json
{
  "final_decision": "REQUIRE_MANUAL_REVIEW",
  "agent_reports": {
    "fraud_agent": {
      "decision": "CHECK-REQUIRED",
      "escalate_to_risk": true
    }
  }
}
```

**Validation**:
- ✓ CHECK-REQUIRED decision made
- ✓ Escalates for manual review
- ✓ Partial agent pipeline execution

---

#### Test 1.4: Interactive Mode (ASK)
**Input**:
- Text: "Possible fraud detected"
- Media Type: TEXT
- Mode: ASK

**Interactive Flow**:
```
FraudAgent: I detected potential fraud. Should I escalate to Risk Agent? (yes/no): 
[User inputs: no]

Expected: 
- User override recorded in audit trail
- ✓ Escalation blocked
- ✓ Log entry: USER_OVERRIDE, ESCALATION_BLOCKED
```

**Validation**:
- ✓ User prompted for confirmation
- ✓ Override respected
- ✓ Decision logged

---

### 2. API Integration Tests

#### Test 2.1: Health Check
```bash
curl -X GET "http://localhost:8000/health"

Expected Response:
{
  "status": "healthy",
  "message": "FinGuard system is operational"
}
```

#### Test 2.2: Text Analysis via API
```bash
curl -X POST "http://localhost:8000/analyze/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text_content": "Verify this suspicious transaction",
    "mode": "COMMAND",
    "metadata": {"source": "api_test"}
  }'

Expected: 200 with complete analysis response
```

#### Test 2.3: Image Analysis via API
```bash
curl -X POST "http://localhost:8000/analyze/image" \
  -F "file=@test_image.jpg" \
  -F "mode=COMMAND" \
  -F "source=api_test"

Expected: 200 with image analysis results
```

#### Test 2.4: Video Analysis via API
```bash
curl -X POST "http://localhost:8000/analyze/video" \
  -F "file=@test_video.mp4" \
  -F "mode=COMMAND" \
  -F "source=api_test"

Expected: Analysis for deepfakes and frame manipulation
```

#### Test 2.5: Audio Analysis via API
```bash
curl -X POST "http://localhost:8000/analyze/audio" \
  -F "file=@test_audio.wav" \
  -F "mode=COMMAND" \
  -F "source=api_test"

Expected: Voice deepfake detection results
```

#### Test 2.6: Document Analysis via API
```bash
curl -X POST "http://localhost:8000/analyze/document" \
  -F "file=@test_document.pdf" \
  -F "mode=COMMAND" \
  -F "source=api_test"

Expected: Document tampering detection
```

---

### 3. Policy Enforcement Tests

#### Test 3.1: Agent Policy Isolation
**Scenario**: Verify Fraud Agent cannot access Risk Agent actions

**Test**:
Execute plan with:
- FraudAgent trying to invoke: `risk-mcp/calculate_risk_score`

**Expected Result**:
```
✗ Blocked by policy
├─ Agent: FraudAgent
├─ Action: calculate_risk_score
├─ Reason: Action not in allow list ["fraud_agent/*", "fraud-mcp/*"]
└─ Status: BLOCKED and LOGGED
```

**Validation**:
- ✓ Action blocked before execution
- ✓ Blocked action logged in `blocked_actions`
- ✓ Error recorded and escalated
- ✓ Pipeline continues to Memory Agent

#### Test 3.2: Dynamic Policy Enforcement
**Scenario**: Verify policy is enforced at token level

**Test**:
- Fraud Agent generates token with its policy
- Attempt to execute action outside policy scope
- Verify CSRG-IAP rejects at proxy level

**Expected**:
- ✓ Proxy verification fails
- ✓ Action not reaching MCP
- ✓ Error logged with policy violation reason

---

### 4. Delegation Chain Tests

#### Test 4.1: Multi-Agent Delegation
**Scenario**: Complete delegation chain from Fraud → Risk → Compliance

**Test Input**:
- High-risk fraud content that triggers full pipeline

**Expected Delegation Flow**:
```
1. FraudAgent creates plan + gets token
   ├─ Log: Plan captured
   ├─ Log: Intent token generated
   └─ Decision: FRAUD

2. FraudAgent delegates to RiskAgent
   ├─ Log: Delegation created
   ├─ Log: Delegation ID: <unique_id>
   └─ RiskAgent receives restricted token

3. RiskAgent executes with delegated token
   ├─ Log: Risk scoring executed
   ├─ Decision: risk_score = 85
   └─ Escalate to Compliance

4. RiskAgent delegates to ComplianceAgent
   ├─ Log: Delegation created
   └─ ComplianceAgent receives token

5. ComplianceAgent validates
   ├─ Log: AML/KYC check executed
   ├─ Log: Regulation validation executed
   └─ Decision: Violations found

6. MemoryUpdateAgent finalizes
   ├─ Log: Consolidation executed
   └─ Log: Audit trail generated
```

**Validation**:
- ✓ All delegation IDs logged
- ✓ Each agent respects restricted permissions
- ✓ Context flows correctly
- ✓ Final report includes full chain

#### Test 4.2: Delegation with Limited Actions
**Scenario**: Verify restricted action list in delegation

**Test**:
- Parent agent creates delegation with `allowed_actions=["specific_action"]`
- Delegate attempts other actions
- Verify only allowed action succeeds

**Expected**:
- ✓ Allowed action: SUCCESS
- ✓ Other actions: BLOCKED
- ✓ Attempts logged

---

### 5. Error Handling Tests

#### Test 5.1: Invalid Plan Structure
**Input**:
```python
plan = {
    "steps": [...]  # Missing "goal"
}
```

**Expected**:
```json
{
  "error": "Missing required field: goal",
  "audit_trail": [...],
  "errors": [{
    "error_type": "PLAN_VALIDATION_FAILED",
    "agent": "FraudAgent"
  }]
}
```

**Validation**:
- ✓ Error captured
- ✓ Graceful failure
- ✓ Logged in errors array

#### Test 5.2: Invalid Media Type
**Input**:
```bash
python armor_workflow.py
# Media type: INVALID_TYPE
```

**Expected**:
```
error: Invalid media type or mode: INVALID_TYPE
```

**Validation**:
- ✓ Input validation works
- ✓ Clear error message

#### Test 5.3: Expired Token
**Scenario**: Token expires during pipeline execution

**Expected**:
- ✓ Error caught at invoke level
- ✓ Error logged with reason
- ✓ New token generated if possible
- ✓ Operation retried or failed gracefully

#### Test 5.4: Network Failure
**Scenario**: ArmorIQ proxy unreachable

**Expected**:
```json
{
  "error": "NetworkError: Unable to reach proxy",
  "audit_trail": [...],
  "errors": [{
    "error_type": "NETWORK_ERROR",
    "agent": "FraudAgent"
  }]
}
```

**Validation**:
- ✓ Graceful error handling
- ✓ Timeout not exceeded
- ✓ Error logged and reported

---

### 6. Batch Analysis Tests

#### Test 6.1: Batch Processing Multiple Inputs
```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "content": "Safe transaction",
        "media_type": "TEXT",
        "metadata": {"id": "batch_1"}
      },
      {
        "content": "Suspicious activity",
        "media_type": "TEXT",
        "metadata": {"id": "batch_2"}
      },
      {
        "content": "Normal operation",
        "media_type": "TEXT",
        "metadata": {"id": "batch_3"}
      }
    ],
    "mode": "COMMAND"
  }'

Expected Response:
{
  "total_items": 3,
  "processed": 3,
  "results": [
    {"final_decision": "SAFE_APPROVED", ...},
    {"final_decision": "FRAUD_DETECTED_MONITOR", ...},
    {"final_decision": "SAFE_APPROVED", ...}
  ]
}
```

**Validation**:
- ✓ All items processed
- ✓ Individual decisions for each
- ✓ Batch metadata preserved

#### Test 6.2: Batch with Failures
**Scenario**: Include invalid input in batch

**Expected**:
- ✓ Other items continue processing
- ✓ Failed item has error field
- ✓ Total count = 3, successful = 2

---

### 7. Media Type Specific Tests

#### Test 7.1: Image Deepfake Detection
**Setup**:
1. Create sample image or use existing test image
2. Submit via `/analyze/image`

**Test Data**:
```bash
# Using Python to create a simple test
from PIL import Image
import numpy as np

img = Image.new('RGB', (100, 100), color='red')
img.save('test_image.jpg')
```

**Expected**:
- ✓ Image base64 encoded
- ✓ Deepfake detection analysis
- ✓ Anomaly detection
- ✓ Result returned with confidence scores

#### Test 7.2: Video Frame Analysis
**Test**:
```bash
curl -X POST "http://localhost:8000/analyze/video" \
  -F "file=@sample_video.mp4" \
  -F "mode=COMMAND"
```

**Expected**:
- ✓ Video frame-by-frame analysis
- ✓ Deepfake indicators
- ✓ Audio sync issues detection
- ✓ Temporal artifact detection

#### Test 7.3: Audio Voice Deepfake
**Test**:
```bash
curl -X POST "http://localhost:8000/analyze/audio" \
  -F "file=@sample_audio.wav" \
  -F "mode=COMMAND"
```

**Expected**:
- ✓ Voice pattern analysis
- ✓ AI synthesis detection
- ✓ Voice similarity checks
- ✓ Artifact detection

---

### 8. Audit Trail & Logging Tests

#### Test 8.1: Audit Trail Completeness
**Test**:
1. Run complete analysis
2. Check `fingard_audit.log`
3. Verify all entries present

**Expected Log Entries**:
```
✓ Plan capture logs
✓ Intent token generation logs
✓ Each action invocation log
✓ Decision point logs
✓ Delegation logs
✓ Error/warning logs
✓ Blocked action logs
✓ Final report logs
```

**Validation**:
- ✓ Every action has timestamp
- ✓ All agents logged
- ✓ Sequential order maintained
- ✓ Log level appropriate (INFO/WARNING/ERROR)

#### Test 8.2: JSON Report Structure
**Test**:
1. Run analysis
2. Load `fingard_final_report.json`
3. Validate structure

**Expected Structure**:
```json
{
  "session_id": "...",
  "timestamp": "...",
  "mode": "...",
  "media_type": "...",
  "final_decision": "...",
  "agent_reports": {
    "fraud_agent": {...},
    "risk_agent": {...},
    "compliance_agent": {...},
    "memory_agent": {...}
  },
  "audit_trail": [...],
  "blocked_actions": [...],
  "errors": [...]
}
```

**Validation**:
- ✓ All required fields present
- ✓ Correct data types
- ✓ No missing reports
- ✓ Complete trail

---

## 🏃 Quick Test Commands

### CLI Quick Test
```bash
# Test 1: Safe content
python armor_workflow.py
# Input: "Normal payment"
# Type: text
# Mode: COMMAND
# Expected: SAFE_APPROVED

# Test 2: Fraud content
python armor_workflow.py
# Input: "Deepfake CEO video detected"
# Type: text
# Mode: ASK
# Expected: Full pipeline, ask for confirmation
```

### API Quick Tests
```bash
# Health check
curl http://localhost:8000/health

# Text analysis
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"text_content":"Test content","mode":"COMMAND"}'

# System info
curl http://localhost:8000/info

# Batch test
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "inputs":[{"content":"test","media_type":"TEXT"}],
    "mode":"COMMAND"
  }'
```

---

## 📊 Test Results Template

### Test Execution Log
```markdown
## Test Suite: FinGuard Multi-Agent System
**Date**: [Date]
**Environment**: [OS/Python Version]
**Duration**: [Total Time]

### Summary
- Total Tests: [#]
- Passed: [#]
- Failed: [#]
- Skipped: [#]

### Detailed Results

#### Category 1: Unit Tests
- [x] Test 1.1 PASSED
- [x] Test 1.2 PASSED
- [ ] Test 1.3 FAILED - Reason

#### Category 2: API Tests
- [x] Test 2.1 PASSED

...

### Issues Found
1. Issue description and resolution
2. ...

### Performance Metrics
- Average plan capture time: [ms]
- Average token generation: [ms]
- Average invocation time: [ms]
- Total pipeline time: [ms]

### Recommendations
1. ...
```

---

## 🔍 Debugging Tips

### 1. Check Audit Logs
```bash
tail -f fingard_audit.log
```

### 2. Examine Final Report
```bash
cat fingard_final_report.json | python -m json.tool
```

### 3. Debug API Requests
```bash
# Enable verbose output
curl -v -X POST http://localhost:8000/analyze/text ...

# Check server logs
# Terminal running uvicorn will show detailed logs
```

### 4. Trace Agent Execution
Look for agent names in audit trail:
```
[FraudAgent] - fraud detection action
[RiskAgent] - risk assessment action
[ComplianceAgent] - compliance validation
[MemoryUpdateAgent] - audit trail
```

### 5. Policy Verification
Search blocked_actions in final report:
```json
"blocked_actions": [
  {
    "agent": "FraudAgent",
    "action": "unauthorized_action",
    "reason": "Action not in allow list"
  }
]
```

---

## 📈 Performance Benchmarks

### Expected Response Times
- Simple text analysis: 1-2 seconds
- Image analysis: 2-5 seconds (depends on size)
- Video analysis: 5-20 seconds (depends on duration)
- Audio analysis: 3-10 seconds (depends on duration)
- Full pipeline (all agents): 2-3 seconds base time
- Batch of 10 items: 15-30 seconds

### Resource Usage
- Memory: ~200-500 MB base + media size
- CPU: Variable based on analysis complexity
- Network: Base API key validation + data transfer

---

## ✅ Success Criteria

- [ ] All 4 agents execute correctly in pipeline
- [ ] Policy enforcement blocks unauthorized actions
- [ ] Delegation tokens work across agents
- [ ] Audit trail is complete and accurate
- [ ] All media types are supported
- [ ] Error handling is graceful
- [ ] API responses are consistent
- [ ] Logging is comprehensive
- [ ] Reports are well-structured
- [ ] Performance meets benchmarks

---

**Last Updated**: February 24, 2026  
**Test Coverage**: Comprehensive  
**Status**: Ready for Testing
