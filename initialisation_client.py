# Imports
from armoriq_sdk import ArmorIQClient
from dotenv import load_dotenv
import os
import logging
from mcp_gateway_adapter import MCPGatewayAdapter, get_adapter

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the ArmorIQ client with environment variables
client1 = ArmorIQClient(
    api_key=os.getenv("ARMORIQ_API_KEY"),
    user_id=os.getenv("ARMORIQ_USER_ID"),
    agent_id=os.getenv("ARMORIQ_AGENT_ID"),
    timeout=60,
    max_retries=5
)

# Initialize MCP Gateway Adapter
mcp_gateway = get_adapter(
    gateway_url=os.getenv("MCP_GATEWAY_URL", "http://localhost:8001")
)

# Override client1.invoke to use gateway adapter
_original_invoke = client1.invoke

def unified_invoke(mcp: str, action: str, intent_token: dict, params: dict):
    """
    Wrapper for client1.invoke that routes through unified MCP gateway
    """
    logger.info(f"Routing MCP call to unified gateway: {mcp}/{action}")
    return mcp_gateway.invoke(mcp, action, params, intent_token)

# Replace the invoke method
client1.invoke = unified_invoke

# Testing the client
if client1:
    logger.info("✅ Client initialized successfully!")
    
    # Test MCP Gateway connectivity
    if mcp_gateway.health_check():
        logger.info("✅ MCP Gateway is accessible")
    else:
        logger.warning("⚠️  MCP Gateway not accessible - ensure it's running on " + 
                      os.getenv("MCP_GATEWAY_URL", "http://localhost:8001"))
else:
    logger.error("❌ Failed to initialise the client.")