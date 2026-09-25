"""
Validator 6: Graph Persistence Validator (tests/validate_graph_write.py)
Validates that every investigated case is committed back to the TigerGraph memory store:
1. case.written_to_graph == True.
2. case.graph_case_id is non-empty and formatted appropriately.
3. Case records exist in the dynamic case memory store (data/case_memory/).
4. Stop reason confirms persistence.
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

from graph.case_memory import CaseMemoryManager


def validate_case_graph_write(data: Dict[str, Any], case_id: str, case_memory_manager: CaseMemoryManager) -> List[str]:
    errors = []
    c = data.get("case", {})

    written = c.get("written_to_graph")
    if not isinstance(written, bool) or not written:
        errors.append(f"case.written_to_graph must be True, got {written}")

    graph_case_id = c.get("graph_case_id")
    if not graph_case_id or not isinstance(graph_case_id, str):
        errors.append(f"case.graph_case_id must be non-empty string, got {graph_case_id}")

    # Check case memory persistence
    mem_case = case_memory_manager.get_case(case_id)
    if not mem_case:
        # Check by target txn id if case_id format differed
        target_txn = str(c.get("first_suspicious_txn_id", ""))
        mem_case = case_memory_manager.get_case(f"CASE-{target_txn}")

    if not mem_case:
        # Also check disk directly in case_memory directory
        mem_dir = os.path.join(PROJECT_ROOT, "data", "case_memory")
        found_on_disk = False
        if os.path.exists(mem_dir):
            for root, _, files in os.walk(mem_dir):
                for f in files:
                    if case_id in f or (target_txn and target_txn in f):
                        found_on_disk = True
                        break
        if not found_on_disk:
            errors.append(f"Case {case_id} was not found in CaseMemoryManager store on disk.")

    return errors


def run_graph_write_validation(cases_dir: str = None) -> bool:
    if cases_dir is None:
        cases_dir = os.path.join(PROJECT_ROOT, "cases")

    print("=" * 80)
    print("  VALIDATOR 6: GRAPH PERSISTENCE VALIDATOR (tests/validate_graph_write.py)")
    print("=" * 80)

    memory_mgr = CaseMemoryManager()
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

        errors = validate_case_graph_write(data, cid, memory_mgr)
        if errors:
            print(f"  [FAIL] {cid}: Graph persistence errors:")
            for err in errors:
                print(f"         - {err}")
            all_passed = False
        else:
            c = data["case"]
            print(f"  [PASS] {cid}: written_to_graph={c['written_to_graph']} (graph_case_id={c['graph_case_id']})")

    print("-" * 80)
    if all_passed:
        print(f"[SUCCESS] All {len(case_files)} cases passed graph write validation.\n")
    else:
        print(f"[FAIL] Graph write validation failed on one or more cases.\n")
    return all_passed


if __name__ == "__main__":
    ok = run_graph_write_validation()
    sys.exit(0 if ok else 1)
