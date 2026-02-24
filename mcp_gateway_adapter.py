"""
MCP Gateway Adapter
Intercepts ArmorIQ SDK MCP calls and routes them to unified gateway
"""

import logging
import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MCPGatewayAdapter:
    """Adapter to route MCP invocations to unified gateway"""
    
    def __init__(self, gateway_url: Optional[str] = None):
        """
        Initialize adapter with gateway URL
        
        Args:
            gateway_url: URL to unified MCP gateway (default: http://localhost:8001)
        """
        self.gateway_url = gateway_url or os.getenv("MCP_GATEWAY_URL", "http://localhost:8001")
        self.invoke_endpoint = f"{self.gateway_url}/invoke"
        self.health_endpoint = f"{self.gateway_url}/health"
        self.logger = logger
        
        self.logger.info(f"MCP Gateway Adapter initialized with gateway: {self.gateway_url}")
    
    def health_check(self) -> bool:
        """Check if MCP gateway is accessible"""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                self.logger.info("✅ MCP Gateway is healthy")
                return True
            else:
                self.logger.warning(f"❌ MCP Gateway health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ MCP Gateway unreachable: {str(e)}")
            return False
    
    def invoke(self, 
               mcp: str,
               action: str,
               params: Dict[str, Any],
               intent_token: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Invoke MCP action through unified gateway
        
        Args:
            mcp: MCP name (fraud, risk, compliance, memory)
            action: Action to perform
            params: Action parameters
            intent_token: Intent token for authorization (optional)
            
        Returns:
            Response from MCP action
        """
        try:
            # Map mcp names to agent types
            agent_type_map = {
                "fraud-mcp": "fraud",
                "fraud_mcp": "fraud",
                "fraud": "fraud",
                "risk-mcp": "risk",
                "risk_mcp": "risk",
                "risk": "risk",
                "compliance-mcp": "compliance",
                "compliance_mcp": "compliance",
                "compliance": "compliance",
                "memory-mcp": "memory",
                "memory_mcp": "memory",
                "memory": "memory",
            }
            
            agent_type = agent_type_map.get(mcp.lower(), mcp.lower())
            
            # Convert IntentToken to JSON-serializable format
            intent_token_data = None
            if intent_token:
                try:
                    # If it's already a dict, use it
                    if isinstance(intent_token, dict):
                        intent_token_data = intent_token
                    else:
                        # If it's an IntentToken object, convert to string
                        intent_token_data = str(intent_token)
                        self.logger.debug(f"Converted IntentToken to string: {intent_token_data[:50]}...")
                except Exception as e:
                    self.logger.warning(f"Could not serialize intent_token: {str(e)}")
                    intent_token_data = None
            
            # Prepare gateway request (with JSON-serializable metadata only)
            gateway_request = {
                "agent_type": agent_type,
                "action": action,
                "payload": params,
                "metadata": {
                    "requested_by": "orchestrator",
                    "has_intent_token": intent_token is not None
                }
            }
            
            self.logger.info(f"Invoking MCP: {agent_type}/{action}")
            self.logger.debug(f"Request payload: {gateway_request}")
            
            # Call unified gateway
            response = requests.post(
                self.invoke_endpoint,
                json=gateway_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"✅ {agent_type}/{action} executed successfully")
                return {
                    "success": True,
                    "result": result.get("result", {}),
                    "status": result.get("status", "success"),
                    "error": None
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"❌ MCP invocation failed: {error_msg}")
                return {
                    "success": False,
                    "result": {},
                    "status": "error",
                    "error": error_msg
                }
        
        except requests.exceptions.Timeout:
            error_msg = f"MCP invocation timeout after 30 seconds"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "result": {},
                "status": "error",
                "error": error_msg
            }
        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to MCP Gateway at {self.gateway_url}"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "result": {},
                "status": "error",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "result": {},
                "status": "error",
                "error": error_msg
            }


# Global adapter instance
_gateway_adapter = None


def get_adapter(gateway_url: Optional[str] = None) -> MCPGatewayAdapter:
    """Get or create global gateway adapter"""
    global _gateway_adapter
    if _gateway_adapter is None:
        _gateway_adapter = MCPGatewayAdapter(gateway_url)
    return _gateway_adapter


def invoke_mcp(mcp: str,
               action: str,
               params: Dict[str, Any],
               intent_token: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to invoke MCP through adapter
    """
    adapter = get_adapter()
    return adapter.invoke(mcp, action, params, intent_token)
