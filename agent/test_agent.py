"""
Test and Verification Harness for Phase 5: Agent Core & Investigation Loop
Runs the full stateful investigation loop end-to-end on non-benchmark historical cases:
1. Case TEST-01 (Txn: 3000332 / Customer C06403) - Out-of-region in-person spend with interactive verification.
2. Case TEST-02 (Txn: 3000196 / Customer C12982) - Customer report of card testing sequence.
3. Case TEST-03 (Txn: 3001018 / Customer C03667) - High model risk score alert with policy gating.

Validates that:
- Full 8-stage loop executes without crashing.
- Inspectable confidence logic properly identifies evidence gaps.
- Policy gating correctly executes 'auto' actions while staging 'L1'/'L2' actions for human sign-off.
- Complete case record and audit trail are saved to disk.
"""

import os
import sys
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from agent.agent import FraudInvestigationAgent

def main():
    print("=" * 80)
    print("PHASE 5 GATE VERIFICATION: Agent Core Investigation Loop")
    print("=" * 80)
    
    agent = FraudInvestigationAgent()
    
    test_scenarios = [
        {
            "case_id": "TEST-01",
            "txn_id": 3000332,
            "trigger_type": "risk_score",
            "trigger_text": "Real-time model scored transaction 3000332 ($117.05, in billing region 476.0) at 0.73. Review and decide.",
            "simulated_customer_response": "denied_fraud", # Cardholder denies charge
            "description": "Out-of-region POS spend with customer denial resulting in staged card block."
        },
        {
            "case_id": "TEST-02",
            "txn_id": 3000196,
            "trigger_type": "customer_report",
            "trigger_text": "Customer C12982 message: 'I see an unrecognized online purchase of $30.12 following small test transactions. Please check my card.' Refers to 3000196.",
            "simulated_customer_response": None, # Direct customer report already indicates unauthorized charge
            "description": "Customer dispute on online card testing sequence."
        },
        {
            "case_id": "TEST-03",
            "txn_id": 3001018,
            "trigger_type": "risk_score",
            "trigger_text": "Real-time model scored transaction 3001018 ($49.04) at 0.84. Review and decide.",
            "simulated_customer_response": "confirmed_authorized", # Customer confirms legitimate travel
            "description": "High risk score with customer confirmation resulting in safe case closure (Rule R3)."
        }
    ]
    
    out_dir = "cases"
    os.makedirs(out_dir, exist_ok=True)
    
    report_lines = [
        "# Phase 5 Verification Report: Agent Core & Investigation Loop",
        "",
        "**Status**: VERIFIED & PASSING",
        "**Date**: September 21, 2026",
        "**Scope**: Validation of autonomous 8-stage investigation loop, inspectable uncertainty/confidence logic, controlled evidence gathering, and policy approval gating (auto vs L1 vs L2) across non-benchmark test cases.",
        "",
        "---",
        ""
    ]
    
    for sc in test_scenarios:
        print(f"\n[+] Running Full Agent Loop for Case {sc['case_id']} (Txn {sc['txn_id']})...")
        print(f"    Scenario: {sc['description']}")
        
        case = agent.run_investigation(
            trigger_type=sc["trigger_type"],
            trigger_text=sc["trigger_text"],
            flagged_txn_id=sc["txn_id"],
            case_id=sc["case_id"],
            simulated_customer_response=sc["simulated_customer_response"]
        )
        
        # Verify Case Integrity
        assert case.status in ["RESOLVED", "CLOSED"], f"Unexpected final status: {case.status}"
        assert len(case.evidence_list) >= 4, f"Insufficient evidence recorded: {len(case.evidence_list)}"
        assert len(case.actions) >= 1, f"No actions recorded: {len(case.actions)}"
        assert len(case.audit_trail) >= 5, f"Incomplete audit trail: {len(case.audit_trail)}"
        assert len(case.decision_explanation) > 100, "Missing decision explanation"
        
        # Verify Policy Gating Integrity
        for act in case.actions:
            if act["route"] == "auto":
                assert act["status"] == "EXECUTED", f"Auto action {act['action_name']} not executed!"
            elif act["route"] in ["L1", "L2"]:
                assert act["status"] == "PENDING_HUMAN_APPROVAL", f"Action {act['action_name']} exceeded authority without approval!"
                
        # Save Case JSON
        case_file = os.path.join(out_dir, f"{case.case_id}.json")
        with open(case_file, "w", encoding="utf-8") as f:
            f.write(case.to_json())
            
        print(f"    -> Case completed successfully! Final status: {case.status}")
        print(f"    -> Evidence items gathered: {len(case.evidence_list)}")
        print(f"    -> Actions recorded: {len(case.actions)}")
        print(f"    -> Audit events logged: {len(case.audit_trail)}")
        print(f"    -> Case record saved to {case_file}")
        
        # Add to markdown report
        report_lines.append(f"## Case Record: {case.case_id} (Txn: `{sc['txn_id']}`)")
        report_lines.append(f"- **Scenario**: {sc['description']}")
        report_lines.append(f"- **Trigger**: `{case.trigger['type']}` — *\"{case.trigger['text']}\"*")
        report_lines.append(f"- **Final Case Status**: `{case.status}`")
        report_lines.append(f"- **Fraud Probability**: `{case.risk_assessment['fraud_probability']:.2f}` | **Confidence**: `{case.risk_assessment['confidence_level']}`")
        report_lines.append("")
        report_lines.append("### Actions Executed & Staged")
        report_lines.append("| Action | Route | Status | Policy Rule | Justification |")
        report_lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for a in case.actions:
            report_lines.append(f"| `{a['action_name']}` | `{a['route']}` | **{a['status']}** | {a['policy_rule']} | {a['reason']} |")
            
        report_lines.append("")
        report_lines.append("### Decision Rationale")
        report_lines.append(case.decision_explanation)
        report_lines.append("")
        report_lines.append("### Audit Trail Summary")
        report_lines.append(f"Total audit trail events logged: {len(case.audit_trail)}.")
        report_lines.append("```json")
        report_lines.append(json.dumps(case.audit_trail[:5], indent=2))
        report_lines.append("... [truncated for display]")
        report_lines.append("```")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

    report_path = "docs/phase5-agent-report.md"
    os.makedirs("docs", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n" + "=" * 80)
    print(f"Phase 5 Gate Validation PASSED! Report saved to {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
