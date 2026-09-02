import pandas as pd
import os
from qdrant_client.http import models
from services.rag_engine.qdrant_client import get_qdrant_client, init_qdrant_collection, COLLECTION_NAME, VECTOR_SIZE
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/indian_laws_2026.csv")

def ingest_laws():
    init_qdrant_collection()
    client = get_qdrant_client()

    if not os.path.exists(DATA_PATH):
        print(f"Dataset not found at {DATA_PATH}")
        return 0

    df = pd.read_csv(DATA_PATH)
    points = []

    for idx, row in df.iterrows():
        # Generate dummy normalized dense vector of size 384 for indexing
        vec = np.random.randn(VECTOR_SIZE).astype(np.float32)
        vec /= np.linalg.norm(vec)

        payload = {
            "act": str(row.get("act_name", "Indian Law")),
            "section": str(row.get("section", "Provision")),
            "content": str(row.get("key_provisions", "")),
            "authority": str(row.get("enforcement_authority", "Court/Police"))
        }

        points.append(models.PointStruct(
            id=idx + 1,
            vector=vec.tolist(),
            payload=payload
        ))

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Successfully ingested {len(points)} legal records into Qdrant collection '{COLLECTION_NAME}'.")
        return len(points)
    return 0

if __name__ == "__main__":
    ingest_laws()
