"""
Validator 3: Exposure Mathematical Identity Validator (tests/validate_exposure.py)
Validates the mathematical identity:
  exposure_usd == sum(abs(TransactionAmt)) for all affected_txn_ids
And validates FinCEN SAR consistency:
  When sar.file == True  -> sar.total_amount_usd == case.exposure_usd
  When sar.file == False -> sar.total_amount_usd == 0
"""

import os
import sys
import json
import csv
import glob
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def load_transaction_amounts() -> Dict[str, float]:
    """Loads TransactionID -> TransactionAmt lookup from transactions.csv."""
    txn_csv_path = os.path.join(PROJECT_ROOT, "data", "transactions.csv")
    amounts = {}
    if os.path.exists(txn_csv_path):
        with open(txn_csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            tid_idx = 0
            amt_idx = 3
            if header:
                if "TransactionID" in header:
                    tid_idx = header.index("TransactionID")
                if "TransactionAmt" in header:
                    amt_idx = header.index("TransactionAmt")
            for row in reader:
                if len(row) > max(tid_idx, amt_idx):
                    try:
                        tid = row[tid_idx].strip()
                        amt = abs(float(row[amt_idx].strip()))
                        amounts[tid] = amt
                    except ValueError:
                        pass
    return amounts


def validate_case_exposure(data: Dict[str, Any], case_id: str, txn_amounts: Dict[str, float]) -> List[str]:
    errors = []
    c = data.get("case", {})
    sar = data.get("sar", {})

    verdict = c.get("verdict", "")
    reported_exposure = float(c.get("exposure_usd", 0.0))
    affected = [str(t) for t in c.get("affected_txn_ids", [])]

    if verdict == "legitimate":
        if reported_exposure != 0.0:
            errors.append(f"Legitimate verdict must have exposure_usd == 0.0, but got {reported_exposure}")
        if sar.get("total_amount_usd", 0) != 0:
            errors.append(f"Legitimate verdict must have sar.total_amount_usd == 0, but got {sar.get('total_amount_usd')}")
    else:
        # Sum transaction amounts
        calculated_sum = 0.0
        missing_txns = []
        for tid in affected:
            if tid in txn_amounts:
                calculated_sum += txn_amounts[tid]
            else:
                missing_txns.append(tid)

        if missing_txns:
            errors.append(f"Affected txns not found in transactions.csv: {missing_txns}")
        else:
            calculated_sum = round(calculated_sum, 2)
            # Compare with reported exposure
            if abs(reported_exposure - calculated_sum) > 0.02:
                errors.append(
                    f"exposure_usd mismatch: reported ${reported_exposure:.2f}, "
                    f"calculated sum(${len(affected)} txns) = ${calculated_sum:.2f}"
                )

        # Validate SAR amount consistency
        sar_file = sar.get("file", False)
        sar_amount = float(sar.get("total_amount_usd", 0.0))
        if sar_file:
            if abs(sar_amount - reported_exposure) > 0.02:
                errors.append(
                    f"SAR amount mismatch: sar.total_amount_usd (${sar_amount:.2f}) != case.exposure_usd (${reported_exposure:.2f})"
                )
        else:
            if sar_amount != 0.0:
                errors.append(f"When sar.file is false, sar.total_amount_usd must be 0, but got ${sar_amount:.2f}")

    return errors


def run_exposure_validation(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("=" * 80)
    print("  VALIDATOR 3: EXPOSURE MATHEMATICAL IDENTITY VALIDATOR (tests/validate_exposure.py)")
    print("=" * 80)

    txn_amounts = load_transaction_amounts()
    print(f"Loaded {len(txn_amounts)} transaction amounts from data/transactions.csv.\n")

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

        errors = validate_case_exposure(data, cid, txn_amounts)
        if errors:
            print(f"  [FAIL] {cid}: Exposure errors:")
            for err in errors:
                print(f"         - {err}")
            all_passed = False
        else:
            c = data["case"]
            sar = data["sar"]
            print(f"  [PASS] {cid}: Exposure = ${c['exposure_usd']:.2f} (SAR file: {sar['file']}, amount: ${sar['total_amount_usd']:.2f})")

    print("-" * 80)
    if all_passed:
        print(f"[SUCCESS] All {len(case_files)} cases passed exposure mathematical identity validation.\n")
    else:
        print(f"[FAIL] Exposure validation failed on one or more cases.\n")
    return all_passed


if __name__ == "__main__":
    ok = run_exposure_validation()
    sys.exit(0 if ok else 1)
