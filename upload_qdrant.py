import json, os
from dotenv import load_dotenv
import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()
URL = os.getenv("URL")
KEY = os.getenv("API_KEY")
JSON_PATH = "./data/faq_with_embeddings.json"
COLLECTION_NAME = "faq_collection"

client = QdrantClient(url=URL, api_key=KEY)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

sample_vector = faq_data[0]["vector"]
detected_size = len(sample_vector)
print(f"{detected_size}")

collections = client.get_collections().collections
exists = any(c.name == COLLECTION_NAME for c in collections)

if not exists:
    print(f"📦 Creating new collection: {COLLECTION_NAME}...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=detected_size, distance=Distance.COSINE)
    )
else:
    print(f"Collection '{COLLECTION_NAME}' already exists. Overwriting data...")

# 3. Prepare and Upload Points
points = [
    PointStruct(
        id=i,
        vector=item["vector"],
        payload={
            "content": item["content"],
            "metadata": item.get("metadata", {})
        }
    ) for i, item in enumerate(faq_data)
]

client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"SUCCESS: {len(points)} items uploaded with size {detected_size}!")