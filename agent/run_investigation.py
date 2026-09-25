"""
Canonical Investigation Pipeline Entrypoint (agent/run_investigation.py)
TigerGraph Hacker House Goa 2026 — Agentic Fraud Investigation System

Unified, definitive CLI and API for running autonomous fraud investigations across:
  - 11-Agent CrewAI forensic architecture (Agents 1 through 11)
  - Live TigerGraph Cloud + Resilient Local Subgraph Hybrid Traversal
  - Graph-Aware Case Similarity (Text + Topology + Pattern)
  - Decoupled Uncertainty & Policy Gating (Bank Policy v1.0 Rules R1-R10)
  - Two-Stage Next-Best-Action Evolution ('initial' -> 'final' -> 'what_changed')
  - Institutional Sandbox Action Gateway Execution
  - Production-Compliant 3-Part JSON Submission Formatter ('case', 'sar', 'next_best_actions')

Usage:
  python -m agent.run_investigation --case-id HHG-001
  python -m agent.run_investigation --case-id HHG-005 --mode demo
  python -m agent.run_investigation --txn-id 3514030 --trigger-type risk_score
  python -m agent.run_investigation --all --mode fast
"""

import os
import sys
import json
import csv
import time
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.agent import FraudInvestigationAgent
from agent.eleven_agents_pipeline import ElevenAgentPipeline
from agent.case_formatter import CaseFormatter
from graph.tigergraph_tools import check_cloud_status
from agent.action_gateway import get_action_gateway


def load_benchmark_pack() -> Dict[str, Dict[str, str]]:
    """Loads benchmark case definitions from data/case_pack.csv."""
    pack_path = os.path.join(_PROJECT_ROOT, "data", "case_pack.csv")
    benchmarks = {}
    if os.path.exists(pack_path):
        with open(pack_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                benchmarks[row["case_id"]] = row
    return benchmarks


def run_canonical_investigation(
    case_id: str,
    flagged_txn_id: Optional[int] = None,
    trigger_type: Optional[str] = None,
    trigger_text: Optional[str] = None,
    simulated_customer_response: Optional[str] = None,
    mode: str = "full",
    output_dir: str = "cases",
    execute_sandbox: bool = True
) -> Dict[str, Any]:
    """
    Executes the canonical fraud investigation end-to-end.
    Returns the complete 3-part validated submission dictionary along with 11-agent telemetry.
    """
    benchmarks = load_benchmark_pack()
    is_benchmark = case_id in benchmarks or case_id.startswith("HHG-")

    # Resolve parameters from benchmark pack if applicable
    if case_id in benchmarks:
        b_info = benchmarks[case_id]
        if flagged_txn_id is None:
            flagged_txn_id = int(b_info["flagged_txn_id"])
        if trigger_type is None:
            trigger_type = b_info["trigger_type"]
        if trigger_text is None:
            trigger_text = b_info["trigger_text"]
    else:
        if flagged_txn_id is None:
            flagged_txn_id = 3514030
        if trigger_type is None:
            trigger_type = "risk_score"
        if trigger_text is None:
            trigger_text = f"Automated risk alert on transaction #{flagged_txn_id}."

    # Default customer response for customer disputes
    if simulated_customer_response is None and trigger_type == "customer_report":
        simulated_customer_response = "denied_fraud"

    print("\n" + "=" * 80)
    print(f"  TIGERGRAPH AGENTIC FRAUD INVESTIGATION — CANONICAL PIPELINE")
    print(f"  Case ID: {case_id} | Transaction: #{flagged_txn_id} | Mode: {mode.upper()}")
    print("=" * 80)

    # 1. Probe TigerGraph Cloud & Graph Resilience
    cloud_probe = check_cloud_status()
    cloud_state = "ONLINE" if cloud_probe.get("available") else f"FALLBACK ({cloud_probe.get('status', 'degraded')})"
    print(f"  [*] Graph Infrastructure: TigerGraph Hybrid Engine [{cloud_state}]")

    # 2. Execute 11-Agent Autonomous Forensic Pipeline
    print(f"  [*] Activating 11-Agent Autonomous Investigation Pipeline...")
    pipeline = ElevenAgentPipeline()
    agent_exec_res = pipeline.investigate(
        flagged_txn_id=flagged_txn_id,
        user_id=f"User_{flagged_txn_id}",
        trigger_type=trigger_type,
        trigger_text=trigger_text,
        case_id=case_id,
        customer_response=simulated_customer_response,
        mode=mode
    )

    # 3. Execute Core 8-Stage Domain Formatter for full README 3-part submission
    core_agent = FraudInvestigationAgent()
    case_obj, submission = core_agent.run_investigation(
        trigger_type=trigger_type,
        trigger_text=trigger_text,
        flagged_txn_id=flagged_txn_id,
        case_id=case_id,
        simulated_customer_response=simulated_customer_response,
        is_benchmark=is_benchmark
    )

    # Attach 11-Agent Telemetry and Frontend Report to submission
    submission["_eleven_agent_telemetry"] = {
        "pipeline_status": agent_exec_res.get("pipeline_status"),
        "pipeline_stages_completed": agent_exec_res.get("pipeline_stages_completed"),
        "telemetry_ms": agent_exec_res.get("telemetry"),
        "frontend_report": agent_exec_res.get("frontend_report")
    }

    # 4. Institutional Sandbox Action Gateway Dispatch
    c_inner = submission["case"]
    nba = submission["next_best_actions"]
    sar = submission["sar"]
    finals = nba.get("final", [])

    if execute_sandbox and finals:
        gateway = get_action_gateway()
        primary_action = finals[0]
        act_name = primary_action.get("action", "MONITOR_CARD")
        act_route = primary_action.get("route", "auto")

        card_list = c_inner.get("connected_card_ids") or ["CARD-4242"]
        card_id = card_list[0] if card_list else "CARD-4242"
        cust_id = c_inner.get("customer_id") or "CUST-101"

        print(f"  [*] Dispatching Action '{act_name}' ({act_route}) to Institutional Sandbox Gateway...")
        if act_route == "auto":
            gw_res = gateway.execute_action(
                action=act_name,
                case_id=case_id,
                card_id=card_id,
                customer_id=cust_id,
                authorized_by="SYSTEM_AUTONOMOUS",
                route="auto",
                reason=primary_action.get("reason", "")
            )
            print(f"      -> Gateway Response: {gw_res.get('execution_status')} | Card Status: {gw_res.get('new_card_status', 'ACTIVE')}")
        else:
            print(f"      -> Human-In-The-Loop Route ({act_route}): Paused in Human Approval Center pending sign-off.")

    # 5. Schema Validation
    formatter = CaseFormatter()
    try:
        formatter.validate_schema(submission)
        schema_status = "[PASS] 100% Schema Compliant (0 errors)"
    except Exception as e:
        schema_status = f"[FAIL] Schema Error: {e}"

    # 6. Persist to Disk
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{case_id}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)

    # 7. Print Executive Summary
    print("\n" + "-" * 80)
    print(f"  INVESTIGATION OUTCOME SUMMARY")
    print("-" * 80)
    print(f"  Case Status:        {c_inner.get('status')}")
    print(f"  Final Verdict:      {c_inner.get('verdict').upper()}")
    print(f"  Fraud Probability:  {c_inner.get('fraud_probability'):.2f}")
    print(f"  Confidence Level:   {c_inner.get('confidence_level')} (Uncertainty: {c_inner.get('uncertainty_score', 0):.2f})")
    print(f"  Detected Pattern:   {c_inner.get('pattern')}")
    print(f"  Financial Exposure: ${c_inner.get('exposure_usd', 0):,.2f} USD")
    print(f"  FinCEN SAR Filing:  {'MANDATED' if sar.get('file') else 'EXEMPT (Amount: $0)'}")
    print(f"  Next-Best-Actions:  {', '.join([a.get('action') + ' (' + a.get('route') + ')' for a in finals])}")
    print(f"  Schema Audit:       {schema_status}")
    print(f"  Artifact Saved:     {out_file}")
    print("=" * 80 + "\n")

    return submission


def main():
    parser = argparse.ArgumentParser(
        description="TigerGraph 11-Agent Fraud Investigation Pipeline Canonical Runner"
    )
    parser.add_argument("--case-id", type=str, default="HHG-001", help="Case ID to investigate (e.g., HHG-001)")
    parser.add_argument("--txn-id", type=int, default=None, help="Explicit Transaction ID override")
    parser.add_argument("--trigger-type", type=str, default=None, choices=["risk_score", "customer_report", "analyst_request"])
    parser.add_argument("--trigger-text", type=str, default=None, help="Trigger alert text")
    parser.add_argument("--customer-response", type=str, default=None, choices=["confirmed_authorized", "denied_fraud", "unresponsive"])
    parser.add_argument("--mode", type=str, default="full", choices=["full", "fast", "demo"], help="Execution mode")
    parser.add_argument("--all", action="store_true", help="Run benchmark across all 20 cases")
    parser.add_argument("--output-dir", type=str, default="cases", help="Output directory for case JSONs")

    args = parser.parse_args()

    if args.all:
        benchmarks = load_benchmark_pack()
        print(f"\n[Canonical Runner] Running all {len(benchmarks)} benchmark cases in {args.mode.upper()} mode...\n")
        t0 = time.time()
        for cid in sorted(benchmarks.keys()):
            run_canonical_investigation(
                case_id=cid,
                mode=args.mode,
                output_dir=args.output_dir
            )
        elapsed = time.time() - t0
        print(f"\n[Canonical Runner] All {len(benchmarks)} benchmark cases completed in {elapsed:.2f} seconds.")
    else:
        run_canonical_investigation(
            case_id=args.case_id,
            flagged_txn_id=args.txn_id,
            trigger_type=args.trigger_type,
            trigger_text=args.trigger_text,
            simulated_customer_response=args.customer_response,
            mode=args.mode,
            output_dir=args.output_dir
        )


if __name__ == "__main__":
    main()
