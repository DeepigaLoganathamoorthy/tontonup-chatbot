import json, os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("URL")
API_KEY = os.getenv("API_KEY")
JSON_PATH = "./data/faq_with_embeddings.json"

client = QdrantClient(url=URL, api_key=API_KEY)

client.recreate_collection(
    collection_name="faq_collection",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

points = []
for i, item in enumerate(data):
    points.append(
        PointStruct(
            id=i,
            vector=item["vector"],
            payload={
                "content": item["content"],
                "metadata": item["metadata"]
            }
        )
    )

client.upsert(collection_name="faq_collection", points=points)
print(f"✅ Success! Uploaded {len(points)} items to Qdrant Cloud.")