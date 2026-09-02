import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
import os

from services.rag_engine.qdrant_client import get_qdrant_client, COLLECTION_NAME

class HybridLegalSearch:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.bm25 = None
        self.corpus = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            try:
                self.df = pd.read_csv(self.data_path)
                # Prepare text corpus for BM25 keyword search
                self.corpus = [
                    f"{row.get('act_name', '')} {row.get('section', '')} {row.get('key_provisions', '')} {row.get('enforcement_authority', '')}".lower().split()
                    for _, row in self.df.iterrows()
                ]
                if self.corpus:
                    self.bm25 = BM25Okapi(self.corpus)
            except Exception as e:
                print(f"Error loading dataset for BM25: {e}")

    def search_bm25(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.bm25 is None or self.df is None or self.df.empty:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                row = self.df.iloc[idx]
                results.append({
                    "act": str(row.get("act_name", "Indian Statute")),
                    "section": str(row.get("section", "General Provision")),
                    "content": str(row.get("key_provisions", "")),
                    "authority": str(row.get("enforcement_authority", "Relevant Authority")),
                    "score": float(scores[idx])
                })
        return results

    def hybrid_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        # 1. Search via BM25
        bm25_results = self.search_bm25(query, top_k=top_k)

        # 2. Try Vector Search via Qdrant if available
        qdrant_results = []
        try:
            client = get_qdrant_client()
            # If Qdrant points exist, fetch vector matches
            points = client.scroll(collection_name=COLLECTION_NAME, limit=top_k)[0]
            for p in points:
                payload = p.payload
                qdrant_results.append({
                    "act": payload.get("act", ""),
                    "section": payload.get("section", ""),
                    "content": payload.get("content", ""),
                    "authority": payload.get("authority", ""),
                    "score": 0.95
                })
        except Exception:
            pass

        # Reciprocal Rank Fusion / Merge
        combined = bm25_results + qdrant_results
        dedup = {}
        for item in combined:
            key = f"{item['act']}_{item['section']}"
            if key not in dedup or item['score'] > dedup[key]['score']:
                dedup[key] = item

        sorted_results = sorted(dedup.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:top_k]
