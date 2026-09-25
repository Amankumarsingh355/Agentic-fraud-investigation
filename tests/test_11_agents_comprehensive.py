"""
Comprehensive Test Suite: 11-Agent Fraud Investigation Pipeline
CrewAI + Ollama (Llama 3) + TigerGraph (pyTigerGraph)
"""

import os
import sys
import json
import time

# Ensure project root in sys.path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.eleven_agents_pipeline import ElevenAgentPipeline
from graph.tigergraph_crewai_integration import FrontendReportSchema


def test_11_agent_pipeline_execution():
    print("\n--- 1. Testing End-to-End 11-Agent Pipeline Execution ---")
    pipeline = ElevenAgentPipeline()
    
    t0 = time.time()
    result = pipeline.investigate(
        flagged_txn_id=3514030,
        user_id="User_101",
        trigger_type="High-Risk Transaction Alert",
        trigger_text="High-risk transfer ($15,000). TigerGraph query revealed User_101 shares Device_99 with known fraudulent User_882 across a 3-hop circular path."
    )
    elapsed = round((time.time() - t0) * 1000, 2)
    print(f"Pipeline executed in {elapsed} ms.")
    
    # Assertions on pipeline metadata
    assert result["success"] is True, "Pipeline execution must succeed"
    assert result["pipeline_stages_completed"] == 11, "Must complete all 11 agent stages"
    assert result["pipeline_status"] == "ALL_11_AGENTS_VERIFIED"
    print("[PASS] All 11 agent stages executed and verified.")
    
    # Check individual agent results
    agents = result["agents"]
    expected_agents = [
        "agent_1_ingestion",
        "agent_2_tigergraph",
        "agent_3_pattern",
        "agent_4_lifecycle",
        "agent_5_memory",
        "agent_6_stepup",
        "agent_7_action",
        "agent_8_policy",
        "agent_9_stopping",
        "agent_10_explainability"
    ]
    for ea in expected_agents:
        assert ea in agents, f"Missing agent output for {ea}"
        assert agents[ea]["status"] == "COMPLETED"
    print("[PASS] Individual agent reports verified for Agents 1-10.")

    # Validate Pydantic FrontendReportSchema
    f_rep = result["frontend_report"]
    report_obj = FrontendReportSchema(**f_rep)
    assert 0.0 <= report_obj.overall_fraud_score <= 1.0
    assert report_obj.investigation_status in ["RESOLVED", "ESCALATED", "PENDING_STEP_UP"]
    assert len(report_obj.key_evidence_summary) >= 3
    assert "shared_nodes" in report_obj.tigergraph_ring_findings
    assert "hops_traversed" in report_obj.tigergraph_ring_findings
    assert "graph_risk_level" in report_obj.tigergraph_ring_findings
    assert "agent_1_ingestion" in report_obj.agent_contributions
    assert "agent_8_policy" in report_obj.agent_contributions
    assert "agent_9_stopping" in report_obj.agent_contributions
    assert isinstance(report_obj.human_approval_required, bool)
    assert len(report_obj.audit_rationale) > 20
    print("[PASS] Pydantic FrontendReportSchema validated with 100% precision.")

    print("\n--- Production JSON Payload Output ---")
    print(report_obj.model_dump_json(indent=2))


def test_cot_audit_escalation_path():
    print("\n--- 2. Testing Chain-of-Thought (CoT) Audit Escalation ---")
    pipeline = ElevenAgentPipeline()
    # Test an ambiguous transaction where risk is lower and customer response is pending
    result = pipeline.investigate(
        flagged_txn_id=3514030,
        user_id="User_Ambiguous",
        trigger_type="Anomaly Flag",
        trigger_text="Standard transaction with minor location shift."
    )
    f_rep = result["frontend_report"]
    print(f"Status: {f_rep['investigation_status']} | Human Approval Required: {f_rep['human_approval_required']}")
    assert f_rep["human_approval_required"] is True, "Ambiguous case must enforce human approval"
    print("[PASS] CoT Step D escalation verified.")


if __name__ == "__main__":
    test_11_agent_pipeline_execution()
    test_cot_audit_escalation_path()
    print("\n==================================================================")
    print("  11-AGENT PIPELINE TEST SUITE: 100% SUCCESSFUL")
    print("==================================================================")
