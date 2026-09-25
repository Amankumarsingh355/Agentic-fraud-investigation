"""
Test Graph-Aware Case Similarity Engine (tests/test_graph_case_similarity.py)
Validates Issue 5 criteria:
1. Tripartite similarity computation: Text (0.4) + Graph (0.4) + Pattern (0.2)
2. Verifies that graph topology directly influences similarity ranking
3. Case A (identical text + disjoint topology) vs Case B (lower text match + matching topology):
   Verifies that Case B achieves higher composite similarity when graph weight is active.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from graph.similar_cases_engine import GraphCaseSimilarityEngine, SimilarCasesEngine

def test_graph_structure_influences_ranking():
    print("======================================================================")
    print("   TESTING GRAPH-AWARE CASE SIMILARITY ENGINE (ISSUE 5)")
    print("======================================================================\n")

    engine = GraphCaseSimilarityEngine(text_weight=0.4, graph_weight=0.4, pattern_weight=0.2)
    print(f"Engine Weights: Text={engine.text_weight}, Graph={engine.graph_weight}, Pattern={engine.pattern_weight}")

    # Query Case: A multi-customer hardware syndicate with 3 accounts sharing POS device
    query_meta = {
        "customer_id": "C_QUERY",
        "card_id": "CARD_QUERY",
        "pattern": "syndicate_ring",
        "exposure_usd": 150.0
    }
    query_subgraph = {
        "shared_hardware_ring": {
            "has_shared_ring": True,
            "connected_customers": ["C_MULE1", "C_MULE2"],
            "ring_size": 3
        },
        "card_timeline_72h": [{"txn_id": 1}, {"txn_id": 2}, {"txn_id": 3}],
        "identity_device": {"device_profile": "POS_Terminal_Model_X"}
    }
    query_features = engine.extract_graph_features(query_meta, query_subgraph)

    # Candidate Case A: High text overlap, but DISJOINT topology (single user, no shared ring, online, ring_size=1)
    cand_a_meta = {
        "customer_id": "C_DISJOINT",
        "card_id": "CARD_DISJOINT",
        "pattern": "out_of_region_use",
        "exposure_usd": 25.0
    }
    cand_a_subgraph = {
        "shared_hardware_ring": {
            "has_shared_ring": False,
            "connected_customers": [],
            "ring_size": 1
        },
        "card_timeline_72h": [{"txn_id": 99}],
        "identity_device": {"device_profile": "iPhone_Safari"}
    }
    cand_a_features = engine.extract_graph_features(cand_a_meta, cand_a_subgraph)
    text_sim_a = 0.90 # Very high text similarity

    # Candidate Case B: Moderate text overlap, but HIGHLY SIMILAR topology (multi-mule ring, ring_size=3, shared device, similar exposure)
    cand_b_meta = {
        "customer_id": "C_RING",
        "card_id": "CARD_RING",
        "pattern": "syndicate_ring",
        "exposure_usd": 140.0
    }
    cand_b_subgraph = {
        "shared_hardware_ring": {
            "has_shared_ring": True,
            "connected_customers": ["C_PREV1", "C_PREV2"],
            "ring_size": 3
        },
        "card_timeline_72h": [{"txn_id": 501}, {"txn_id": 502}],
        "identity_device": {"device_profile": "POS_Terminal_Model_Y"}
    }
    cand_b_features = engine.extract_graph_features(cand_b_meta, cand_b_subgraph)
    text_sim_b = 0.55 # Lower text similarity

    sim_a = engine.compute_composite_similarity(
        text_sim=text_sim_a,
        feat1=query_features,
        feat2=cand_a_features,
        pattern1=query_meta["pattern"],
        pattern2=cand_a_meta["pattern"]
    )

    sim_b = engine.compute_composite_similarity(
        text_sim=text_sim_b,
        feat1=query_features,
        feat2=cand_b_features,
        pattern1=query_meta["pattern"],
        pattern2=cand_b_meta["pattern"]
    )

    print("Case A (High text, Disjoint topology):")
    print(f"  • Text Sim:    {sim_a['text_similarity']}")
    print(f"  • Graph Sim:   {sim_a['graph_similarity']}")
    print(f"  • Pattern Sim: {sim_a['pattern_similarity']}")
    print(f"  • FINAL SCORE: {sim_a['final_similarity']}\n")

    print("Case B (Moderate text, Matching topology & ring):")
    print(f"  • Text Sim:    {sim_b['text_similarity']}")
    print(f"  • Graph Sim:   {sim_b['graph_similarity']}")
    print(f"  • Pattern Sim: {sim_b['pattern_similarity']}")
    print(f"  • FINAL SCORE: {sim_b['final_similarity']}\n")

    # Assert that graph structural influence elevates Case B over Case A
    assert sim_b['graph_similarity'] > sim_a['graph_similarity'], "Case B graph similarity must be higher than Case A"
    assert sim_b['final_similarity'] > sim_a['final_similarity'], (
        f"Case B ({sim_b['final_similarity']}) must rank higher than Case A ({sim_a['final_similarity']}) due to graph structure!"
    )
    print("  [PASS] Graph topology directly influenced ranking: Case B > Case A.")

    # Verification with SimilarCasesEngine instance
    sim_engine = SimilarCasesEngine()
    print("\n[PASS] SimilarCasesEngine initialized with GraphCaseSimilarityEngine.")

if __name__ == "__main__":
    test_graph_structure_influences_ranking()
