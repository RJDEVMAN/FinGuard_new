# Quick Start Guide - FinGuard System

Get up and running with FinGuard in 5 minutes!

## 🚀 Installation (2 minutes)

### 1. Activate Virtual Environment
```bash
# Windows
code_warriors\Scripts\activate

# Mac/Linux
source code_warriors/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file in project root:
```env
ARMORIQ_API_KEY=your_api_key_here
ARMORIQ_USER_ID=your_user_id_here
ARMORIQ_AGENT_ID=fraud_agent
```

### 4. Test Installation
```bash
python initialisation_client.py
# Should print: "Client initialized successfully!"
```

---

## 🎯 Run Your First Analysis (3 minutes)

### Option A: CLI Mode (Interactive)
```bash
python armor_workflow.py

# Then follow prompts:
# Enter your input: "Check this suspicious transaction"
# Media type: text
# Mode: COMMAND

# View results in console + fingard_final_report.json
```

### Option B: API Mode (Recommended for Testing)

**Terminal 1: Start API Server**
```bash
python -m uvicorn fastapi_endpoint:app --reload --port 8000
# Server will start at http://localhost:8000
```

**Terminal 2: Run Analysis**
```bash
# Simple text analysis
curl -X POST "http://localhost:8000/analyze/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text_content": "Check this suspicious document",
    "mode": "COMMAND"
  }'

# Or visit: http://localhost:8000/docs for interactive API docs
```

---

## 📊 Understanding Output

### Final Decision Types
```
SAFE_APPROVED              → No threats detected
REQUIRE_MANUAL_REVIEW      → Uncertain, needs human review
FRAUD_DETECTED_MONITOR     → Fraud found, monitor closely
BLOCK_IMMEDIATELY          → Critical threat, block now
ESCALATE_TO_AUTHORITIES    → Compliance violations, escalate
```

### Sample Response
```json
{
  "session_id": "SESSION_20260224120000000123",
  "final_decision": "FRAUD_DETECTED_MONITOR",
  "agent_reports": {
    "fraud_agent": {
      "decision": "FRAUD",
      "detection_data": {...}
    },
    "risk_agent": {
      "risk_score": 82,
      "severity": "HIGH"
    },
    "compliance_agent": {
      "violations": ["AML_VIOLATION"],
      "required_actions": [...]
    }
  },
  "audit_trail": [...]
}
```

---

## 🧪 Test Scenarios

### 1. Safe Content
```bash
Input: "Normal bank transfer completed"
Expected: SAFE_APPROVED
```

### 2. Fraud Content
```bash
Input: "Deepfake video of executive with manipulated audio"
Expected: FRAUD_DETECTED_MONITOR → ESCALATE_TO_AUTHORITIES
```

### 3. Uncertain Content
```bash
Input: "Document appears slightly modified"
Expected: REQUIRE_MANUAL_REVIEW
```

### 4. Image Upload
```bash
curl -X POST "http://localhost:8000/analyze/image" \
  -F "file=@suspicious_image.jpg" \
  -F "mode=COMMAND"
```

### 5. Batch Analysis
```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"content": "Text 1", "media_type": "TEXT"},
      {"content": "Text 2", "media_type": "TEXT"}
    ],
    "mode": "COMMAND"
  }'
```

---

## 📁 Generated Files

After running analysis:

### 1. `fingard_audit.log`
Real-time log of all operations
```
2026-02-24 12:00:00,000 - FraudAgent - INFO - Starting fraud analysis...
2026-02-24 12:00:00,100 - FraudAgent - INFO - Plan captured successfully
2026-02-24 12:00:00,200 - RiskAgent - INFO - Starting risk assessment
...
```

### 2. `fingard_final_report.json`
Complete analysis report with all data

---

## 🔗 API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/info` | System information |
| POST | `/analyze/text` | Analyze text |
| POST | `/analyze/image` | Analyze image |
| POST | `/analyze/video` | Analyze video |
| POST | `/analyze/audio` | Analyze audio |
| POST | `/analyze/document` | Analyze document |
| POST | `/analyze/batch` | Batch analysis |
| POST | `/analyze/custom` | Custom analysis |
| GET | `/docs` | API documentation (Swagger UI) |
| GET | `/redoc` | API docs (ReDoc) |

---

## 🎛️ Execution Modes

### ASK Mode (Interactive)
```
Agent proposes decision → User confirms/overrides → Process continues
```

### COMMAND Mode (Autonomous)  
```
Agent makes decision autonomously → No user interaction → Process continues
```

---

## 🐛 Troubleshooting

### Issue: "Client not initialized"
```
Solution: Check .env file has correct ARMORIQ_API_KEY
```

### Issue: Port 8000 already in use
```bash
# Use different port
python -m uvicorn fastapi_endpoint:app --port 8001
```

### Issue: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Check logs
```bash
# View audit trail
tail -f fingard_audit.log

# View final report
cat fingard_final_report.json
```

---

## 📚 Architecture Overview

```
Your Input (Text/Image/Video/Audio/Document)
           ↓
FraudAgent (Detect fraud/deepfakes)
           ↓ (if FRAUD detected)
RiskAgent (Assess severity)
           ↓ (if HIGH RISK)
ComplianceAgent (Validate regulations)
           ↓
MemoryUpdateAgent (Log everything)
           ↓
Final Report (SAFE_APPROVED | FRAUD_DETECTED | etc.)
```

---

## 💡 Key Features

✓ **4-Agent Pipeline**: Specialized analysis at each stage
✓ **Policy Enforcement**: Each agent has restricted permissions
✓ **Multi-Media**: Text, image, video, audio, documents
✓ **Dual Modes**: Interactive (ASK) or Autonomous (COMMAND)
✓ **Complete Audit**: Every action logged and reported
✓ **Delegation**: Secure agent-to-agent communication
✓ **Error Handling**: Graceful failures with detailed reporting
✓ **REST API**: Easy integration via FastAPI

---

## 🎓 Learn More

- Full documentation: See `README.md`
- Test scenarios: See `TEST_GUIDE.md`
- Source code: See `armor_workflow.py` and `fastapi_endpoint.py`
- ArmorIQ SDK: https://docs.armoriq.ai/docs

---

## ⚡ 30-Second Summary

1. Activate virtual env: `code_warriors\Scripts\activate`
2. Run: `python -m uvicorn fastapi_endpoint:app --port 8000`
3. Test: `curl http://localhost:8000/health`
4. Analyze: `curl -X POST http://localhost:8000/analyze/text -H "Content-Type: application/json" -d '{"text_content":"test","mode":"COMMAND"}'`
5. View results: Check response JSON

---

**Ready to secure your data! 🔒**

For detailed guidance, see:
- `README.md` - Complete documentation
- `TEST_GUIDE.md` - Comprehensive test scenarios
- `armor_workflow.py` - Agent implementation
- `fastapi_endpoint.py` - API endpoints
