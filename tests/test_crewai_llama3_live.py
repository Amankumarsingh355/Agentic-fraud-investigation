"""
Test Suite: CrewAI + Ollama (Llama 3) + TigerGraph (pyTigerGraph)
End-to-End Verification of Multi-Agent Fraud Investigation System
"""

import os
import sys
import json
import time

# Ensure project root in sys.path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from graph.tigergraph_crewai_integration import (
    conn,
    trace_fraud_ring,
    get_user_graph_profile,
    FrontendReportSchema,
    EnterpriseFraudInvestigationCrew
)


def test_tigergraph_tools():
    print("\n--- 1. Testing TigerGraph Tools ---")
    user_id = "CUST-3514030"
    
    print(f"Calling trace_fraud_ring(user_id='{user_id}', max_hops=3)...")
    t0 = time.time()
    ring_output = trace_fraud_ring.invoke({"user_id": user_id, "max_hops": 3})
    ring_data = json.loads(ring_output)
    print(f"Ring query completed in {round((time.time() - t0)*1000, 2)} ms.")
    assert "results" in ring_data, "trace_fraud_ring must return a results key"
    print("[PASS] Tool 1 (trace_fraud_ring) verified.")

    print(f"Calling get_user_graph_profile(user_id='{user_id}')...")
    t1 = time.time()
    prof_output = get_user_graph_profile.invoke({"user_id": user_id})
    prof_data = json.loads(prof_output)
    print(f"Profile query completed in {round((time.time() - t1)*1000, 2)} ms.")
    assert "results" in prof_data, "get_user_graph_profile must return a results key"
    print("[PASS] Tool 2 (get_user_graph_profile) verified.")


def test_enterprise_crew_and_schema():
    print("\n--- 2. Testing Enterprise Crew & FrontendReportSchema ---")
    crew_engine = EnterpriseFraudInvestigationCrew()
    
    t0 = time.time()
    report: FrontendReportSchema = crew_engine.run_investigation(
        case_id="HHG-001",
        user_id="CUST-3514030",
        flagged_txn_id=3514030,
        trigger_context="Multi-hop transaction ring alert"
    )
    elapsed = round((time.time() - t0) * 1000, 2)
    print(f"Investigation completed in {elapsed} ms.")
    
    # Assertions on FrontendReportSchema
    assert report.case_id == "HHG-001"
    assert 0.0 <= report.overall_fraud_score <= 1.0
    assert report.investigation_status in ["RESOLVED", "ESCALATED", "PENDING_STEP_UP"]
    assert len(report.key_evidence_summary) >= 3
    assert "query_executed" in report.tigergraph_ring_findings
    assert "Agent_11_LeadSynthesizer" in report.agent_contributions
    assert isinstance(report.human_approval_required, bool)
    assert len(report.audit_rationale) > 20
    
    print("\n[PASS] Validated Production JSON Output:")
    print(report.model_dump_json(indent=2))
    print("\n[PASS] All FrontendReportSchema assertions PASSED with 100% precision.")


if __name__ == "__main__":
    test_tigergraph_tools()
    test_enterprise_crew_and_schema()
    print("\n========================================================")
    print("  ALL TESTS PASSED: CrewAI + Ollama (Llama 3) + TigerGraph")
    print("========================================================")
