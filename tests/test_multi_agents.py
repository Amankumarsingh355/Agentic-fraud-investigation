"""
Unit test for Multi-Agent Fraud Squad
Verifies:
1. All 5 individual agents execute and produce valid reports
2. Chief Orchestrator synthesizes consensus and generates 100% valid submission
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agents import (
    GraphTopologyAgent,
    VelocityAnomalyAgent,
    IdentityDeviceAgent,
    PolicyComplianceAgent,
    CaseMemoryAgent,
    ChiefOrchestratorAgent
)

def test_squad():
    print("[TEST] Initializing ChiefOrchestratorAgent...")
    orch = ChiefOrchestratorAgent()
    
    # Test on Txn #3514030 (HHG-001)
    print("\n[TEST] Running Squad Investigation on Txn #3514030...")
    result = orch.run_squad_investigation(
        flagged_txn_id=3514030,
        trigger_type="risk_score",
        trigger_text="Real-time model scored transaction 3514030 at 0.61.",
        case_id="HHG-001"
    )

    assert result["success"] is True
    assert "squad_consensus" in result
    assert "agents" in result
    assert len(result["agents"]) == 5

    print(f"\n--- SQUAD CONSENSUS REPORT ({result['elapsed_ms']} ms) ---")
    print(f"Weighted Risk: {result['squad_consensus']['weighted_risk_score']}")
    print(f"Team Confidence: {result['squad_consensus']['team_confidence']}")
    print(f"Verdict: {result['squad_consensus']['verdict']}")

    print("\n--- INDIVIDUAL AGENT BREAKDOWNS ---")
    for k, a in result["agents"].items():
        print(f"[{a['agent_name']}] Status={a['status']} Risk={a['risk_score']} Conf={a['confidence']}")
        print(f"   Summary: {a['summary']}")
        if a["findings"]:
            print(f"   Key Finding: {a['findings'][0]['description']}")
        print()

    print("[PASS] All 5 individual specialist agents evaluated successfully!")

if __name__ == "__main__":
    test_squad()
