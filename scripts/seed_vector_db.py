#!/usr/bin/env python3
"""
LexiMini AI — Vector Database Seeding Utility
Reads data/indian_laws_2026.csv and populates Qdrant Vector DB collection.
"""

import os
import pandas as pd
from typing import List, Dict, Any

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "indian_laws_2026.csv")

def load_dataset(data_path: str = DATA_PATH) -> pd.DataFrame:
    if not os.path.exists(data_path):
        print(f"[Error] Dataset file not found at: {data_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(data_path)
    print(f"[Info] Successfully loaded {len(df)} rows from {data_path}")
    return df

def seed_qdrant(df: pd.DataFrame):
    if df.empty:
        print("[Warning] Empty dataset provided for seeding.")
        return

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import VectorParams, Distance, PointStruct
    except ImportError:
        print("[Note] qdrant_client not installed locally. Seeding skipped for standalone python environment.")
        return

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    collection_name = "indian_laws"

    try:
        client = QdrantClient(host=host, port=port, timeout=5.0)
        collections = [c.name for c in client.get_collections().collections]

        if collection_name not in collections:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"[Success] Created Qdrant collection: '{collection_name}'")

        points = []
        for idx, row in df.iterrows():
            payload = {
                "act": str(row.get("act_name", "")),
                "section": str(row.get("section", "")),
                "content": str(row.get("key_provisions", "")),
                "authority": str(row.get("enforcement_authority", "")),
            }
            # Simulated 384-dim dummy vector for initial indexing test
            dummy_vector = [0.01 * (i % 10) for i in range(384)]
            points.append(PointStruct(id=idx + 1, vector=dummy_vector, payload=payload))

        client.upsert(collection_name=collection_name, points=points)
        print(f"[Success] Seeded {len(points)} legal records into Qdrant collection '{collection_name}'.")

    except Exception as e:
        print(f"[Note] Could not connect to Qdrant at {host}:{port} ({e}). (Ensure Docker containers are running).")

if __name__ == "__main__":
    print("=== LexiMini AI — Vector Database Seeding Utility ===")
    dataset_df = load_dataset()
    seed_qdrant(dataset_df)
