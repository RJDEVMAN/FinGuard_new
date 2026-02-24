# FastAPI Backend Testing Guide

## Quick Test Execution

### Run All Tests
```bash
python -m pytest test_fastapi_backend.py -v
```

### Run Specific Test Class
```bash
# Test only health endpoints
python -m pytest test_fastapi_backend.py::TestHealthEndpoints -v

# Test only text analysis
python -m pytest test_fastapi_backend.py::TestTextAnalysisEndpoint -v

# Test only workflow compliance
python -m pytest test_fastapi_backend.py::TestWorkflowCompliance -v
```

### Run Single Test
```bash
python -m pytest test_fastapi_backend.py::TestHealthEndpoints::test_health_check_success -v
```

### Additional Options
```bash
# Show print statements
python -m pytest test_fastapi_backend.py -v -s

# Stop after first failure
python -m pytest test_fastapi_backend.py -x

# Show local variables on failure
python -m pytest test_fastapi_backend.py -l

# Generate coverage report
python -m pytest test_fastapi_backend.py --cov=app --cov-report=html
```

---

## Test Categories

### 1. Health Endpoints Tests
- `test_health_check_success` - Verify health endpoint returns healthy status
- `test_system_info` - Verify system info endpoint returns metadata

### 2. Text Analysis Tests
- `test_analyze_text_safe` - Test SAFE classification
- `test_analyze_text_with_metadata` - Test with custom metadata

### 3. Media Analysis Tests
- `test_analyze_image` - Image file analysis
- `test_analyze_video` - Video file analysis
- `test_analyze_audio` - Audio file analysis
- `test_analyze_document` - Document file analysis

### 4. Batch Analysis Tests
- `test_batch_analysis_multiple_items` - Process multiple items in batch

### 5. Custom Analysis Tests
- `test_analyze_custom_request` - Custom request format handling

### 6. Report Retrieval Tests
- `test_get_report` - Report retrieval endpoint

### 7. Workflow Compliance Tests
- `test_4_tier_agent_pipeline` - Verify all 4 agents execute

### 8. Middleware Tests
- `test_cors_headers_present` - CORS configuration check

### 9. Error Handling Tests
- `test_empty_text_input` - Handle empty input
- `test_orchestrator_error` - Handle orchestrator failures

### 10. Response Format Tests
- `test_analysis_response_format` - Verify response structure

---

## API Endpoint Testing (Manual)

### Start Server
```bash
python -m uvicorn fastapi_endpoint:app --reload --port 8000
```

### Test Endpoints with curl

#### Health Check
```bash
curl http://localhost:8000/health
```

#### System Info
```bash
curl http://localhost:8000/info
```

#### Text Analysis
```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "text_content": "Regular bank transfer",
    "mode": "COMMAND"
  }'
```

#### Image Analysis
```bash
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@image.jpg" \
  -F "mode=COMMAND"
```

#### Batch Analysis
```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"input": "Test 1", "media_type": "TEXT"},
      {"input": "Test 2", "media_type": "TEXT"}
    ],
    "mode": "COMMAND"
  }'
```

#### Custom Analysis
```bash
curl -X POST http://localhost:8000/analyze/custom \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Custom input",
    "media_type": "TEXT",
    "mode": "COMMAND"
  }'
```

---

## Test Results Example

```
============================= test session starts ==============================
platform win32 -- Python 3.13.6, pytest-9.0.2, pluggy-1.6.0

test_fastapi_backend.py::TestHealthEndpoints::test_health_check_success PASSED [  6%]
test_fastapi_backend.py::TestHealthEndpoints::test_system_info PASSED [ 12%]
test_fastapi_backend.py::TestTextAnalysisEndpoint::test_analyze_text_safe PASSED [ 18%]
test_fastapi_backend.py::TestTextAnalysisEndpoint::test_analyze_text_with_metadata PASSED [ 25%]
test_fastapi_backend.py::TestMediaAnalysisEndpoints::test_analyze_image PASSED [ 31%]
test_fastapi_backend.py::TestMediaAnalysisEndpoints::test_analyze_video PASSED [ 37%]
test_fastapi_backend.py::TestMediaAnalysisEndpoints::test_analyze_audio PASSED [ 43%]
test_fastapi_backend.py::TestMediaAnalysisEndpoints::test_analyze_document PASSED [ 50%]
test_fastapi_backend.py::TestBatchAnalysisEndpoint::test_batch_analysis_multiple_items PASSED [ 56%]
test_fastapi_backend.py::TestCustomAnalysisEndpoint::test_analyze_custom_request PASSED [ 62%]
test_fastapi_backend.py::TestReportRetrievalEndpoint::test_get_report PASSED [ 68%]
test_fastapi_backend.py::TestWorkflowCompliance::test_4_tier_agent_pipeline PASSED [ 75%]
test_fastapi_backend.py::TestMiddleware::test_cors_headers_present PASSED [ 81%]
test_fastapi_backend.py::TestErrorHandling::test_empty_text_input PASSED [ 87%]
test_fastapi_backend.py::TestErrorHandling::test_orchestrator_error PASSED [ 93%]
test_fastapi_backend.py::TestResponseFormats::test_analysis_response_format PASSED [100%]

============================== 16 passed in 2.41s ===============================
```

---

## Troubleshooting

### Tests Not Found
```bash
# Make sure you're in the workspace root directory
cd c:\Users\Ruturaj Pandit\Desktop\Code_warriors

# Verify pytest is installed
python -m pip show pytest
```

### Import Errors
```bash
# Ensure virtual environment is activated
code_warriors\Scripts\activate

# Install required packages
python -m pip install -r requirements.txt
```

### Module Not Found
```bash
# Make sure app package is in the Python path
# Tests should be run from the workspace root:
python -m pytest test_fastapi_backend.py
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: FastAPI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest test_fastapi_backend.py -v
```

---

## Coverage Report

To generate a coverage report:
```bash
python -m pytest test_fastapi_backend.py --cov=app --cov-report=html --cov-report=term
```

This creates:
- HTML report in `htmlcov/` directory
- Terminal output with coverage percentages

---

## Performance Testing

### Load Testing with Apache Bench
```bash
# Start server first
python -m uvicorn fastapi_endpoint:app --reload --port 8000

# In another terminal:
ab -n 100 -c 10 http://localhost:8000/health
```

### Load Testing with Locust
```bash
# Install locust
pip install locust

# Create locustfile.py and run
locust -f locustfile.py --host=http://localhost:8000
```

---

## Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use pytest-watch for Auto-run
```bash
pip install pytest-watch
ptw test_fastapi_backend.py
```

### Use pytest-html for Report
```bash
pip install pytest-html
pytest test_fastapi_backend.py --html=report.html
```

---

**All tests passing! ✅**
