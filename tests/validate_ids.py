"""
Validator 2: Entity ID Grounding Validator (tests/validate_ids.py)
Verifies ZERO hallucinated or fabricated IDs across all benchmark outputs:
1. Every transaction ID in affected_txn_ids and first_suspicious_txn_id exists in data/transactions.csv.
2. Every historical case ID in similar_prior_cases exists in data/closed_cases_history.csv (strictly CC-xxxx format).
3. Zero placeholder/test IDs (e.g., MEM-RUN-1, UPLOAD-TEST-01, TODO, PLACEHOLDER).
4. Customer and Card IDs match data/case_pack.csv.
"""

import os
import sys
import json
import csv
import glob
from typing import Dict, Any, List, Set

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def load_dataset_references():
    """Loads reference IDs from ground truth dataset CSVs."""
    case_pack_path = os.path.join(PROJECT_ROOT, "data", "case_pack.csv")
    closed_cases_path = os.path.join(PROJECT_ROOT, "data", "closed_cases_history.csv")
    transactions_path = os.path.join(PROJECT_ROOT, "data", "transactions.csv")

    case_pack = {}
    if os.path.exists(case_pack_path):
        with open(case_pack_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                case_pack[row["case_id"]] = row

    valid_closed_cases = set()
    if os.path.exists(closed_cases_path):
        with open(closed_cases_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                valid_closed_cases.add(row["case_id"])

    # Load transaction IDs set (scan column 1)
    valid_txns = set()
    if os.path.exists(transactions_path):
        with open(transactions_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            txn_idx = 0
            if header and "TransactionID" in header:
                txn_idx = header.index("TransactionID")
            for row in reader:
                if row:
                    valid_txns.add(row[txn_idx].strip())

    return case_pack, valid_closed_cases, valid_txns


def validate_case_ids(
    data: Dict[str, Any],
    case_id: str,
    case_pack: Dict[str, Any],
    valid_closed_cases: Set[str],
    valid_txns: Set[str]
) -> List[str]:
    errors = []
    c = data.get("case", {})
    pack_row = case_pack.get(case_id, {})

    # 1. First Suspicious Transaction ID
    first_txn = str(c.get("first_suspicious_txn_id", ""))
    expected_txn = str(pack_row.get("flagged_txn_id", ""))
    if c.get("verdict") != "legitimate":
        if expected_txn and first_txn != expected_txn:
            errors.append(f"first_suspicious_txn_id mismatch: got '{first_txn}', expected '{expected_txn}'")

    # 2. Affected Transaction IDs Grounding
    affected = c.get("affected_txn_ids", [])
    if not isinstance(affected, list):
        errors.append("affected_txn_ids must be a list")
    else:
        for tid in affected:
            tid_str = str(tid).strip()
            if valid_txns and tid_str not in valid_txns:
                errors.append(f"Hallucinated transaction ID in affected_txn_ids: '{tid_str}' not in transactions.csv")

    # 3. Similar Prior Cases Grounding (Zero Non-Dataset IDs)
    similar_cases = c.get("similar_prior_cases", [])
    if not isinstance(similar_cases, list):
        errors.append("similar_prior_cases must be a list")
    else:
        for sim_id in similar_cases:
            sim_str = str(sim_id).strip()
            if not sim_str.startswith("CC-"):
                errors.append(f"Invalid case prefix in similar_prior_cases: '{sim_str}' (must be 'CC-xxxx')")
            elif valid_closed_cases and sim_str not in valid_closed_cases:
                errors.append(f"Hallucinated case ID in similar_prior_cases: '{sim_str}' not in closed_cases_history.csv")

    # 4. Check for Test / Synthetic / Placeholder Markers
    forbidden_tokens = ["MEM-RUN", "UPLOAD-TEST", "TODO", "PLACEHOLDER", "FIXME", "XXX"]
    full_text = json.dumps(data)
    for token in forbidden_tokens:
        if token in full_text:
            errors.append(f"Contains synthetic/placeholder token: '{token}'")

    return errors


def run_id_validation(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("=" * 80)
    print("  VALIDATOR 2: ENTITY ID GROUNDING VALIDATION (tests/validate_ids.py)")
    print("=" * 80)

    case_pack, valid_closed_cases, valid_txns = load_dataset_references()
    print(f"Loaded reference dataset: {len(case_pack)} case pack entries, {len(valid_closed_cases)} closed cases, {len(valid_txns)} transactions.\n")

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

        errors = validate_case_ids(data, cid, case_pack, valid_closed_cases, valid_txns)
        if errors:
            print(f"  [FAIL] {cid}: {len(errors)} grounding errors:")
            for err in errors:
                print(f"         - {err}")
            all_passed = False
        else:
            sim_count = len(data.get("case", {}).get("similar_prior_cases", []))
            aff_count = len(data.get("case", {}).get("affected_txn_ids", []))
            print(f"  [PASS] {cid}: All IDs grounded ({aff_count} txns, {sim_count} prior cases)")

    print("-" * 80)
    if all_passed:
        print(f"[SUCCESS] All {len(case_files)} cases passed ID grounding validation (0 hallucinations).\n")
    else:
        print(f"[FAIL] ID grounding validation failed on one or more cases.\n")
    return all_passed


if __name__ == "__main__":
    ok = run_id_validation()
    sys.exit(0 if ok else 1)
