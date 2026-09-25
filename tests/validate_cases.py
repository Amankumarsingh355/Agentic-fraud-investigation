"""
Master Validator Suite: All 20 Cases (tests/validate_cases.py)
Executes all 6 domain validators across all 20 benchmark case artifacts:
1. Schema Validator (tests/validate_schema.py)
2. Entity ID Grounding Validator (tests/validate_ids.py)
3. Exposure Mathematical Identity Validator (tests/validate_exposure.py)
4. Policy Compliance & Route Governance Validator (tests/validate_policy.py)
5. FinCEN SAR Regulatory Compliance Validator (tests/validate_sar.py)
6. Graph Persistence Validator (tests/validate_graph_write.py)

Generates an executive compliance scoreboard and ensures 100% audit readiness.
"""

import os
import sys
import glob

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.validate_schema import run_schema_validation
from tests.validate_ids import run_id_validation
from tests.validate_exposure import run_exposure_validation
from tests.validate_policy import run_policy_validation
from tests.validate_sar import run_sar_validation
from tests.validate_graph_write import run_graph_write_validation


def run_all_validators(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("\n" + "=" * 90)
    print("  TIGERGRAPH 11-AGENT FRAUD INVESTIGATION SYSTEM — MASTER VALIDATOR SUITE")
    print(f"  Validating benchmark cases in: {cases_dir}")
    print("=" * 90 + "\n")

    case_files = sorted(glob.glob(os.path.join(cases_dir, "HHG-*.json")))
    if len(case_files) != 20:
        print(f"[WARNING] Expected 20 benchmark cases (HHG-001 through HHG-020), but found {len(case_files)}.")

    suite_results = {}

    # Test 1: Schema
    print(">>> RUNNING VALIDATOR 1/6: JSON Schema & Field Specifications...")
    suite_results["Schema Validator"] = run_schema_validation(cases_dir)

    # Test 2: ID Grounding
    print(">>> RUNNING VALIDATOR 2/6: Entity ID Grounding & Zero Hallucinations...")
    suite_results["ID Grounding Validator"] = run_id_validation(cases_dir)

    # Test 3: Exposure
    print(">>> RUNNING VALIDATOR 3/6: Exposure Mathematical Identity...")
    suite_results["Exposure Validator"] = run_exposure_validation(cases_dir)

    # Test 4: Policy
    print(">>> RUNNING VALIDATOR 4/6: Policy Compliance & Approval Routes...")
    suite_results["Policy Compliance Validator"] = run_policy_validation(cases_dir)

    # Test 5: SAR
    print(">>> RUNNING VALIDATOR 5/6: FinCEN SAR Regulatory Rules...")
    suite_results["FinCEN SAR Validator"] = run_sar_validation(cases_dir)

    # Test 6: Graph Persistence
    print(">>> RUNNING VALIDATOR 6/6: Graph Memory Store Persistence...")
    suite_results["Graph Persistence Validator"] = run_graph_write_validation(cases_dir)

    # Summary Scoreboard
    print("\n" + "=" * 90)
    print("  MASTER VALIDATOR SCOREBOARD — 20 BENCHMARK CASES")
    print("=" * 90)
    print(f"  {'Validator Test Name':<45} | {'Status':<10}")
    print("  " + "-" * 60)

    all_passed = True
    for vname, passed in suite_results.items():
        status_str = "[PASS] PASS" if passed else "[FAIL] FAIL"
        if not passed:
            all_passed = False
        print(f"  {vname:<45} | {status_str}")

    print("  " + "=" * 60)
    if all_passed and len(case_files) == 20:
        print("  FINAL OUTCOME: 100% AUDIT READY (ALL 20 CASES PASSED ALL VALIDATORS)\n")
        return True
    else:
        print(f"  FINAL OUTCOME: AUDIT ISSUES DETECTED ({sum(1 for v in suite_results.values() if v)}/6 validators passed).\n")
        return False


if __name__ == "__main__":
    ok = run_all_validators()
    sys.exit(0 if ok else 1)
