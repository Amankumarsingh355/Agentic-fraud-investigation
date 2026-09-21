"""
Hybrid Case Memory Retrieval Engine (Static + Dynamic Graph Memory)
Combines Graph Structural Linkages + Dense Vector Similarity over both
historical closed cases (months 1-4) and dynamically persisted cases.
Strictly isolates evaluation benchmark cases from retrieval.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))
from graph.load_vector_store import VectorRetriever

MEMORY_FILE = os.path.join("data", "dynamic_case_memory.json")

class SimilarCasesEngine:
    def __init__(self, data_path=os.path.join("data", "closed_cases_history.csv"), memory_file: str = MEMORY_FILE, retriever=None):
        self.retriever = retriever or VectorRetriever()
        self.memory_file = memory_file
        self.df_cc = pd.read_csv(data_path)
        self.case_lookup = self.df_cc.set_index("case_id").to_dict(orient="index")
        
    def _load_dynamic_memory(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load dynamic memory in SimilarCasesEngine: {e}")
        return {}

    def find_similar_cases(
        self,
        query_text: str,
        target_pattern: str = None,
        target_exposure: float = 0.0,
        target_device: str = None,
        target_customer: str = None,
        top_k: int = 3,
        alpha: float = 0.5 # Weight for vector vs graph similarity
    ):
        """
        Computes hybrid similarity:
        Score = alpha * VectorSimilarity + (1 - alpha) * GraphStructuralSimilarity
        Searches across both historical static cases and newly resolved dynamic cases.
        """
        dynamic_memory = self._load_dynamic_memory()
        candidates = {}

        # 1. Vector semantic search over static historical cases
        vector_results = self.retriever.search(
            query=query_text,
            top_k=top_k * 5,
            doc_type="closed_case_memory"
        )
        
        for vr in vector_results:
            cid = vr['metadata']['case_id']
            if cid not in self.case_lookup:
                continue
            candidates[cid] = {
                "case_id": cid,
                "is_dynamic": False,
                "vector_score": vr['score'],
                "metadata": vr['metadata'],
                "notes": vr['content_snippet']
            }
            
        # 2. Check Dynamic Memory cases (Persisted from agent runs)
        q_vec = self.retriever.vectorizer.transform([query_text])
        for cid, dcase in dynamic_memory.items():
            # STRICT ISOLATION: Never retrieve benchmark evaluation cases
            if dcase.get("is_benchmark") or dcase.get("namespace") == "eval_benchmark":
                continue
                
            # Vector score for dynamic case narrative
            narrative = dcase.get("narrative", "")
            d_vec = self.retriever.vectorizer.transform([f"{dcase.get('pattern')} {narrative}"])
            d_vscore = float(cosine_similarity(q_vec, d_vec)[0][0])
            
            candidates[cid] = {
                "case_id": cid,
                "is_dynamic": True,
                "vector_score": max(d_vscore, 0.25 if target_pattern and dcase.get("pattern") == target_pattern else 0.1),
                "metadata": {
                    "case_id": cid,
                    "customer_id": dcase.get("customer_id"),
                    "card_id": dcase.get("card_id"),
                    "outcome": dcase.get("outcome"),
                    "pattern": dcase.get("pattern"),
                    "exposure_usd": dcase.get("exposure_usd", 0.0),
                    "actions_taken": str(dcase.get("actions_taken", []))
                },
                "notes": narrative[:250] + "..." if len(narrative) > 250 else narrative
            }

        # 3. Structural scoring & hybrid ranking
        scored_cases = []
        for cid, cand in candidates.items():
            meta = cand["metadata"]
            c_pattern = meta.get("pattern", "")
            c_exposure = float(meta.get("exposure_usd", 0.0))
            is_dynamic = cand.get("is_dynamic", False)
            
            # Graph structural score components [0, 1]
            graph_score = 0.0
            
            # Pattern match
            if target_pattern and c_pattern == target_pattern:
                graph_score += 0.40
            elif not target_pattern:
                graph_score += 0.15
                
            # Entity match (Device or Customer)
            if target_customer and meta.get("customer_id") == target_customer:
                graph_score += 0.35
                
            # Exposure proximity
            if target_exposure > 0.0:
                diff = abs(c_exposure - target_exposure)
                if diff <= (0.3 * target_exposure):
                    graph_score += 0.30
                elif diff <= (0.7 * target_exposure):
                    graph_score += 0.15
                elif diff <= (1.2 * target_exposure):
                    graph_score += 0.05
            else:
                graph_score += 0.15
                
            # Proven outcome weighting
            if meta.get("outcome") == "confirmed_fraud":
                graph_score += 0.15
                
            # Dynamic recency boost (recently learned knowledge is prioritized)
            if is_dynamic:
                graph_score += 0.15

            # Blend scores
            v_score = cand["vector_score"]
            hybrid_score = (alpha * v_score) + ((1.0 - alpha) * graph_score)
            
            scored_cases.append({
                "case_id": cid,
                "is_dynamic": is_dynamic,
                "hybrid_score": round(hybrid_score, 4),
                "vector_score": round(v_score, 4),
                "graph_score": round(graph_score, 4),
                "pattern": c_pattern,
                "outcome": meta.get("outcome"),
                "exposure_usd": c_exposure,
                "actions_taken": meta.get("actions_taken"),
                "notes_snippet": cand["notes"]
            })
            
        # Sort by hybrid score descending
        scored_cases.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return scored_cases[:top_k]
