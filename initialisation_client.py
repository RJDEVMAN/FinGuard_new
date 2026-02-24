# Imports
from armoriq_sdk import ArmorIQClient
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize the ArmorIQ client with environment variables
client1 = ArmorIQClient(
    api_key=os.getenv("ARMORIQ_API_KEY"),
    user_id=os.getenv("ARMORIQ_USER_ID"),
    agent_id=os.getenv("ARMORIQ_AGENT_ID"),
    timeout=60,
    max_retries=5
)

# Testing the client
if client1:
    print("Client initialized successfully!")
else:
    print("Failed to initialise the client.")