"""
FinGuard System Integration Test
Tests all components: MCP Gateway, FastAPI, Orchestrator
"""

import logging
import requests
import json
import time
import sys
from typing import Dict, Any
import subprocess
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinGuardTester:
    """Test FinGuard system integration"""
    
    def __init__(self):
        self.mcp_gateway_url = os.getenv("MCP_GATEWAY_URL", "http://localhost:8001")
        self.fastapi_url = "http://localhost:8000"
        self.test_results = []
    
    def test_mcp_gateway_health(self) -> bool:
        """Test MCP Gateway is accessible"""
        logger.info("=" * 70)
        logger.info("TEST 1: MCP Gateway Health Check")
        logger.info("=" * 70)
        
        try:
            response = requests.get(f"{self.mcp_gateway_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ MCP Gateway is healthy")
                logger.info(f"   Service: {data.get('service')}")
                logger.info(f"   Agents: {data.get('agents')}")
                logger.info(f"   Version: {data.get('version')}")
                self.test_results.append(("MCP Gateway Health", True, None))
                return True
            else:
                logger.error(f"❌ MCP Gateway health check returned {response.status_code}")
                self.test_results.append(("MCP Gateway Health", False, f"Status {response.status_code}"))
                return False
        
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Cannot connect to MCP Gateway at {self.mcp_gateway_url}")
            logger.error("   Ensure mcp_gateway.py is running: python -m uvicorn mcp_gateway:app --port 8001")
            self.test_results.append(("MCP Gateway Health", False, "Connection refused"))
            return False
        except Exception as e:
            logger.error(f"❌ Error testing MCP Gateway: {str(e)}")
            self.test_results.append(("MCP Gateway Health", False, str(e)))
            return False
    
    def test_mcp_fraud_agent(self) -> bool:
        """Test Fraud MCP Agent invocation"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 2: Fraud MCP Agent Invocation")
        logger.info("=" * 70)
        
        try:
            payload = {
                "agent_type": "fraud",
                "action": "detect_deepfakes",
                "payload": {
                    "input": "test_data",
                    "media_type": "image"
                }
            }
            
            logger.info(f"Sending request to MCP Gateway: POST /invoke")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.mcp_gateway_url}/invoke",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Fraud Agent executed successfully")
                logger.info(f"   Status: {data.get('status')}")
                logger.info(f"   Agent: {data.get('agent_type')}")
                logger.info(f"   Action: {data.get('action')}")
                self.test_results.append(("Fraud Agent Invocation", True, None))
                return True
            else:
                error = response.text
                logger.error(f"❌ Fraud Agent invocation failed: {response.status_code}")
                logger.error(f"   Error: {error}")
                self.test_results.append(("Fraud Agent Invocation", False, error))
                return False
        
        except Exception as e:
            logger.error(f"❌ Error testing Fraud Agent: {str(e)}")
            self.test_results.append(("Fraud Agent Invocation", False, str(e)))
            return False
    
    def test_mcp_all_agents(self) -> bool:
        """Test all MCP agents"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 3: All MCP Agents")
        logger.info("=" * 70)
        
        agents = {
            "fraud": "detect_deepfakes",
            "risk": "assess_risk_level",
            "compliance": "verify_compliance",
            "memory": "consolidate_findings"
        }
        
        all_passed = True
        
        for agent, action in agents.items():
            try:
                payload = {
                    "agent_type": agent,
                    "action": action,
                    "payload": {
                        "input": "test_data",
                        "session_id": "TEST_SESSION_001"
                    }
                }
                
                response = requests.post(
                    f"{self.mcp_gateway_url}/invoke",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ {agent.upper()} agent - {action}: SUCCESS")
                else:
                    logger.error(f"❌ {agent.upper()} agent - {action}: FAILED ({response.status_code})")
                    all_passed = False
            
            except Exception as e:
                logger.error(f"❌ {agent.upper()} agent - {action}: ERROR - {str(e)}")
                all_passed = False
        
        self.test_results.append(("All MCP Agents", all_passed, None))
        return all_passed
    
    def test_fastapi_health(self) -> bool:
        """Test FastAPI Backend health"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 4: FastAPI Backend Health Check")
        logger.info("=" * 70)
        
        try:
            response = requests.get(f"{self.fastapi_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ FastAPI Backend is healthy")
                logger.info(f"   Status: {data.get('status')}")
                self.test_results.append(("FastAPI Health", True, None))
                return True
            else:
                logger.error(f"❌ FastAPI health check returned {response.status_code}")
                self.test_results.append(("FastAPI Health", False, f"Status {response.status_code}"))
                return False
        
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Cannot connect to FastAPI at {self.fastapi_url}")
            logger.error("   Ensure fastapi_endpoint.py is running: python -m uvicorn fastapi_endpoint:app --port 8000")
            self.test_results.append(("FastAPI Health", False, "Connection refused"))
            return False
        except Exception as e:
            logger.error(f"❌ Error testing FastAPI: {str(e)}")
            self.test_results.append(("FastAPI Health", False, str(e)))
            return False
    
    def test_fastapi_text_analysis(self) -> bool:
        """Test FastAPI text analysis endpoint"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 5: FastAPI Text Analysis")
        logger.info("=" * 70)
        
        try:
            payload = {
                "text_content": "Send crypto to offshore account urgently",
                "mode": "COMMAND"
            }
            
            logger.info(f"Sending request to FastAPI: POST /analyze/text")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.fastapi_url}/analyze/text",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Text Analysis executed successfully")
                logger.info(f"   Session ID: {data.get('session_id')}")
                logger.info(f"   Decision: {data.get('decision')}")
                self.test_results.append(("FastAPI Text Analysis", True, None))
                return True
            else:
                error = response.text
                logger.error(f"❌ Text analysis failed: {response.status_code}")
                logger.error(f"   Error: {error}")
                self.test_results.append(("FastAPI Text Analysis", False, error))
                return False
        
        except Exception as e:
            logger.error(f"❌ Error testing text analysis: {str(e)}")
            self.test_results.append(("FastAPI Text Analysis", False, str(e)))
            return False
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST SUMMARY")
        logger.info("=" * 70)
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result, error in self.test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
            if error:
                logger.info(f"         Error: {error}")
        
        logger.info("=" * 70)
        logger.info(f"Results: {passed}/{total} tests passed")
        logger.info("=" * 70)
        
        return passed == total
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        logger.info("\n")
        logger.info("╔════════════════════════════════════════════════════════════════╗")
        logger.info("║    FinGuard System Integration Test Suite                      ║")
        logger.info("╚════════════════════════════════════════════════════════════════╝")
        
        tests = [
            self.test_mcp_gateway_health,
            self.test_mcp_fraud_agent,
            self.test_mcp_all_agents,
            self.test_fastapi_health,
            self.test_fastapi_text_analysis,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed: {str(e)}")
        
        success = self.print_summary()
        
        return success


def main():
    """Main entry point"""
    tester = FinGuardTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
