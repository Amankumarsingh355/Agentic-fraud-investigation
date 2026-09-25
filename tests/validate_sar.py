"""
Validator 5: FinCEN SAR Compliance Validator (tests/validate_sar.py)
Validates strict FinCEN Suspicious Activity Report (SAR) filing logic:
1. sar.file == True strictly requires FILE_REPORT in next_best_actions.final AND verdict == 'fraud'.
2. If sar.file == True:
   - narrative: > 100 characters covering Who, What, When, Where, Why, How.
   - subjects: non-empty list of target customer/suspect identifiers.
   - total_amount_usd: > 0 and matches case.exposure_usd exactly.
   - activity_dates: list of exactly 2 date strings [start, end].
3. If sar.file == False:
   - narrative == ""
   - subjects == []
   - total_amount_usd == 0
   - activity_dates == []
4. Under NO circumstances may a legitimate verdict trigger a SAR filing.
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


def validate_case_sar(data: Dict[str, Any], case_id: str) -> List[str]:
    errors = []
    c = data.get("case", {})
    sar = data.get("sar", {})
    nba = data.get("next_best_actions", {})

    verdict = c.get("verdict", "")
    sar_file = sar.get("file")
    exposure = float(c.get("exposure_usd", 0.0))

    final_action_names = [
        a.get("action") for a in nba.get("final", [])
    ]
    file_report_in_actions = "FILE_REPORT" in final_action_names

    # Rule 1: Under no circumstance can a legitimate verdict trigger SAR
    if verdict == "legitimate" and sar_file:
        errors.append("Rule violation: sar.file == True for a legitimate verdict! Legitimate cases can never file a SAR.")

    # Rule 2: sar.file must strictly track FILE_REPORT action
    if sar_file and not file_report_in_actions:
        errors.append("sar.file == True but 'FILE_REPORT' is NOT present in next_best_actions.final.")
    if file_report_in_actions and verdict == "fraud" and not sar_file:
        errors.append("next_best_actions.final contains 'FILE_REPORT' for fraud verdict, but sar.file is False.")

    # Rule 3: Content checks when sar.file is True
    if sar_file:
        narrative = sar.get("narrative", "")
        if not narrative or len(narrative) < 100:
            errors.append(f"When sar.file is True, narrative must be substantive (>100 chars), got {len(narrative)} chars.")

        subjects = sar.get("subjects", [])
        if not isinstance(subjects, list) or len(subjects) == 0:
            errors.append("When sar.file is True, subjects must be a non-empty list of suspect/customer entities.")

        sar_amount = sar.get("total_amount_usd", 0)
        if not isinstance(sar_amount, (int, float)) or sar_amount <= 0:
            errors.append(f"When sar.file is True, total_amount_usd must be > 0, got {sar_amount}")
        elif abs(float(sar_amount) - exposure) > 0.02:
            errors.append(f"When sar.file is True, total_amount_usd (${sar_amount}) must equal case.exposure_usd (${exposure})")

        dates = sar.get("activity_dates", [])
        if not isinstance(dates, list) or len(dates) != 2:
            errors.append(f"When sar.file is True, activity_dates must contain exactly [start, end], got {dates}")

    # Rule 4: Sanitization checks when sar.file is False
    else:
        if sar.get("narrative") != "":
            errors.append(f"When sar.file is False, narrative MUST be empty string '', got: '{sar.get('narrative')[:50]}...'")
        if sar.get("subjects") != []:
            errors.append(f"When sar.file is False, subjects MUST be empty list [], got: {sar.get('subjects')}")
        if sar.get("total_amount_usd") != 0:
            errors.append(f"When sar.file is False, total_amount_usd MUST be 0, got: {sar.get('total_amount_usd')}")
        if sar.get("activity_dates") != []:
            errors.append(f"When sar.file is False, activity_dates MUST be empty list [], got: {sar.get('activity_dates')}")

    return errors


def run_sar_validation(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("=" * 80)
    print("  VALIDATOR 5: FINCEN SAR REGULATORY COMPLIANCE VALIDATOR (tests/validate_sar.py)")
    print("=" * 80)

    case_files = sorted(glob.glob(os.path.join(cases_dir, "HHG-*.json")))
    if not case_files:
        print(f"[FAIL] No benchmark case files found in {cases_dir}")
        return False

    all_passed = True
    total_sar_filed = 0
    total_sar_exempt = 0

    for cpath in case_files:
        cid = os.path.basename(cpath).replace(".json", "")
        with open(cpath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"  [FAIL] {cid}: Invalid JSON: {e}")
                all_passed = False
                continue

        errors = validate_case_sar(data, cid)
        if errors:
            print(f"  [FAIL] {cid}: FinCEN SAR compliance errors:")
            for err in errors:
                print(f"         - {err}")
            all_passed = False
        else:
            sar = data.get("sar", {})
            if sar.get("file"):
                total_sar_filed += 1
                print(f"  [PASS] {cid}: SAR FILED (Amount: ${sar['total_amount_usd']:.2f}, Narrative: {len(sar['narrative'])} chars)")
            else:
                total_sar_exempt += 1
                print(f"  [PASS] {cid}: SAR EXEMPT (Fields cleanly cleared: narrative='', subjects=[], amount=0)")

    print("-" * 80)
    print(f"Total SARs Filed:  {total_sar_filed}")
    print(f"Total SARs Exempt: {total_sar_exempt}")
    if all_passed:
        print(f"[SUCCESS] All {len(case_files)} cases passed FinCEN SAR regulatory validation.\n")
    else:
        print(f"[FAIL] FinCEN SAR validation failed on one or more cases.\n")
    return all_passed


if __name__ == "__main__":
    ok = run_sar_validation()
    sys.exit(0 if ok else 1)
