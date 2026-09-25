"""
Validator 1: Schema Validator (tests/validate_schema.py)
Validates that every case JSON strictly adheres to the TigerGraph Fraud Investigation Benchmark Schema.
Covers:
- Exact top-level keys ('case_id', 'case', 'evidence_requests', 'next_best_actions', 'sar', 'stop_reason', 'tool_calls', 'tokens', 'latency_s')
- 'case' inner schema (verdict, status, pattern, exposure_usd, evidence, etc.)
- 'sar' schema (file, narrative, subjects, total_amount_usd, activity_dates)
- 'next_best_actions' schema (initial, final, what_changed)
- Enum validation, type validation, and range bounds.
"""

import os
import sys
import json
import glob
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

VALID_STATUSES = {"open", "closed_fraud", "closed_legitimate", "escalated"}
VALID_VERDICTS = {"fraud", "legitimate", "uncertain"}
VALID_PATTERNS = {
    "card_testing",
    "card_not_present_fraud",
    "card_not_present_new_device",
    "out_of_region_use",
    "account_takeover",
    "undocumented",
    "none"
}
VALID_EVIDENCE_SOURCES = {"graph", "document", "customer", "external"}
VALID_ACTION_ROUTES = {"auto", "L1", "L2"}


def validate_case_schema(data: Dict[str, Any], case_id: str) -> List[str]:
    """Validates schema for a single case dict. Returns list of error strings."""
    errors = []

    # 1. Top-Level Keys
    required_top = [
        "case_id", "case", "evidence_requests", "next_best_actions",
        "sar", "stop_reason", "tool_calls", "tokens", "latency_s"
    ]
    for k in required_top:
        if k not in data:
            errors.append(f"Missing required top-level key: '{k}'")

    if errors:
        return errors

    if data["case_id"] != case_id:
        errors.append(f"case_id mismatch: file is for {case_id} but json contains {data['case_id']}")

    # 2. Case Object
    c = data["case"]
    case_required = [
        "status", "verdict", "fraud_probability", "pattern",
        "pattern_description", "affected_txn_ids", "first_suspicious_txn_id",
        "connected_card_ids", "connected_device_profiles", "exposure_usd",
        "evidence", "similar_prior_cases", "summary", "written_to_graph",
        "graph_case_id"
    ]
    for ck in case_required:
        if ck not in c:
            errors.append(f"'case' missing key: '{ck}'")

    if c.get("status") not in VALID_STATUSES:
        errors.append(f"Invalid status: '{c.get('status')}'. Must be one of {VALID_STATUSES}")

    if c.get("verdict") not in VALID_VERDICTS:
        errors.append(f"Invalid verdict: '{c.get('verdict')}'. Must be one of {VALID_VERDICTS}")

    prob = c.get("fraud_probability")
    if not isinstance(prob, (int, float)) or not (0.0 <= prob <= 1.0):
        errors.append(f"Invalid fraud_probability: '{prob}'. Must be float in [0.0, 1.0]")

    if c.get("pattern") not in VALID_PATTERNS:
        errors.append(f"Invalid pattern: '{c.get('pattern')}'. Must be one of {VALID_PATTERNS}")

    if not isinstance(c.get("affected_txn_ids"), list):
        errors.append("affected_txn_ids must be a list of strings")

    if not isinstance(c.get("exposure_usd"), (int, float)) or c.get("exposure_usd") < 0:
        errors.append("exposure_usd must be a non-negative float")

    if not isinstance(c.get("evidence"), list):
        errors.append("evidence must be a list")
    else:
        for idx, ev in enumerate(c["evidence"]):
            for ek in ["claim", "source", "ref", "entity_ids"]:
                if ek not in ev:
                    errors.append(f"Evidence #{idx} missing '{ek}'")
            if ev.get("source") not in VALID_EVIDENCE_SOURCES:
                errors.append(f"Evidence #{idx} has invalid source: '{ev.get('source')}'")

    if not isinstance(c.get("written_to_graph"), bool) or not c.get("written_to_graph"):
        errors.append("written_to_graph must be True")

    if not c.get("graph_case_id"):
        errors.append("graph_case_id must be non-empty string")

    # 3. Next Best Actions Object
    nba = data["next_best_actions"]
    for nk in ["initial", "final", "what_changed"]:
        if nk not in nba:
            errors.append(f"'next_best_actions' missing key: '{nk}'")

    if isinstance(nba.get("initial"), list):
        for idx, a in enumerate(nba["initial"]):
            if "action" not in a or "route" not in a or "reason" not in a:
                errors.append(f"Initial action #{idx} missing required fields ('action', 'route', 'reason')")
            elif a["route"] not in VALID_ACTION_ROUTES:
                errors.append(f"Initial action #{idx} has invalid route: '{a['route']}'")
    else:
        errors.append("'next_best_actions.initial' must be a list")

    if isinstance(nba.get("final"), list):
        for idx, a in enumerate(nba["final"]):
            if "action" not in a or "route" not in a or "reason" not in a:
                errors.append(f"Final action #{idx} missing required fields ('action', 'route', 'reason')")
            elif a["route"] not in VALID_ACTION_ROUTES:
                errors.append(f"Final action #{idx} has invalid route: '{a['route']}'")
    else:
        errors.append("'next_best_actions.final' must be a list")

    if not isinstance(nba.get("what_changed"), str) or len(nba.get("what_changed", "")) < 10:
        errors.append("'what_changed' must be a non-empty string explaining action evolution")

    # 4. SAR Object
    sar = data["sar"]
    for sk in ["file", "narrative", "subjects", "total_amount_usd", "activity_dates"]:
        if sk not in sar:
            errors.append(f"'sar' missing key: '{sk}'")

    if not isinstance(sar.get("file"), bool):
        errors.append("sar.file must be boolean")
    elif sar["file"]:
        if not sar.get("narrative") or len(sar["narrative"]) < 50:
            errors.append("When sar.file is true, narrative must be non-empty (>50 chars)")
        if not isinstance(sar.get("subjects"), list) or len(sar["subjects"]) == 0:
            errors.append("When sar.file is true, subjects must be a non-empty list")
        if not isinstance(sar.get("total_amount_usd"), (int, float)) or sar["total_amount_usd"] <= 0:
            errors.append("When sar.file is true, total_amount_usd must be > 0")
        if not isinstance(sar.get("activity_dates"), list) or len(sar["activity_dates"]) != 2:
            errors.append("When sar.file is true, activity_dates must contain exactly [start_date, end_date]")
    else:
        if sar.get("narrative") != "":
            errors.append("When sar.file is false, narrative must be empty string")
        if sar.get("subjects") != []:
            errors.append("When sar.file is false, subjects must be []")
        if sar.get("total_amount_usd") != 0:
            errors.append("When sar.file is false, total_amount_usd must be 0")
        if sar.get("activity_dates") != []:
            errors.append("When sar.file is false, activity_dates must be []")

    # 5. Metadata
    if not isinstance(data.get("tool_calls"), int) or data["tool_calls"] <= 0:
        errors.append("tool_calls must be a positive integer")
    if not isinstance(data.get("tokens"), int) or data["tokens"] <= 0:
        errors.append("tokens must be a positive integer")
    if not isinstance(data.get("latency_s"), (int, float)) or data["latency_s"] <= 0:
        errors.append("latency_s must be a positive number")

    return errors


def run_schema_validation(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("=" * 80)
    print("  VALIDATOR 1: BENCHMARK SCHEMA VALIDATION (tests/validate_schema.py)")
    print("=" * 80)

    case_files = sorted(glob.glob(os.path.join(cases_dir, "HHG-*.json")))
    if not case_files:
        print(f"[FAIL] No benchmark case files found in {cases_dir}")
        return False

    all_passed = True
    for cpath in case_files:
        cid = os.path.basename(cpath).replace(".json", "")
        with open(cpath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"  [FAIL] {cid}: Invalid JSON: {e}")
                all_passed = False
                continue

        errors = validate_case_schema(data, cid)
        if errors:
            print(f"  [FAIL] {cid}: {len(errors)} schema errors:")
            for err in errors:
                print(f"         - {err}")
            all_passed = False
        else:
            print(f"  [PASS] {cid}: 100% schema compliant")

    print("-" * 80)
    if all_passed:
        print(f"[SUCCESS] All {len(case_files)} cases passed schema validation (0 errors).\n")
    else:
        print(f"[FAIL] Schema validation failed on one or more cases.\n")
    return all_passed


if __name__ == "__main__":
    ok = run_schema_validation()
    sys.exit(0 if ok else 1)
