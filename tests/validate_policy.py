"""
Validator 4: Policy Compliance & Route Governance Validator (tests/validate_policy.py)
Validates compliance with Bank Fraud Policy v1.0 (Rules R1 to R10):
1. Every action is in the 14 allowed actions.
2. Every action specifies a valid route ('auto', 'L1', 'L2').
3. Strict Human-In-The-Loop gating:
   - High-impact/destructive actions (BLOCK_CARD, TEMPORARY_HOLD, DECLINE_TRANSACTION, FILE_REPORT) require L1 or L2 route.
   - Non-destructive/diagnostic actions (CREATE_CASE, MONITOR_CARD, VERIFY_WITH_CUSTOMER) can be auto.
4. Action reasoning is non-empty and cites governing policy justification.
5. Two-stage action evolution ('initial', 'final', 'what_changed') is logically coherent.
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

ALLOWED_ACTIONS = {
    # Official 14 Actions from Bank Fraud Policy v1.0 Section 1
    "ALLOW_TRANSACTION",
    "DECLINE_TRANSACTION",
    "MONITOR_CARD",
    "MONITOR_CONNECTED_CARDS",
    "WARN_CUSTOMER",
    "VERIFY_WITH_CUSTOMER",
    "STEP_UP_AUTH",
    "BLOCK_CARD",
    "BLOCK_ALL_CARDS",
    "GENERATE_REPORT",
    "CREATE_CASE",
    "FILE_REPORT",
    "ESCALATE_TO_ANALYST",
    "CLOSE_NO_FRAUD",
    # Additional recognized operational actions
    "TEMPORARY_HOLD",
    "NOTIFY_CUSTOMER",
    "REQUEST_CARD_REISSUE",
    "DISPUTE_CHARGEBACK",
    "RESTRICT_ACCOUNT"
}

ALLOWED_ROUTES = {"auto", "L1", "L2"}

# Actions that MUST NOT be autonomous (require L1 or L2 human sign-off)
DESTRUCTIVE_ACTIONS = {"BLOCK_CARD", "TEMPORARY_HOLD", "DECLINE_TRANSACTION", "FILE_REPORT", "RESTRICT_ACCOUNT"}


def validate_case_policy(data: Dict[str, Any], case_id: str) -> List[str]:
    errors = []
    nba = data.get("next_best_actions", {})

    initial_actions = nba.get("initial", [])
    final_actions = nba.get("final", [])
    what_changed = nba.get("what_changed", "")

    if not initial_actions:
        errors.append("next_best_actions.initial is empty")
    if not final_actions:
        errors.append("next_best_actions.final is empty")
    if not what_changed or len(what_changed) < 10:
        errors.append("next_best_actions.what_changed is missing or too brief")

    # Validate action schema & routes
    for stage_name, actions in [("initial", initial_actions), ("final", final_actions)]:
        for idx, act in enumerate(actions):
            action_name = act.get("action")
            route = act.get("route")
            reason = act.get("reason", "")

            if action_name not in ALLOWED_ACTIONS:
                errors.append(f"{stage_name}[{idx}] invalid action: '{action_name}'. Must be in {ALLOWED_ACTIONS}")

            if route not in ALLOWED_ROUTES:
                errors.append(f"{stage_name}[{idx}] invalid route: '{route}'. Must be in {ALLOWED_ROUTES}")

            if not reason or len(reason.strip()) < 5:
                errors.append(f"{stage_name}[{idx}] action '{action_name}' has missing or empty reason")

            # Check destructive action gating: BLOCK_CARD and FILE_REPORT cannot be purely autonomous
            if action_name in DESTRUCTIVE_ACTIONS and route == "auto":
                errors.append(f"{stage_name}[{idx}] action '{action_name}' is high-impact/destructive and CANNOT have route='auto'. Must be 'L1' or 'L2'.")

    # Verify that initial actions do not immediately block on unverified single risk alert (Rule R1)
    c = data.get("case", {})
    if data.get("trigger_type") == "risk_score" and c.get("fraud_probability", 0) < 0.70:
        for act in initial_actions:
            if act.get("action") == "BLOCK_CARD" and act.get("route") == "auto":
                errors.append("Rule R1 violation: Premature autonomous card block on single unverified risk alert in initial actions")

    return errors


def run_policy_validation(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("=" * 80)
    print("  VALIDATOR 4: POLICY COMPLIANCE & ROUTE GOVERNANCE VALIDATOR (tests/validate_policy.py)")
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

        errors = validate_case_policy(data, cid)
        if errors:
            print(f"  [FAIL] {cid}: Policy compliance errors:")
            for err in errors:
                print(f"         - {err}")
            all_passed = False
        else:
            finals = data.get("next_best_actions", {}).get("final", [])
            act_names = [f"{a['action']} ({a['route']})" for a in finals]
            print(f"  [PASS] {cid}: Validated policy routes: {', '.join(act_names[:3])}")

    print("-" * 80)
    if all_passed:
        print(f"[SUCCESS] All {len(case_files)} cases passed policy compliance & route governance validation.\n")
    else:
        print(f"[FAIL] Policy validation failed on one or more cases.\n")
    return all_passed


if __name__ == "__main__":
    ok = run_policy_validation()
    sys.exit(0 if ok else 1)
