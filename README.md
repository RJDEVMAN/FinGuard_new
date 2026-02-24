# FinGuard Multi-Agent Security Orchestration System

A comprehensive financial defense system powered by ArmorIQ SDK with hierarchical multi-agent architecture and policy-enforced delegation.

## 📋 System Overview

FinGuard implements a **4-tier multi-agent pipeline** that analyzes media inputs for fraud, assesses risk, validates compliance, and maintains complete audit trails.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT ANALYSIS PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT (Media: Text/Image/Video/Audio/Document)                │
│     │                                                           │
│     ▼                                                           │
│  ┌──────────────────────________________────────────┐          │
│  │ STAGE 1: FRAUD AGENT (Primary Analysis)         │          │
│  │ ├─ Detect deepfakes & synthetic media           │          │
│  │ ├─ Identify AI-generated content anomalies      │          │
│  │ ├─ Policy: allow=["fraud_agent/*"]              │          │
│  │ └─ Decision: SAFE | FRAUD | CHECK-REQUIRED     │          │
│  └──────────────┬─────────────────────────────────┘          │
│                 │ [Escalate if FRAUD detected]                │
│                 ▼                                              │
│  ┌──────────────────────________________────────────┐          │
│  │ STAGE 2: RISK AGENT (Risk Assessment)           │          │
│  │ ├─ Evaluate threat severity                     │          │
│  │ ├─ Calculate risk score (0-100)                 │          │
│  │ ├─ Policy: allow=["risk_agent/*"]               │          │
│  │ └─ Decision: Escalate if score > 70             │          │
│  └──────────────┬─────────────────────────────────┘          │
│                 │ [Escalate if HIGH RISK]                    │
│                 ▼                                              │
│  ┌──────────────────────________________────────────┐          │
│  │ STAGE 3: COMPLIANCE AGENT (Regulatory Check)    │          │
│  │ ├─ Validate AML/KYC requirements                │          │
│  │ ├─ Check regulatory compliance                  │          │
│  │ ├─ Policy: allow=["compliance_agent/*"]         │          │
│  │ └─ Decision: Violations? | Required Actions?    │          │
│  └──────────────┬─────────────────────────────────┘          │
│                 │ [Always proceed]                            │
│                 ▼                                              │
│  ┌──────────────────────________________────────────┐          │
│  │ STAGE 4: MEMORY AGENT (Audit & Finalization)    │          │
│  │ ├─ Consolidate all findings                     │          │
│  │ ├─ Generate complete audit trail                │          │
│  │ ├─ Log blocked actions & errors                 │          │
│  │ └─ Policy: allow=["memoryupdate_agent/*"]       │          │
│  └──────────────┬─────────────────────────────────┘          │
│                 │                                              │
│                 ▼                                              │
│  ┌──────────────────────────────────────────────────┐          │
│  │        FINAL DECISION & COMPLETE REPORT         │          │
│  │  SAFE_APPROVED | REQUIRE_MANUAL_REVIEW |        │          │
│  │  FRAUD_DETECTED_MONITOR | BLOCK_IMMEDIATELY |   │          │
│  │  ESCALATE_TO_AUTHORITIES                        │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Architecture

### Four Specialized Agents

#### 1. **FraudAgent** (Primary)
- Analyzes media for fraud indicators
- Detects deepfakes and synthetic content
- Identifies AI-generated anomalies
- **Policy**: `allow: ["fraud_agent/*"]` | `deny: ["risk_agent/*", "compliance_agent/*", "memoryupdate_agent/*"]`
- **Decision**: SAFE | FRAUD | CHECK-REQUIRED

#### 2. **RiskAgent** (Secondary)
- Assesses threat severity and impact
- Calculates risk scores (0-100)
- Provides mitigation recommendations
- **Policy**: `allow: ["risk_agent/*"]` | `deny: ["fraud_agent/*", "compliance_agent/*", "memoryupdate_agent/*"]`
- **Decision**: Escalate based on risk thresholds

#### 3. **ComplianceAgent** (Tertiary)
- Validates regulatory requirements (AML/KYC)
- Checks data protection compliance
- Flags violations and required actions
- **Policy**: `allow: ["compliance_agent/*"]` | `deny: ["fraud_agent/*", "risk_agent/*", "memoryupdate_agent/*"]`
- **Decision**: Violations? | Required Actions?

#### 4. **MemoryUpdateAgent** (Final)
- Consolidates all agent findings
- Generates complete audit trail
- Logs blocked actions and errors
- Acts as central audit logger
- **Policy**: `allow: ["memoryupdate_agent/*"]` | `deny: ["fraud_agent/*", "risk_agent/*", "compliance_agent/*"]`

### Key Features

✅ **Policy Enforcement**
- Each agent has explicit allow/deny rules
- Cryptographic verification via ArmorIQ
- Actions blocked by policy are logged and reported

✅ **Delegation Mechanism**
- Agents delegate to next agent with restricted permissions
- Trusted token-based authority transfer
- Sub-agents can only execute allowed actions

✅ **Multi-Media Support**
- **Text**: Email, messages, documents
- **Image**: Photos, screenshots
- **Video**: Video files, stream recordings
- **Audio**: Voice messages, recordings
- **Document**: PDF, DOC, XLS files

✅ **Dual Mode Execution**
- **ASK Mode**: Interactive - agents ask user confirmation at decision points
- **COMMAND Mode**: Autonomous - agents make decisions automatically

✅ **Complete Audit Trail**
- Every action logged with timestamp
- Policy violations recorded
- Errors captured and reported
- Final report includes all decisions and reasoning

## 📁 File Structure

```
Code_warriors/
├── armor_workflow.py          # Main multi-agent orchestration system
├── fastapi_endpoint.py         # REST API endpoints for analysis
├── initialisation_client.py    # ArmorIQ SDK client initialization
├── requirements.txt            # Python dependencies
├── fingard_audit.log           # Audit trail logs (generated)
├── fingard_final_report.json   # Final analysis report (generated)
└── README.md                   # This file
```

## 🚀 Installation & Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv code_warriors
code_warriors\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create `.env` file:
```env
ARMORIQ_API_KEY=your_api_key_here
ARMORIQ_USER_ID=your_user_id_here
ARMORIQ_AGENT_ID=fraud_agent
```

### 3. Verify Installation
```bash
python initialisation_client.py
# Should print: "Client initialized successfully!"
```

## 💻 Usage

### CLI Mode (armor_workflow.py)

```bash
python armor_workflow.py

# Interactive prompts:
# Enter your input (or file path for media): [your_input]
# Media type (text/image/audio/video/document): [choice]
# Mode (ASK/COMMAND): [choice]
```

### API Mode (fastapi_endpoint.py)

```bash
# Start API server
python -m uvicorn fastapi_endpoint:app --reload --port 8000

# API will be available at: http://localhost:8000
# Documentation: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 🔍 Testing Scenarios

### Test Case 1: Detect Fraud in Text
```python
# CLI
Input: "Check this document - it looks tampered"
Media Type: text
Mode: COMMAND

# Expected Result: FRAUD detected with detailed findings
```

### Test Case 2: Safe Content
```python
# CLI
Input: "Normal transaction approved"
Media Type: text
Mode: ASK

# Expected Result: SAFE_APPROVED
```

### Test Case 3: Image Deepfake
```bash
# API - Image Upload
curl -X POST "http://localhost:8000/analyze/image" \
  -F "file=@suspicious_image.jpg" \
  -F "mode=COMMAND"

# Expected Result: FRAUD_DETECTED with deepfake indicators
```

### Test Case 4: Batch Analysis
```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"content": "Text to check", "media_type": "TEXT"},
      {"content": "Another check", "media_type": "TEXT"}
    ],
    "mode": "COMMAND"
  }'
```

### Test Case 5: Policy Violation Scenario
When an agent tries to execute an action outside its policy:
```
✗ Action blocked by policy
├─ Agent: FraudAgent
├─ Attempted Action: risk_assessment (DENIED)
├─ Reason: Action not in allow list
└─ Status: Logged and escalated to next agent with context
```

## 📊 API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /info` - System information
- `GET /` - API overview

### Analysis Endpoints
- `POST /analyze/text` - Text analysis
- `POST /analyze/image` - Image analysis
- `POST /analyze/video` - Video analysis
- `POST /analyze/audio` - Audio analysis
- `POST /analyze/document` - Document analysis
- `POST /analyze/batch` - Batch analysis
- `POST /analyze/custom` - Custom analysis

### Report
- `GET /report/{session_id}` - Retrieve specific session report

## 📝 Request/Response Examples

### Text Analysis Request
```json
POST /analyze/text
{
  "text_content": "Verify this payment transaction",
  "mode": "COMMAND",
  "metadata": {
    "source": "email",
    "priority": "high"
  }
}
```

### Response Structure
```json
{
  "session_id": "SESSION_20260224120000000123",
  "timestamp": "2026-02-24T12:00:00.000000",
  "mode": "COMMAND",
  "media_type": "text",
  "final_decision": "SAFE_APPROVED",
  "agent_reports": {
    "fraud_agent": {
      "agent": "FraudAgent",
      "decision": "SAFE",
      "detection_data": {...},
      "anomaly_data": {...}
    }
  },
  "audit_trail": [
    {
      "timestamp": "2026-02-24T12:00:00.000000",
      "agent": "FraudAgent",
      "action": "DEEPFAKE_DETECTION",
      "status": "EXECUTED",
      "details": {...}
    }
  ],
  "blocked_actions": [],
  "errors": []
}
```

## 🔐 Security Features

### Policy-Enforced Delegation
- Each agent has explicit permissions
- Delegated tokens are cryptographically bound
- Sub-agents receive restricted access tokens
- Attempts to exceed permissions are logged

### Cryptographic Verification
- Plans are validated before execution
- Intent tokens signed with Ed25519
- Actions must be in the captured plan
- Unauthorized actions are rejected

### Audit Trail
- Every action logged with timestamp
- All policy violations recorded
- Errors captured with context
- Complete session history maintained

## 📋 Agent Decision Flow

```
┌─────────────────────────────────────────┐
│ FRAUD AGENT DECISION                    │
├─────────────────────────────────────────┤
│                                         │
│ confidence > 0.8 OR anomalies > 5       │
│         ↓                               │
│   DECISION: FRAUD                       │
│         ↓                               │
│   escalate_to_risk = TRUE               │
│                                         │
│ confidence 0.5-0.8 OR anomalies 2-5     │
│         ↓                               │
│   DECISION: CHECK-REQUIRED              │
│         ↓                               │
│   escalate_to_risk = TRUE               │
│                                         │
│ confidence < 0.5 AND anomalies < 2      │
│         ↓                               │
│   DECISION: SAFE                        │
│         ↓                               │
│   escalate_to_risk = FALSE              │
│                                         │
└─────────────────────────────────────────┘

If escalate_to_risk = TRUE
              ↓
┌─────────────────────────────────────────┐
│ RISK AGENT DECISION                     │
├─────────────────────────────────────────┤
│                                         │
│ risk_score > 80     → BLOCK_IMMEDIATELY │
│ risk_score 70-80    → ESCALATE_TO_COMPLIANCE
│ risk_score < 70     → FRAUD_DETECTED_MONITOR
│                                         │
│ If escalate_to_compliance = TRUE        │
│         ↓                               │
├─────────────────────────────────────────┤
│ COMPLIANCE AGENT                        │
├─────────────────────────────────────────┤
│                                         │
│ violations.count() > 0                  │
│         ↓                               │
│   ESCALATE_TO_AUTHORITIES               │
│                                         │
│ violations.count() = 0                  │
│         ↓                               │
│   FRAUD_DETECTED_MONITOR                │
│                                         │
└─────────────────────────────────────────┘
```

## 🔧 Configuration

### Execution Modes

**ASK Mode** (Interactive)
```python
mode = "ASK"
# Agent will prompt user for confirmation at each critical decision
# User can override agent decisions
```

**COMMAND Mode** (Autonomous)
```python
mode = "COMMAND"
# Agent makes decisions autonomously
# No user interaction required
```

### Policy Customization

Each agent's policy can be customized:
```python
policy = {
    "allow": ["mcp_pattern/*"],           # Allowed actions
    "deny": ["restricted_agent/*"],        # Denied actions
    "allowed_tools": ["tool1", "tool2"],   # Whitelisted tools
    "rate_limit": 100,                     # Requests per hour
    "ip_whitelist": ["10.0.0.0/8"],        # Allowed IPs
    "time_restrictions": {
        "allowed_hours": [9, 10, 11, ...],
        "allowed_days": ["Monday", "Tuesday", ...]
    }
}
```

## 📊 Output Files

### fingard_audit.log
Real-time logging of all agent operations:
```
2026-02-24 12:00:00,000 - FraudAgent - INFO - Starting fraud analysis for text
2026-02-24 12:00:00,100 - FraudAgent - INFO - Plan captured successfully
2026-02-24 12:00:00,200 - FraudAgent - INFO - Intent token generated with policy enforcement
2026-02-24 12:00:00,300 - FraudAgent - INFO - Action 'detect_deepfakes' executed successfully
```

### fingard_final_report.json
Comprehensive analysis report with all findings and decisions.

## 🐛 Error Handling

Errors are handled at multiple levels:

1. **Plan Level**: Invalid plan structure rejected
2. **Token Level**: Invalid/expired tokens rejected
3. **Invocation Level**: Unauthorized actions blocked
4. **Delegation Level**: Delegation failures logged
5. **Orchestration Level**: Pipeline errors captured

All errors are:
- Logged with full context
- Included in audit trail
- Reported in final output
- Passed to next agent for awareness

## 🎯 Testing Workflow

### Recommended Test Order

1. **Basic Functionality**
   - Test with simple text input in both modes
   - Verify decision making logic

2. **Media Types**
   - Test each media type (image, video, audio, document)
   - Verify encoding/decoding

3. **Policy Enforcement**
   - Trigger actions outside agent's policy
   - Verify blocking and logging

4. **Delegation**
   - Follow decision flow across all agents
   - Verify delegation tokens work

5. **Error Scenarios**
   - Invalid inputs
   - Network failures
   - Edge cases

6. **Batch Processing**
   - Multiple inputs in single request
   - Error handling in batch

7. **Performance**
   - Large media files
   - Response times
   - Concurrent requests

## 📈 Performance Considerations

- **Plan Capture**: ~100-200ms
- **Token Generation**: ~50-100ms
- **Action Invocation**: ~200-500ms per action
- **Total Pipeline**: ~1-3 seconds for complete analysis

Optimization tips:
- Batch similar requests
- Cache policy tokens
- Use appropriate timeout values
- Monitor API response times

## 🔄 Future Enhancements

- Database storage for session history
- Dashboard for monitoring
- Advanced analytics and reporting
- Machine learning for decision improvement
- Real-time streaming analysis
- Custom MCP integration
- Advanced delegation chains
- Multi-language support

## 📚 References

- [ArmorIQ SDK Documentation](https://docs.armoriq.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)

## 📞 Support

For issues or questions:
1. Check `fingard_audit.log` for detailed errors
2. Review `fingard_final_report.json` for complete analysis
3. Consult ArmorIQ SDK documentation
4. Check FastAPI documentation for API issues

## 📄 License

This project is part of the FinGuard security system.

---

**Version**: 1.0.0  
**Last Updated**: February 24, 2026  
**Status**: Production Ready
