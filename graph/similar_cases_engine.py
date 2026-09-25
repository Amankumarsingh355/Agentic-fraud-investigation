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

class GraphCaseSimilarityEngine:
    """
    Graph-Aware Case Similarity Engine (Issue 5)
    Evaluates case relevance by fusing:
    1. Text Semantic Similarity (vector / TF-IDF cosine)
    2. Graph Structural Similarity (hop depth, ring size, shared devices, entity count, velocity)
    3. Pattern Taxonomy Similarity (category matching)
    
    Final Similarity = (Text * TEXT_WEIGHT) + (Graph * GRAPH_WEIGHT) + (Pattern * PATTERN_WEIGHT)
    """
    def __init__(
        self,
        text_weight: float = 0.4,
        graph_weight: float = 0.4,
        pattern_weight: float = 0.2
    ):
        total = text_weight + graph_weight + pattern_weight
        self.text_weight = text_weight / total
        self.graph_weight = graph_weight / total
        self.pattern_weight = pattern_weight / total

    def extract_graph_features(self, case_meta: Dict[str, Any], subgraph: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extracts topological feature vector from case metadata and subgraph."""
        rings = subgraph.get("shared_hardware_ring", {}) if subgraph else {}
        timeline = subgraph.get("card_timeline_72h", []) if subgraph else []
        dev = subgraph.get("identity_device") if subgraph else None

        ring_size = rings.get("ring_size", 1) if rings else (
            2 if case_meta.get("pattern") in ["syndicate_ring", "card_not_present_new_device"] else 1
        )
        shared_devices = len(rings.get("connected_customers", [])) if rings else (1 if ring_size > 1 else 0)
        txn_count = len(timeline) if timeline else int(case_meta.get("affected_txns_count", 1))
        hop_depth = 3 if ring_size > 1 else 2
        entity_count = 2 + ring_size + (1 if dev else 0)

        # Entity set for overlap computation
        entities = set()
        if case_meta.get("customer_id"):
            entities.add(f"cust_{case_meta.get('customer_id')}")
        if case_meta.get("card_id"):
            entities.add(f"card_{case_meta.get('card_id')}")
        if dev and dev.get("device_profile"):
            entities.add(f"dev_{dev.get('device_profile')}")
        for c in rings.get("connected_customers", []):
            entities.add(f"cust_{c}")

        return {
            "entity_count": entity_count,
            "transaction_count": txn_count,
            "device_count": 1 if dev else 0,
            "shared_device_count": shared_devices,
            "relationship_count": entity_count + txn_count,
            "hop_depth": hop_depth,
            "ring_size": ring_size,
            "transaction_velocity": float(len(timeline)) if timeline else 1.0,
            "exposure_usd": float(case_meta.get("exposure_usd", 0.0) or 0.0),
            "entities": entities
        }

    def compute_structural_similarity(self, f1: Dict[str, Any], f2: Dict[str, Any]) -> float:
        """Computes topological similarity between two case feature vectors in [0.0, 1.0]."""
        # 1. Ring size similarity
        r1 = f1.get("ring_size", 1)
        r2 = f2.get("ring_size", 1)
        ring_sim = 1.0 - (abs(r1 - r2) / max(r1, r2, 1))

        # 2. Hop depth similarity
        h1 = f1.get("hop_depth", 2)
        h2 = f2.get("hop_depth", 2)
        hop_sim = 1.0 - (abs(h1 - h2) / max(h1, h2, 1))

        # 3. Shared device ratio similarity
        sd1 = 1.0 if f1.get("shared_device_count", 0) > 0 else 0.0
        sd2 = 1.0 if f2.get("shared_device_count", 0) > 0 else 0.0
        device_sim = 1.0 if sd1 == sd2 else 0.2

        # 4. Entity overlap Jaccard
        e1 = f1.get("entities", set())
        e2 = f2.get("entities", set())
        if e1 and e2 and (e1 | e2):
            overlap_sim = len(e1 & e2) / len(e1 | e2)
        else:
            overlap_sim = 0.0

        # 5. Financial exposure proximity
        exp1 = max(float(f1.get("exposure_usd", 1.0)), 1.0)
        exp2 = max(float(f2.get("exposure_usd", 1.0)), 1.0)
        ratio = min(exp1, exp2) / max(exp1, exp2)
        exposure_sim = ratio

        # Composite structural score
        graph_sim = (
            0.35 * ring_sim +
            0.20 * hop_sim +
            0.20 * device_sim +
            0.15 * exposure_sim +
            0.10 * overlap_sim
        )
        return max(0.0, min(1.0, float(graph_sim)))

    def compute_pattern_similarity(self, p1: Optional[str], p2: Optional[str]) -> float:
        """Taxonomic pattern similarity in [0.0, 1.0]."""
        if not p1 or not p2:
            return 0.2
        p1 = p1.lower().strip()
        p2 = p2.lower().strip()
        if p1 == p2:
            return 1.0

        # Pattern family clusters
        families = [
            {"card_testing", "card_velocity_burst", "card_testing_velocity"},
            {"card_not_present_fraud", "card_not_present_new_device", "cnp_new_device", "account_takeover"},
            {"out_of_region_use", "out_of_region"},
            {"syndicate_ring", "undocumented", "shared_hardware_syndicate"}
        ]
        for fam in families:
            if p1 in fam and p2 in fam:
                return 0.65

        return 0.15

    def compute_composite_similarity(
        self,
        text_sim: float,
        feat1: Dict[str, Any],
        feat2: Dict[str, Any],
        pattern1: str,
        pattern2: str
    ) -> Dict[str, float]:
        """Calculates final combined similarity across text, graph, and pattern."""
        graph_sim = self.compute_structural_similarity(feat1, feat2)
        pattern_sim = self.compute_pattern_similarity(pattern1, pattern2)

        final_sim = (
            (self.text_weight * text_sim) +
            (self.graph_weight * graph_sim) +
            (self.pattern_weight * pattern_sim)
        )

        return {
            "text_similarity": round(float(text_sim), 4),
            "graph_similarity": round(float(graph_sim), 4),
            "pattern_similarity": round(float(pattern_sim), 4),
            "final_similarity": round(float(final_sim), 4),
            "weights": {
                "text": self.text_weight,
                "graph": self.graph_weight,
                "pattern": self.pattern_weight
            }
        }

class SimilarCasesEngine:
    def __init__(
        self,
        data_path=os.path.join("data", "closed_cases_history.csv"),
        memory_file: str = MEMORY_FILE,
        retriever=None,
        text_weight: float = 0.4,
        graph_weight: float = 0.4,
        pattern_weight: float = 0.2
    ):
        self.retriever = retriever or VectorRetriever()
        self.memory_file = memory_file
        self.df_cc = pd.read_csv(data_path)
        self.case_lookup = self.df_cc.set_index("case_id").to_dict(orient="index")
        self.graph_similarity_engine = GraphCaseSimilarityEngine(
            text_weight=text_weight,
            graph_weight=graph_weight,
            pattern_weight=pattern_weight
        )
        
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
            # STRICT ISOLATION: Never retrieve benchmark evaluation cases or ungrounded synthetic cases
            if dcase.get("is_benchmark") or dcase.get("namespace") == "eval_benchmark":
                continue
            if cid not in self.case_lookup:
                # Do not retrieve mock or synthetic memory cases not in closed_cases_history.csv
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

        # 3. Structural feature extraction & tripartite similarity ranking
        target_meta = {
            "customer_id": target_customer,
            "device_profile": target_device,
            "pattern": target_pattern,
            "exposure_usd": target_exposure
        }
        target_features = self.graph_similarity_engine.extract_graph_features(target_meta)

        scored_cases = []
        for cid, cand in candidates.items():
            meta = cand["metadata"]
            c_pattern = meta.get("pattern", "")
            c_exposure = float(meta.get("exposure_usd", 0.0) or 0.0)
            is_dynamic = cand.get("is_dynamic", False)
            cand_features = self.graph_similarity_engine.extract_graph_features(meta)

            # Compute composite similarity using tripartite engine
            sim_res = self.graph_similarity_engine.compute_composite_similarity(
                text_sim=cand["vector_score"],
                feat1=target_features,
                feat2=cand_features,
                pattern1=target_pattern,
                pattern2=c_pattern
            )
            final_score = sim_res["final_similarity"]

            # Dynamic recency boost if freshly resolved case
            if is_dynamic:
                final_score = min(1.0, final_score + 0.05)

            scored_cases.append({
                "case_id": cid,
                "is_dynamic": is_dynamic,
                "hybrid_score": round(final_score, 4),
                "vector_score": sim_res["text_similarity"],
                "graph_score": sim_res["graph_similarity"],
                "pattern_score": sim_res["pattern_similarity"],
                "pattern": c_pattern,
                "outcome": meta.get("outcome"),
                "exposure_usd": c_exposure,
                "actions_taken": meta.get("actions_taken"),
                "notes_snippet": cand["notes"],
                "similarity_breakdown": sim_res
            })
            
        # Sort by hybrid score descending
        scored_cases.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return scored_cases[:top_k]
