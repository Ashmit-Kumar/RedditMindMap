from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import uuid
from embedding_utils import get_embedding  # you will define this
import os
# Initialize client (use your real Qdrant host/API key if using cloud)
client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

def init_vector_db():
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
    except Exception as e:
        print("[!] Could not init collection:", str(e))

def push_to_vector_db(username: str, persona_text: str, metadata: dict):
    try:
        # Get vector embedding
        vector = get_embedding(persona_text)  # should return a list of floats

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={**metadata, "username": username}
        )

        client.upsert(collection_name=COLLECTION_NAME, points=[point])
        print(f"[✓] Pushed embedding for {username} to vector DB")

    except Exception as e:
        print(f"[X] Failed to push {username} to vector DB:", e)
