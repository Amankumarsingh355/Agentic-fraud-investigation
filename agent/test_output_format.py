"""
Test and Verification Script for Phase 7: Explainability & Output Format
Validates Phase 7 Gate:
"Output for one sample case matches the README's required answer format exactly."

Validates:
1. Exact 3-part schema (internal case, regulatory SAR, evolved next best actions).
2. All required fields, data types, enum values, and structural dependencies.
3. Verification that case is written to graph memory (written_to_graph == True).
4. Emits detailed report to docs/phase7-output-format-report.md.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from agent.agent import FraudInvestigationAgent
from agent.case_formatter import (
    VALID_STATUSES,
    VALID_VERDICTS,
    VALID_PATTERNS,
    VALID_EVIDENCE_SOURCES,
    VALID_ACTION_ROUTES
)

def validate_exact_readme_format(data: dict) -> List[str]:
    """Strict validator against README.md Answer Format."""
    errors = []
    
    # 1. Top-level keys
    required_top = {
        "case_id": str,
        "case": dict,
        "evidence_requests": list,
        "next_best_actions": dict,
        "sar": dict,
        "stop_reason": str,
        "tool_calls": int,
        "tokens": int,
        "latency_s": (int, float)
    }
    for k, t in required_top.items():
        if k not in data:
            errors.append(f"Missing top-level key: '{k}'")
        elif not isinstance(data[k], t):
            errors.append(f"Top-level key '{k}' has type {type(data[k])}, expected {t}")
            
    if errors:
        return errors
        
    # 2. Part 1: case
    c = data["case"]
    case_keys = {
        "status": str,
        "verdict": str,
        "fraud_probability": (int, float),
        "pattern": str,
        "pattern_description": str,
        "affected_txn_ids": list,
        "first_suspicious_txn_id": str,
        "connected_card_ids": list,
        "connected_device_profiles": list,
        "exposure_usd": (int, float),
        "evidence": list,
        "similar_prior_cases": list,
        "summary": str,
        "written_to_graph": bool,
        "graph_case_id": str
    }
    for k, t in case_keys.items():
        if k not in c:
            errors.append(f"Missing 'case.{k}'")
        elif not isinstance(c[k], t):
            errors.append(f"'case.{k}' has type {type(c[k])}, expected {t}")
            
    if c.get("status") not in VALID_STATUSES:
        errors.append(f"Invalid case.status: '{c.get('status')}'. Allowed: {VALID_STATUSES}")
    if c.get("verdict") not in VALID_VERDICTS:
        errors.append(f"Invalid case.verdict: '{c.get('verdict')}'. Allowed: {VALID_VERDICTS}")
    if not (0.0 <= c.get("fraud_probability", -1) <= 1.0):
        errors.append(f"case.fraud_probability out of [0, 1] range: {c.get('fraud_probability')}")
    if c.get("pattern") not in VALID_PATTERNS:
        errors.append(f"Invalid case.pattern: '{c.get('pattern')}'. Allowed: {VALID_PATTERNS}")
    if c.get("pattern") == "undocumented" and not c.get("pattern_description"):
        errors.append("pattern_description required when pattern is 'undocumented'")
    if not c.get("written_to_graph"):
        errors.append("case.written_to_graph must be True")
    if not c.get("graph_case_id"):
        errors.append("case.graph_case_id must not be empty")

    # Evidence items
    for idx, ev in enumerate(c.get("evidence", [])):
        if not isinstance(ev, dict):
            errors.append(f"case.evidence[{idx}] is not an object")
            continue
        for ek in ["claim", "source", "ref", "entity_ids"]:
            if ek not in ev:
                errors.append(f"Missing key in evidence[{idx}]: '{ek}'")
        if ev.get("source") not in VALID_EVIDENCE_SOURCES:
            errors.append(f"Invalid evidence[{idx}].source: '{ev.get('source')}'")
        if not isinstance(ev.get("entity_ids"), list):
            errors.append(f"evidence[{idx}].entity_ids must be a list")

    # 3. Part 2: sar
    sar = data["sar"]
    sar_keys = {
        "file": bool,
        "reason": str,
        "narrative": str,
        "subjects": list,
        "total_amount_usd": (int, float),
        "activity_dates": list
    }
    for k, t in sar_keys.items():
        if k not in sar:
            errors.append(f"Missing 'sar.{k}'")
        elif not isinstance(sar[k], t):
            errors.append(f"'sar.{k}' has type {type(sar[k])}, expected {t}")
            
    if not sar.get("file"):
        if sar.get("narrative") != "":
            errors.append("When sar.file is false, sar.narrative must be empty string ''")
        if sar.get("subjects") != []:
            errors.append("When sar.file is false, sar.subjects must be empty list []")
        if sar.get("total_amount_usd") != 0:
            errors.append("When sar.file is false, sar.total_amount_usd must be 0")
        if sar.get("activity_dates") != []:
            errors.append("When sar.file is false, sar.activity_dates must be empty list []")
    else:
        if len(sar.get("narrative", "")) < 30:
            errors.append("When sar.file is true, narrative must be populated (6-12 sentences)")
        if not sar.get("subjects"):
            errors.append("When sar.file is true, subjects must contain IDs")
        if len(sar.get("activity_dates", [])) != 2:
            errors.append("When sar.file is true, activity_dates must contain [start, end]")

    # 4. Part 3: next_best_actions
    nba = data["next_best_actions"]
    if "initial" not in nba or not isinstance(nba["initial"], list):
        errors.append("next_best_actions.initial must be a list")
    if "final" not in nba or not isinstance(nba["final"], list):
        errors.append("next_best_actions.final must be a list")
    if "what_changed" not in nba or not isinstance(nba["what_changed"], str):
        errors.append("next_best_actions.what_changed must be a string")

    for act_list_name in ["initial", "final"]:
        for idx, act in enumerate(nba.get(act_list_name, [])):
            if not isinstance(act, dict):
                errors.append(f"next_best_actions.{act_list_name}[{idx}] is not an object")
                continue
            for ak in ["action", "route", "reason"]:
                if ak not in act:
                    errors.append(f"Missing '{ak}' in next_best_actions.{act_list_name}[{idx}]")
            if act.get("route") not in VALID_ACTION_ROUTES:
                errors.append(f"Invalid route in {act_list_name}[{idx}]: '{act.get('route')}'")

    return errors

def main():
    print("=" * 80)
    print("PHASE 7 GATE VERIFICATION: Output Format & Exact Answer Artifact")
    print("=" * 80)
    
    agent = FraudInvestigationAgent()
    
    # Run agent on sample case HHG-001 (Txn 3514030)
    print("\n[+] Running Agent on Benchmark Sample Case HHG-001 (Txn 3514030)...")
    case, submission = agent.run_investigation(
        trigger_type="risk_score",
        trigger_text="Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide.",
        flagged_txn_id=3514030,
        case_id="HHG-001",
        simulated_customer_response="denied_fraud", # Cardholder denies unrecognized out-of-region charge
        is_benchmark=True # Tags benchmark namespace
    )
    
    print(f"    -> Investigation finished in {submission['latency_s']}s.")
    print(f"    -> Case Status: {submission['case']['status']} | Verdict: {submission['case']['verdict']}")
    print(f"    -> Fraud Probability: {submission['case']['fraud_probability']}")
    print(f"    -> Written to graph: {submission['case']['written_to_graph']} (Graph ID: {submission['case']['graph_case_id']})")
    print(f"    -> SAR Filed: {submission['sar']['file']} (Reason: {submission['sar']['reason'][:60]}...)")
    print(f"    -> Actions Initial: {len(submission['next_best_actions']['initial'])} | Final: {len(submission['next_best_actions']['final'])}")
    
    # Run Schema Validation
    print("\n[+] Validating submission JSON against exact README specification...")
    errors = validate_exact_readme_format(submission)
    
    if errors:
        print("\n[-] VALIDATION FAILED WITH ERRORS:")
        for err in errors:
            print(f"   * {err}")
        sys.exit(1)
        
    print("\n[+] Schema validation passed with 0 errors! Exact match to README requirements.")
    
    # Verify graph persistence
    persisted = agent.case_memory_manager.get_case("HHG-001")
    assert persisted is not None, "Error: Case HHG-001 was not written to graph memory store!"
    print(f"[+] Verified graph persistence: Case HHG-001 stored in namespace '{persisted['namespace']}'")
    
    # Generate Report
    report_lines = [
        "# Phase 7 Verification Report: Explainability & Exact Output Format",
        "",
        "**Status**: VERIFIED & PASSING",
        "**Date**: September 21, 2026",
        "**Scope**: Validation of the 3-part submission JSON artifact against the exact schema specified in README.md (case, sar, next_best_actions).",
        "",
        "---",
        "",
        "## Phase 7 Gate Result: PASSED (0 Schema Errors)",
        "",
        "### Sample Case Validated: `HHG-001` (Txn `3514030`)",
        f"- **Verdict**: `{submission['case']['verdict']}`",
        f"- **Status**: `{submission['case']['status']}`",
        f"- **Fraud Probability**: `{submission['case']['fraud_probability']}`",
        f"- **Pattern**: `{submission['case']['pattern']}`",
        f"- **Written to Graph**: `{submission['case']['written_to_graph']}` (`{submission['case']['graph_case_id']}`)",
        f"- **SAR File Mandated**: `{submission['sar']['file']}`",
        f"- **Next Best Actions**: `{len(submission['next_best_actions']['initial'])}` initial $\\rightarrow$ `{len(submission['next_best_actions']['final'])}` final",
        "",
        "### Generated Submission Artifact (`cases/HHG-001.json`)",
        "```json",
        json.dumps(submission, indent=2),
        "```",
        "",
        "---",
        "",
        "## Graph Memory Record Inspection",
        "```json",
        json.dumps(persisted, indent=2),
        "```"
    ]
    
    report_path = "docs/phase7-output-format-report.md"
    os.makedirs("docs", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\nPhase 7 Gate Validation PASSED! Report saved to {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
