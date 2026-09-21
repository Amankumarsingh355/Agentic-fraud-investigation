"""
Hybrid Case Memory Retrieval Engine
Combines Graph Structural Linkages + Dense Vector Similarity over Closed Cases
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))
from graph.load_vector_store import VectorRetriever

class SimilarCasesEngine:
    def __init__(self, data_path=os.path.join("data", "closed_cases_history.csv")):
        self.retriever = VectorRetriever()
        self.df_cc = pd.read_csv(data_path)
        # Ensure fast lookup
        self.case_lookup = self.df_cc.set_index("case_id").to_dict(orient="index")
        
    def find_similar_cases(
        self,
        query_text: str,
        target_pattern: str = None,
        target_exposure: float = 0.0,
        target_channel: str = None,
        top_k: int = 3,
        alpha: float = 0.5 # Weight for vector vs graph similarity
    ):
        """
        Computes hybrid similarity:
        Score = alpha * VectorSimilarity + (1 - alpha) * GraphStructuralSimilarity
        """
        # 1. Vector semantic search over analyst notes
        vector_results = self.retriever.search(
            query=query_text,
            top_k=top_k * 5, # Fetch wider pool for re-ranking
            doc_type="closed_case_memory"
        )
        
        candidates = {}
        for vr in vector_results:
            cid = vr['metadata']['case_id']
            if cid not in self.case_lookup:
                continue
            candidates[cid] = {
                "case_id": cid,
                "vector_score": vr['score'],
                "metadata": vr['metadata'],
                "notes": vr['content_snippet']
            }
            
        # 2. Also query graph memory candidates matching pattern if pool is small
        if target_pattern and len(candidates) < top_k * 3:
            pattern_matches = self.df_cc[self.df_cc['pattern'] == target_pattern].head(10)
            for _, r in pattern_matches.iterrows():
                cid = str(r['case_id'])
                if cid not in candidates:
                    candidates[cid] = {
                        "case_id": cid,
                        "vector_score": 0.1, # baseline default
                        "metadata": {
                            "case_id": cid,
                            "pattern": r['pattern'],
                            "outcome": r['outcome'],
                            "exposure_usd": float(r['exposure_usd']),
                            "actions_taken": str(r['actions_taken'])
                        },
                        "notes": str(r['analyst_notes'])[:200]
                    }
                    
        # 3. Compute structural similarity & hybrid rank
        scored_cases = []
        for cid, cand in candidates.items():
            meta = cand["metadata"]
            c_pattern = meta.get("pattern", "")
            c_exposure = float(meta.get("exposure_usd", 0.0))
            
            # Graph structural score components [0, 1]
            graph_score = 0.0
            
            # Pattern match
            if target_pattern and c_pattern == target_pattern:
                graph_score += 0.50
            elif not target_pattern:
                graph_score += 0.20
                
            # Exposure proximity
            if target_exposure > 0.0:
                diff = abs(c_exposure - target_exposure)
                if diff <= (0.3 * target_exposure):
                    graph_score += 0.35
                elif diff <= (0.7 * target_exposure):
                    graph_score += 0.20
                elif diff <= (1.2 * target_exposure):
                    graph_score += 0.10
            else:
                graph_score += 0.20
                
            # Proven outcome weighting
            if meta.get("outcome") == "confirmed_fraud":
                graph_score += 0.15
                
            # Blend scores
            v_score = cand["vector_score"]
            hybrid_score = (alpha * v_score) + ((1.0 - alpha) * graph_score)
            
            scored_cases.append({
                "case_id": cid,
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

if __name__ == "__main__":
    engine = SimilarCasesEngine()
    print("Testing SimilarCasesEngine...")
    
    # Test case 1: Card testing
    res = engine.find_similar_cases(
        query_text="Card testing sequence: 3 micro authorizations under $5 within 40 minutes followed by $250 spend",
        target_pattern="card_testing",
        target_exposure=268.43,
        top_k=2
    )
    print("\n--- Card Testing Query Results ---")
    for r in res:
        print(f"[{r['case_id']}] Hybrid: {r['hybrid_score']} (Vec: {r['vector_score']}, Graph: {r['graph_score']}) | Pattern: {r['pattern']} | Exp: ${r['exposure_usd']}")
        print(f"   Notes: {r['notes_snippet'][:120]}...")
        
    # Test case 2: Out of region use
    res2 = engine.find_similar_cases(
        query_text="Card present in-person purchase in foreign region 444 while domestic home activity continues",
        target_pattern="out_of_region_use",
        target_exposure=150.0,
        top_k=2
    )
    print("\n--- Out of Region Query Results ---")
    for r in res2:
        print(f"[{r['case_id']}] Hybrid: {r['hybrid_score']} (Vec: {r['vector_score']}, Graph: {r['graph_score']}) | Pattern: {r['pattern']} | Exp: ${r['exposure_usd']}")
        print(f"   Notes: {r['notes_snippet'][:120]}...")
