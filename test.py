from qdrant_client import QdrantClient

# COPY THESE EXACTLY FROM YOUR STRMLIT SECRETS
import os
from dotenv import load_dotenv
load_dotenv()
URL = os.getenv("URL")
KEY = os.getenv("API_KEY")

client = QdrantClient(url=URL, api_key=KEY)

try:
    collections = client.get_collections()
    print("✅ CONNECTION SUCCESSFUL!")
    print("Found these collections:", [c.name for c in collections.collections])
except Exception as e:
    print("❌ CONNECTION FAILED!")
    print(f"Error details: {e}")