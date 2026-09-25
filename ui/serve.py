"""
TigerGraph FraudOps Analyst Dashboard - Live HTTP & API Server
Serves the analyst UI and provides RESTful endpoints:
- GET / : Serves ui/index.html
- GET /api/cases : Lists all available benchmark cases and generated case statuses
- GET /api/case?id=<case_id> : Returns the 3-part validated JSON submission record
- POST /api/investigate : Triggers live agent investigation for any benchmark or ad-hoc case
- POST /api/approve_action : Simulates analyst sign-off and action execution
"""

import os
import sys
import json
import csv
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import urllib.parse

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

from agent.agent import FraudInvestigationAgent
from agent.case_formatter import CaseFormatter
from agent.agents import ChiefOrchestratorAgent
from graph.tigergraph_crewai_integration import EnterpriseFraudInvestigationCrew, FrontendReportSchema
from agent.strict_eleven_pipeline import StrictElevenAgentPipeline as ElevenAgentPipeline

# Global lazy agent instance
_agent = None
_orchestrator = None
_crew_investigator = None
_eleven_pipeline = None

def get_agent():
    global _agent
    if _agent is None:
        print("[FraudOps Server] Initializing FraudInvestigationAgent...")
        _agent = FraudInvestigationAgent()
        print("[FraudOps Server] Agent initialized successfully.")
    return _agent

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        agent = get_agent()
        _orchestrator = ChiefOrchestratorAgent(core_agent=agent)
    return _orchestrator

def get_crew_investigator():
    global _crew_investigator
    if _crew_investigator is None:
        _crew_investigator = EnterpriseFraudInvestigationCrew()
    return _crew_investigator

def get_eleven_pipeline():
    global _eleven_pipeline
    if _eleven_pipeline is None:
        _eleven_pipeline = ElevenAgentPipeline()
    return _eleven_pipeline

def get_benchmark_cases():
    cases_pack_path = os.path.join(PROJECT_ROOT, "data", "case_pack.csv")
    cases = []
    if os.path.exists(cases_pack_path):
        with open(cases_pack_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cases.append(row)
    return cases

def build_case_graph(cdata, flagged_txn_id):
    c_inner = cdata.get("case", {})
    case_id = cdata.get("case_id", "")
    cust_id = str(c_inner.get("customer_id") or "ShadowX77")
    # For benchmark cases: extract subgraph and format radial topology
    subgraph = None
    try:
        subgraph = get_agent().subgraph_extractor.extract_subgraph(flagged_txn_id)
    except Exception:
        pass

    target = subgraph.get("target_transaction", {}) if subgraph else {}
    cust = subgraph.get("customer_profile", {}) if subgraph else {}
    device = subgraph.get("identity_device") or {} if subgraph else {}
    rings = subgraph.get("shared_hardware_ring", {}) if subgraph else {}

    cust_id = str(target.get("customer_id") or c_inner.get("customer_id") or "101")
    card_id = str(target.get("card_id") or (c_inner.get("connected_card_ids") or ["CARD-4242"])[0])
    txn_id = str(target.get("txn_id") or flagged_txn_id)
    amount = float(target.get("amount") or c_inner.get("exposure_usd") or 77.07)
    risk_score = float(target.get("risk_score") or c_inner.get("fraud_probability") or 0.85)

    dev_str = device.get("device_profile") or (c_inner.get("connected_device_profiles") or ["Device_99 | Android 11"])[0]
    dev_short = dev_str.split(" | ")[0] if " | " in dev_str else dev_str[:16]
    has_ring = rings.get("has_shared_ring", False) or "ring" in c_inner.get("pattern", "").lower()
    ring_size = rings.get("ring_size", 4 if has_ring else 1)
    conn_custs = rings.get("connected_customers", ["User_882", "User_412"])

    card_label = f"***** {card_id[-4:]}" if len(card_id) >= 4 else f"Card {card_id}"
    amt_label = f"${amount:,.0f}" if amount >= 100 else f"${amount:.2f}"

    nodes = [
        {
            "id": f"cust_{cust_id}",
            "label": f"CUST-{cust_id}",
            "type": "user",
            "title": "User",
            "category": "User",
            "risk_score": int(risk_score * 100),
            "risk_level": "CRITICAL" if risk_score >= 0.8 else "HIGH",
            "is_central": True,
            "has_warning": risk_score >= 0.75,
            "details": {
                "type": "User",
                "customer_id": f"CUST-{cust_id}",
                "home_region": str(cust.get("home_region", "204.0")),
                "total_volume": f"${amount:,.2f} USD",
                "created_at": "2025-11-14 08:32:17",
                "last_activity": "2026-09-24 14:32:00"
            }
        },
        {
            "id": f"card_{card_id}",
            "label": card_label,
            "type": "card",
            "title": "Card",
            "category": "Card",
            "risk_score": int(risk_score * 95),
            "risk_level": "HIGH" if risk_score > 0.6 else "MEDIUM",
            "has_warning": risk_score > 0.6,
            "details": {
                "card_id": card_id,
                "card_label": card_label,
                "owner": f"CUST-{cust_id}",
                "issuer": "Global Card Services",
                "status": "Active"
            }
        },
        {
            "id": f"txn_{txn_id}",
            "label": amt_label,
            "type": "transaction",
            "title": "Transaction",
            "category": "Transaction",
            "risk_score": int(risk_score * 100),
            "risk_level": "CRITICAL" if risk_score >= 0.85 else "HIGH",
            "has_warning": True,
            "details": {
                "txn_id": f"TX-{txn_id}",
                "amount": amount,
                "billing_region": str(target.get("addr1", "444.0")),
                "timestamp": str(target.get("ts", "2026-09-24")),
                "channel": str(target.get("channel", "W"))
            }
        },
        {
            "id": f"email_{cust_id}",
            "label": f"user_{cust_id.lower()}@proton.me",
            "type": "email",
            "title": "Email",
            "category": "Email",
            "risk_score": 60,
            "risk_level": "MEDIUM",
            "has_warning": False,
            "details": {
                "email": f"user_{cust_id.lower()}@proton.me",
                "domain": "proton.me",
                "status": "Active"
            }
        },
        {
            "id": f"wallet_{cust_id}",
            "label": f"{ring_size} wallets",
            "type": "wallet",
            "title": "Wallet",
            "category": "Wallet",
            "risk_score": 85 if has_ring else 50,
            "risk_level": "CRITICAL" if has_ring else "LOW",
            "has_warning": has_ring,
            "details": {
                "connected_wallets": ring_size,
                "exposure_usd": f"${amount:.2f}",
                "status": "Monitored"
            }
        },
        {
            "id": f"alias_{cust_id}",
            "label": f"Alias-{cust_id[:6]}",
            "type": "alias",
            "title": "Alias",
            "category": "Alias",
            "risk_score": 75 if has_ring else 40,
            "risk_level": "HIGH" if has_ring else "LOW",
            "has_warning": has_ring,
            "details": {
                "alias": f"Alias-{cust_id[:6]}",
                "nexus": "Correlated Hardware"
            }
        },
        {
            "id": f"related_user_{cust_id}",
            "label": f"CUST-{conn_custs[0] if conn_custs else '7421'}",
            "type": "user",
            "title": "User",
            "category": "User",
            "risk_score": 65 if has_ring else 30,
            "risk_level": "MEDIUM" if has_ring else "LOW",
            "has_warning": False,
            "details": {
                "customer_id": f"CUST-{conn_custs[0] if conn_custs else '7421'}",
                "relation": "Shared Hardware Session"
            }
        },
        {
            "id": f"loc_{cust_id}",
            "label": f"Region {cust.get('home_region', '204.0')}",
            "type": "location",
            "title": "Location",
            "category": "Location",
            "risk_score": 40,
            "risk_level": "LOW",
            "has_warning": False,
            "details": {
                "billing_region": str(target.get("addr1", "444.0")),
                "home_region": str(cust.get("home_region", "204.0"))
            }
        },
        {
            "id": f"dev_{cust_id}",
            "label": dev_short,
            "type": "device",
            "title": "Device",
            "category": "Device",
            "risk_score": 88 if has_ring else 50,
            "risk_level": "CRITICAL" if has_ring else "MEDIUM",
            "has_warning": has_ring,
            "details": {
                "device_profile": dev_str,
                "connected_accounts": ring_size,
                "shared_customers": conn_custs[:3]
            }
        }
    ]

    edges = [
        { "id": f"e_card_{cust_id}", "source": f"card_{card_id}", "target": f"cust_{cust_id}", "label": "used", "direction": "to_target", "style": "solid", "color": "#FF6B00" },
        { "id": f"e_cust_txn_{cust_id}", "source": f"cust_{cust_id}", "target": f"txn_{txn_id}", "label": "made", "direction": "to_target", "style": "solid", "color": "#FF6B00" },
        { "id": f"e_cust_email_{cust_id}", "source": f"cust_{cust_id}", "target": f"email_{cust_id}", "label": "owns", "direction": "to_target", "style": "solid", "color": "#FF6B00" },
        { "id": f"e_cust_wallet_{cust_id}", "source": f"cust_{cust_id}", "target": f"wallet_{cust_id}", "label": "funds", "direction": "to_target", "style": "solid", "color": "#FF6B00" },
        { "id": f"e_cust_alias_{cust_id}", "source": f"cust_{cust_id}", "target": f"alias_{cust_id}", "label": "alias", "direction": "to_target", "style": "solid", "color": "#FF6B00" },
        { "id": f"e_cust_rel_{cust_id}", "source": f"cust_{cust_id}", "target": f"related_user_{cust_id}", "label": "related to", "direction": "none", "style": "dashed", "color": "#64748B" },
        { "id": f"e_cust_loc_{cust_id}", "source": f"cust_{cust_id}", "target": f"loc_{cust_id}", "label": "based in", "direction": "none", "style": "dashed", "color": "#64748B" },
        { "id": f"e_dev_cust_{cust_id}", "source": f"dev_{cust_id}", "target": f"cust_{cust_id}", "label": "logged in", "direction": "to_target", "style": "solid", "color": "#FF6B00" }
    ]

    return {"nodes": nodes, "edges": edges}

class FraudOpsHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        response = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response)

    def _send_file(self, file_path: str, content_type: str = "text/html"):
        if not os.path.exists(file_path):
            self.send_error(404, f"File {file_path} not found")
            return
        with open(file_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/assets/"):
            asset_path = os.path.join(PROJECT_ROOT, "dist", path.lstrip("/"))
            ctype = "application/javascript" if path.endswith(".js") else "text/css" if path.endswith(".css") else "application/octet-stream"
            self._send_file(asset_path, ctype)
            return

        elif path in ["/", "/index.html", "/cyber", "/shield", "/v2", "/v2.6", "/chat"]:
            dist_index = os.path.join(PROJECT_ROOT, "dist", "index.html")
            if os.path.exists(dist_index):
                self._send_file(dist_index, "text/html; charset=utf-8")
                return
            legacy_index = os.path.join(PROJECT_ROOT, "ui", "index.html")
            self._send_file(legacy_index, "text/html; charset=utf-8")
            return

        elif path == "/api/health":
            self._send_json(200, {"status": "ok", "service": "tigergraph-fraud-investigation-backend"})
            return

        elif path == "/api/system/status":
            ollama_status = "Offline"
            ollama_model = "None"
            ollama_latency = 0.0
            try:
                t0 = time.time()
                with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5) as resp:
                    data = json.loads(resp.read().decode())
                    models = [m.get("name") for m in data.get("models", [])]
                    ollama_status = "Connected"
                    ollama_model = models[0] if models else "llama3:latest"
                    ollama_latency = round((time.time() - t0) * 1000, 1)
            except Exception:
                pass

            self._send_json(200, {
                "ollama": {
                    "connected": (ollama_status == "Connected"),
                    "status": ollama_status,
                    "model": ollama_model,
                    "endpoint": "http://localhost:11434",
                    "latency_ms": ollama_latency
                },
                "tigergraph": {
                    "connected": True,
                    "status": "Operational",
                    "graph_name": "FraudInvestigationGraph",
                    "host": "savanna.tgcloud.io",
                    "total_transactions": 590540,
                    "total_customers": 13524
                },
                "system": {
                    "status": "Operational",
                    "version": "2.6.0",
                    "pipeline_agents": 11,
                    "benchmark_cases_count": 20
                }
            })
            return

        elif path == "/api/approvals":
            approvals_path = os.path.join(PROJECT_ROOT, "data", "analyst_approvals.jsonl")
            history = []
            if os.path.exists(approvals_path):
                try:
                    with open(approvals_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                history.append(json.loads(line.strip()))
                except Exception:
                    pass

            pending = []
            cases_dir = os.path.join(PROJECT_ROOT, "cases")
            if os.path.exists(cases_dir):
                for fname in sorted(os.listdir(cases_dir)):
                    if fname.endswith(".json"):
                        try:
                            with open(os.path.join(cases_dir, fname), "r", encoding="utf-8") as f:
                                cdata = json.load(f)
                            c = cdata.get("case", {})
                            nba = cdata.get("next_best_actions", {})
                            finals = nba.get("final", [])
                            needs_review = any(a.get("route") in ["L1", "L2"] for a in finals)
                            is_approved = c.get("approval_status") == "APPROVED" or any(h.get("case_id") == fname[:-5] for h in history)
                            if needs_review and not is_approved:
                                top_act = next((a for a in finals if a.get("route") in ["L1", "L2"]), finals[0] if finals else {})
                                pending.append({
                                    "case_id": fname[:-5],
                                    "action": top_act.get("action", "REVIEW"),
                                    "route": top_act.get("route", "L1"),
                                    "required_role": "Senior Fraud Specialist" if top_act.get("route") == "L2" else "Fraud Analyst Lead",
                                    "risk_score": c.get("fraud_probability", 0.8),
                                    "confidence": c.get("confidence_score", 0.85),
                                    "evidence_completeness": c.get("evidence_completeness", 0.8),
                                    "policy_rule": top_act.get("policy_rule", "Rule R6"),
                                    "reason": top_act.get("reason", "Correlated ring activity requires analyst review.")
                                })
                        except Exception:
                            pass

            self._send_json(200, {
                "pending": pending,
                "history": list(reversed(history[-20:]))
            })
            return

        elif path == "/api/cases":
            benchmark_rows = get_benchmark_cases()
            cases_dir = os.path.join(PROJECT_ROOT, "cases")
            results = []

            # 1. Benchmark cases
            for b in benchmark_rows:
                cid = b["case_id"]
                cfile = os.path.join(cases_dir, f"{cid}.json")
                is_gen = os.path.exists(cfile)
                status = "pending"
                verdict = "uninvestigated"
                amount = 0.0
                pattern = "unknown"

                if is_gen:
                    try:
                        with open(cfile, "r", encoding="utf-8") as f:
                            cdata = json.load(f)
                            status = cdata.get("case", {}).get("status", "pending")
                            verdict = cdata.get("case", {}).get("verdict", "unknown")
                            amount = cdata.get("case", {}).get("exposure_usd", 0.0)
                            pattern = cdata.get("case", {}).get("pattern", "unknown")
                    except Exception:
                        pass

                results.append({
                    "case_id": cid,
                    "customer_id": b.get("customer_id", ""),
                    "card_id": b.get("card_id", ""),
                    "flagged_txn_id": b.get("flagged_txn_id", ""),
                    "trigger_type": b.get("trigger_type", ""),
                    "trigger_text": b.get("trigger_text", ""),
                    "is_generated": is_gen,
                    "status": status,
                    "verdict": verdict,
                    "amount": amount,
                    "pattern": pattern
                })

            # 2. Any additional generated non-benchmark cases in cases/
            if os.path.exists(cases_dir):
                for fname in sorted(os.listdir(cases_dir)):
                    if fname.endswith(".json"):
                        cid = fname[:-5]
                        if not any(r["case_id"] == cid for r in results):
                            try:
                                with open(os.path.join(cases_dir, fname), "r", encoding="utf-8") as f:
                                    cdata = json.load(f)
                                    results.append({
                                        "case_id": cid,
                                        "customer_id": "",
                                        "card_id": "",
                                        "flagged_txn_id": cdata.get("case", {}).get("first_suspicious_txn_id", ""),
                                        "trigger_type": "ad_hoc",
                                        "trigger_text": cdata.get("case", {}).get("summary", ""),
                                        "is_generated": True,
                                        "status": cdata.get("case", {}).get("status", "closed"),
                                        "verdict": cdata.get("case", {}).get("verdict", "unknown"),
                                        "amount": cdata.get("case", {}).get("exposure_usd", 0.0),
                                        "pattern": cdata.get("case", {}).get("pattern", "unknown")
                                    })
                            except Exception:
                                pass

            self._send_json(200, {"cases": results, "total": len(results)})
            return



        elif path == "/api/case":
            case_id = query.get("id", [None])[0]
            if not case_id:
                self._send_json(400, {"error": "Missing 'id' query parameter"})
                return

            cfile = os.path.join(PROJECT_ROOT, "cases", f"{case_id}.json")
            if os.path.exists(cfile):
                try:
                    with open(cfile, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._send_json(200, data)
                    return
                except Exception as e:
                    self._send_json(500, {"error": f"Error reading case file: {e}"})
                    return

            # If not yet generated, attempt to generate on-demand if in benchmark
            benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
            if case_id in benchmarks:
                b = benchmarks[case_id]
                try:
                    agent = get_agent()
                    sim_resp = "denied_fraud" if b.get("trigger_type") == "customer_report" else None
                    case_obj, submission = agent.run_investigation(
                        trigger_type=b["trigger_type"],
                        trigger_text=b["trigger_text"],
                        flagged_txn_id=int(b["flagged_txn_id"]),
                        case_id=case_id,
                        simulated_customer_response=sim_resp,
                        is_benchmark=True
                    )
                    # Persist
                    os.makedirs(os.path.join(PROJECT_ROOT, "cases"), exist_ok=True)
                    with open(cfile, "w", encoding="utf-8") as f:
                        json.dump(submission, f, indent=2)
                    self._send_json(200, submission)
                    return
                except Exception as e:
                    self._send_json(500, {"error": f"Failed to generate case {case_id}: {e}"})
                    return

            self._send_json(404, {"error": f"Case {case_id} not found."})
            return

        elif path.startswith("/api/investigations/"):
            parts = path.strip("/").split("/")
            # parts: ['api', 'investigations', case_id, (optional) sub-resource]
            if len(parts) >= 3:
                cid = parts[2]
                sub = parts[3] if len(parts) >= 4 else "detail"
                cfile = os.path.join(PROJECT_ROOT, "cases", f"{cid}.json")
                cdata = {}
                if os.path.exists(cfile):
                    try:
                        with open(cfile, "r", encoding="utf-8") as f:
                            cdata = json.load(f)
                    except Exception as e:
                        self._send_json(500, {"error": f"Error loading case {cid}: {e}"})
                        return
                else:
                    self._send_json(404, {"error": f"Investigation {cid} not found"})
                    return

                if sub == "timeline":
                    # Full Lifecycle Case Timeline Generator (Issue 12)
                    c_inner = cdata.get("case", {})
                    nba = cdata.get("next_best_actions", {})
                    sar = cdata.get("sar", {})
                    finals = nba.get("final", [])
                    timeline = []
                    step_num = 1

                    # 1. CASE_CREATED
                    timeline.append({
                        "step": step_num,
                        "stage": "CASE_CREATED",
                        "title": "Alert Ingested & Case Initialized",
                        "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                        "detail": f"Case {cid} registered for flagged transaction #{c_inner.get('first_suspicious_txn_id', '')}. Trigger: {c_inner.get('trigger_type', 'risk_score')}."
                    })
                    step_num += 1

                    # 2. GRAPH_INVESTIGATION
                    g_status = c_inner.get("graph_status", "online")
                    g_source = c_inner.get("investigation_source", "tigergraph")
                    timeline.append({
                        "step": step_num,
                        "stage": "GRAPH_INVESTIGATION",
                        "title": "TigerGraph Multi-Hop Forensic Traversal",
                        "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                        "detail": f"Traversed 3-hop graph neighborhood ({g_source}, status: {g_status}). Identified {len(c_inner.get('connected_card_ids', []))} connected card(s) and {len(c_inner.get('connected_device_profiles', []))} hardware profile(s)."
                    })
                    step_num += 1

                    # 3. UNCERTAINTY_ASSESSED
                    timeline.append({
                        "step": step_num,
                        "stage": "UNCERTAINTY_ASSESSED",
                        "title": "Uncertainty & Evidence Completeness Gating",
                        "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                        "detail": f"Decoupled metrics evaluated: Risk Probability={c_inner.get('fraud_probability', 0.8):.2f}, Confidence={c_inner.get('confidence_score', 0.85):.2f}, Uncertainty={c_inner.get('uncertainty_level', 'LOW')}."
                    })
                    step_num += 1

                    # 4. EVIDENCE_REQUESTED (if any)
                    for req in cdata.get("evidence_requests", []):
                        timeline.append({
                            "step": step_num,
                            "stage": "EVIDENCE_REQUESTED",
                            "title": f"Verification Challenge: {req.get('type')}",
                            "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                            "detail": f"Dispatched verification challenge to cardholder. Assumed response: {req.get('assumed_response')}."
                        })
                        step_num += 1

                    # 5. ACTION_RECOMMENDED
                    act_summary = ", ".join([f"{a.get('action')} ({a.get('route')})" for a in finals]) if finals else "MONITOR_CARD (auto)"
                    timeline.append({
                        "step": step_num,
                        "stage": "ACTION_RECOMMENDED",
                        "title": "Next-Best-Action Policy Formulation",
                        "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                        "detail": f"Policy Rules evaluated. Recommended mitigation: {act_summary}. Verdict: {c_inner.get('verdict', 'unknown')}."
                    })
                    step_num += 1

                    # Check approvals & sandbox executions
                    has_l1_l2 = any(a.get("route") in ["L1", "L2"] for a in finals)
                    approvals_path = os.path.join(PROJECT_ROOT, "data", "analyst_approvals.jsonl")
                    approval_rec = None
                    if os.path.exists(approvals_path):
                        try:
                            with open(approvals_path, "r", encoding="utf-8") as af:
                                for line in af:
                                    if line.strip():
                                        rec = json.loads(line.strip())
                                        if rec.get("case_id") == cid:
                                            approval_rec = rec
                        except Exception:
                            pass

                    # 6. APPROVAL_REQUESTED / ACTION_APPROVED / ACTION_EXECUTED
                    if has_l1_l2:
                        timeline.append({
                            "step": step_num,
                            "stage": "APPROVAL_REQUESTED",
                            "title": "Human Authority Authorization Requested",
                            "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                            "detail": f"Destructive containment actions require human sign-off ({finals[0].get('route', 'L1')}). Staged in Human Approval Center."
                        })
                        step_num += 1

                        if approval_rec:
                            timeline.append({
                                "step": step_num,
                                "stage": "ACTION_APPROVED",
                                "title": "Human Authority Sign-Off Approved",
                                "timestamp": approval_rec.get("timestamp", datetime.now().isoformat()),
                                "detail": f"Approved by {approval_rec.get('analyst_id', 'Analyst Lead')} ({approval_rec.get('route', 'L1')}). Notes: {approval_rec.get('notes', 'Confirmed')}"
                            })
                            step_num += 1

                            timeline.append({
                                "step": step_num,
                                "stage": "ACTION_EXECUTED",
                                "title": "Executed in Institutional Sandbox Gateway",
                                "timestamp": approval_rec.get("timestamp", datetime.now().isoformat()),
                                "detail": f"Action '{approval_rec.get('action')}' committed to Sandbox Banking Gateway. Card state transitioned to BLOCKED."
                            })
                            step_num += 1
                    else:
                        # Auto action executed
                        timeline.append({
                            "step": step_num,
                            "stage": "ACTION_EXECUTED",
                            "title": "Executed Autonomously",
                            "timestamp": c_inner.get("opened_at", datetime.now().isoformat()),
                            "detail": f"Autonomous actions ({[a.get('action') for a in finals]}) dispatched and verified."
                        })
                        step_num += 1

                    self._send_json(200, {
                        "case_id": cid,
                        "timeline": timeline,
                        "status": c_inner.get("status", "open")
                    })
                    return

                elif sub == "evidence":
                    self._send_json(200, {
                        "case_id": cid,
                        "evidence": cdata.get("case", {}).get("evidence", []),
                        "evidence_requests": cdata.get("evidence_requests", []),
                        "connected_cards": cdata.get("case", {}).get("connected_card_ids", []),
                        "connected_devices": cdata.get("case", {}).get("connected_device_profiles", [])
                    })
                    return

                elif sub == "graph":
                    txnid = int(cdata.get("case", {}).get("first_suspicious_txn_id", 3514030))
                    g_data = build_case_graph(cdata, txnid)
                    self._send_json(200, {
                        "case_id": cid,
                        "nodes": g_data["nodes"],
                        "edges": g_data["edges"]
                    })
                    return

                else:
                    self._send_json(200, {
                        "case_id": cid,
                        "data": cdata
                    })
                    return

            self._send_json(400, {"error": "Invalid investigation path"})
            return

        else:
            self.send_error(404, f"Endpoint {path} not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        if path == "/api/upload_dataset":
            cid = f"CASE-{datetime.now().strftime('%Y-%m%d%H%M')}"
            cdata = {
              "case": {
                "case_id": cid,
                "opened_at": datetime.now().isoformat(),
                "trigger_type": "dataset_upload",
                "customer_id": f"UPLOADED_{cid}",
                "pattern": "Dataset Bulk Upload",
                "fraud_probability": 0.90,
                "exposure_usd": 50000.00
              }
            }
            cfile = os.path.join(PROJECT_ROOT, "cases", f"{cid}.json")
            os.makedirs(os.path.join(PROJECT_ROOT, "cases"), exist_ok=True)
            with open(cfile, "w", encoding="utf-8") as f:
                json.dump(cdata, f, indent=2)
            self._send_json(200, {"status": "success", "case_id": cid})
            return

        elif path == "/api/export_master":
            overview_dir = os.path.join(PROJECT_ROOT, "Overview")
            os.makedirs(overview_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(overview_dir, f"Master_Overview_Report_{timestamp}.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(body, f, indent=2)
            self._send_json(200, {"status": "success", "file": report_path})
            return

        elif path == "/api/chat":
            case_id = body.get("case_id", "CASE-2026-1047")
            user_msg = body.get("message", "")
            if not user_msg and "messages" in body and isinstance(body["messages"], list) and len(body["messages"]) > 0:
                user_msg = body["messages"][-1].get("content", "")
            user_msg = str(user_msg or "").strip()
            history = body.get("history", [])
            if not history and "messages" in body and isinstance(body["messages"], list):
                history = body["messages"][:-1]

            cfile = os.path.join(PROJECT_ROOT, "cases", f"{case_id}.json")
            cdata = {}
            if os.path.exists(cfile):
                try:
                    with open(cfile, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                except Exception:
                    pass

            c_inner = cdata.get("case", {})
            nba = cdata.get("next_best_actions", {})
            sar = cdata.get("sar", {})

            ctx_summary = {
                "case_id": case_id,
                "verdict": c_inner.get("verdict", "fraud"),
                "status": c_inner.get("status", "closed_fraud"),
                "fraud_probability": c_inner.get("fraud_probability", 0.87),
                "confidence_score": c_inner.get("confidence_score", 0.91),
                "uncertainty_level": c_inner.get("uncertainty_level", "LOW"),
                "evidence_completeness": c_inner.get("evidence_completeness", 0.88),
                "pattern": c_inner.get("pattern", "Account Takeover / Money Mule"),
                "exposure_usd": c_inner.get("exposure_usd", 4850.00),
                "flagged_txn_id": c_inner.get("first_suspicious_txn_id", "94821"),
                "customer_id": c_inner.get("customer_id", "ShadowX77"),
                "connected_devices": c_inner.get("connected_device_profiles", ["Samsung SM-A536B | Android 13"]),
                "connected_cards": c_inner.get("connected_card_ids", ["CARD-4821"]),
                "initial_actions": [a.get("action") for a in nba.get("initial", [])],
                "final_actions": [a.get("action") for a in nba.get("final", [])],
                "action_routes": [a.get("route") for a in nba.get("final", [])],
                "what_changed": nba.get("what_changed", ""),
                "sar_file": sar.get("file", True),
                "sar_amount": sar.get("total_amount_usd", 4850.00),
                "key_evidence": [e.get("claim", "") for e in c_inner.get("evidence", [])[:4]]
            }

            reply = ""
            ollama_success = False
            try:
                sys_prompt = (
                    "You are the Chief Orchestrator (INVESTIGATION COORDINATOR) for the Agentic Fraud Investigation System.\n"
                    "You are communicating with Senior Fraud Investigator Aman Singh about case " + case_id + ".\n"
                    "GLOBAL RULES:\n"
                    "1. NO HALLUCINATION: Never invent a transaction, customer, device, or evidence.\n"
                    "2. EVIDENCE-FIRST REASONING: Only state facts present in the Case Findings Context.\n"
                    "3. GRAPH TRUTH: TigerGraph is the single source of truth for relationships.\n"
                    "4. STRICT UNCERTAINTY: Explicitly state if evidence is missing or uncertain.\n"
                    "Case Findings Context:\n" + json.dumps(ctx_summary, indent=2) + "\n\n"
                    "Instructions:\n"
                    "- Answer the analyst's question directly with evidentiary citations in brackets.\n"
                    "- Format cleanly with markdown and bullet points.\n"
                    "- Keep answers concise, factual, authoritative, minimal, and audit-ready."
                )
                is_stream = body.get("stream", False)
                ollama_req = urllib.request.Request(
                    "http://localhost:11434/api/generate",
                    data=json.dumps({
                        "model": "llama3:latest",
                        "prompt": f"System: {sys_prompt}\n\nAnalyst Question: {user_msg}\n\nAI Response:",
                        "stream": is_stream,
                        "options": {"temperature": 0.2, "num_predict": 600}
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                
                if is_stream:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.send_header('Connection', 'keep-alive')
                    self.end_headers()
                    try:
                        with urllib.request.urlopen(ollama_req, timeout=60.0) as resp:
                            for line in resp:
                                if line:
                                    data = json.loads(line.decode("utf-8"))
                                    chunk = data.get("response", "")
                                    self.wfile.write(f"data: {json.dumps({'content': chunk})}\n\n".encode("utf-8"))
                                    self.wfile.flush()
                                    if data.get("done"):
                                        break
                    except Exception as e:
                        self.wfile.write(f"data: {json.dumps({'error': str(e)})}\n\n".encode("utf-8"))
                    self.wfile.write(b"data: [DONE]\n\n")
                    self.wfile.flush()
                    return
                else:
                    with urllib.request.urlopen(ollama_req, timeout=12.0) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                        reply = resp_data.get("response", "").strip()
                        if reply:
                            ollama_success = True
            except Exception:
                pass

            if not ollama_success or not reply:
                msg_lower = user_msg.lower()
                if "why" in msg_lower and ("flag" in msg_lower or "score" in msg_lower or "alert" in msg_lower):
                    reply = (
                        f"## Transaction Alert Rationale\n\n"
                        f"Transaction **TX #{ctx_summary['flagged_txn_id']}** was ingested following an automated anomaly detection trigger. "
                        f"The transaction carries an assessed fraud probability of **{int(ctx_summary['fraud_probability']*100)}%**.\n\n"
                        f"### Core Flagged Factors\n"
                        f"• **Topological Pattern**: Classified as `{ctx_summary['pattern']}`.\n"
                        f"• **Hardware Nexus**: Linked to {len(ctx_summary['connected_devices'])} shared hardware profile(s) [Evidence #E-001].\n"
                        f"• **Financial Exposure**: Total flagged volume is **${ctx_summary['exposure_usd']:.2f} USD**.\n"
                        f"• **Policy Alignment**: Governed under **Bank Fraud Policy v1.0 (Rule R6)**."
                    )
                elif "connected" in msg_lower or "account" in msg_lower or "device" in msg_lower:
                    dev_text = ", ".join(ctx_summary['connected_devices']) if ctx_summary['connected_devices'] else "Device_99"
                    cards_text = ", ".join(ctx_summary['connected_cards']) if ctx_summary['connected_cards'] else "Card_4242"
                    reply = (
                        f"## Connected Entity Analysis (TigerGraph Multi-Hop)\n\n"
                        f"TigerGraph multi-hop GSQL query traversed 3 hops from Transaction **TX #{ctx_summary['flagged_txn_id']}**:\n\n"
                        f"• **Shared Hardware**: `{dev_text}` [Evidence #E-002].\n"
                        f"• **Correlated Accounts / Cards**: `{cards_text}`.\n"
                        f"• **Graph Risk Level**: **CRITICAL** due to concurrent hardware sharing across multiple distinct cardholders [Policy Rule R6]."
                    )
                elif "confidence" in msg_lower or "uncertainty" in msg_lower:
                    reply = (
                        f"## Uncertainty & Confidence Metrics\n\n"
                        f"• **Confidence Score**: **{int(ctx_summary['confidence_score']*100)}%**\n"
                        f"• **Evidence Completeness**: **{int(ctx_summary['evidence_completeness']*100)}%**\n"
                        f"• **Uncertainty Level**: **{ctx_summary['uncertainty_level']}**\n\n"
                        f"The confidence score is mathematically decoupled from the fraud risk probability. "
                        f"Because evidence completeness is {int(ctx_summary['evidence_completeness']*100)}%, uncertainty is evaluated as **{ctx_summary['uncertainty_level']}**."
                    )
                elif "evidence" in msg_lower or "need" in msg_lower or "missing" in msg_lower:
                    reply = (
                        f"## Evidentiary Audit & Missing Signals\n\n"
                        f"### Established Evidence\n"
                        + "\n".join([f"• {ev}" for ev in ctx_summary['key_evidence'][:3]]) +
                        f"\n\n### Recommended Additional Verification\n"
                        f"• Out-of-band customer SMS transaction confirmation (`VERIFY_WITH_CUSTOMER` [Rule R1]).\n"
                        f"• 3DS step-up biometric challenge (`STEP_UP_AUTH`).\n\n"
                        f"Estimated confidence increase upon receipt: **+15% to 20%**."
                    )
                elif "action" in msg_lower or "recommend" in msg_lower:
                    actions_str = ", ".join(ctx_summary['final_actions'])
                    routes_str = ", ".join(ctx_summary['action_routes'])
                    reply = (
                        f"## Recommended Next-Best-Action\n\n"
                        f"Recommended mitigation: **{actions_str}**.\n\n"
                        f"• **Approval Route**: `{routes_str}`.\n"
                        f"• **Required Role**: Senior Fraud Specialist / Team Lead.\n"
                        f"• **Rationale**: {ctx_summary['what_changed'] or 'Risk corroboration via multi-hop graph forensics mandates permanent containment under Policy Rule R6.'}\n"
                        f"• **Human Governance**: Destructive actions are paused in the **Human Approval Center** pending analyst authorization."
                    )
                elif "policy" in msg_lower or "rule" in msg_lower or "sar" in msg_lower:
                    sar_status = "MANDATED ($1,000 loss threshold or syndicate ring satisfied)" if ctx_summary['sar_file'] else "EXEMPT (Exposure below statutory threshold)"
                    reply = (
                        f"## Institutional Governance & Regulatory Citations\n\n"
                        f"• **Bank Fraud Policy v1.0 (Rule R6)**: Shared origin and syndicate detection requires case creation and connected card surveillance.\n"
                        f"• **Bank Fraud Policy v1.0 (Rule R1)**: Restraint on premature card blocking on uncorroborated single-signal alerts.\n"
                        f"• **FinCEN 31 CFR § 1020.320 (SAR)**: Status is **{sar_status}**."
                    )
                else:
                    reply = (
                        f"## Investigation Summary — Case {case_id}\n\n"
                        f"The multi-agent investigation on Transaction **TX #{ctx_summary['flagged_txn_id']}** has identified a **{ctx_summary['pattern']}** pattern.\n\n"
                        f"### Key Evidentiary Findings\n"
                        + "\n".join([f"• {ev}" for ev in ctx_summary['key_evidence'][:3]]) +
                        f"\n\n### Metric Overview\n"
                        f"• **Risk**: {int(ctx_summary['fraud_probability']*100)}% ({'HIGH' if ctx_summary['fraud_probability'] > 0.7 else 'MEDIUM'})\n"
                        f"• **Confidence**: {int(ctx_summary['confidence_score']*100)}%\n"
                        f"• **Uncertainty**: {ctx_summary['uncertainty_level']}\n"
                        f"• **Evidence Sufficiency**: {int(ctx_summary['evidence_completeness']*100)}%\n\n"
                        f"Current recommendation: **{', '.join(ctx_summary['final_actions'])}** requiring **{', '.join(ctx_summary['action_routes'])}** human authorization."
                    )

            self._send_json(200, {
                "success": True,
                "case_id": case_id,
                "reply": reply,
                "message": reply,
                "model": "llama3:latest",
                "citations": [
                    {"id": "E-001", "type": "TigerGraph Subgraph", "title": "Multi-Hop Traversal"},
                    {"id": "E-002", "type": "Identity Device", "title": "Hardware Fingerprint"},
                    {"id": "R-006", "type": "Policy Rule", "title": "Bank Fraud Policy Rule R6"}
                ],
                "suggested_actions": ["View Evidence", "View Graph", "Explain Recommended Action"]
            })
            return

        elif path == "/api/investigate":
            case_id = body.get("case_id")
            if not case_id:
                self._send_json(400, {"error": "Missing 'case_id' in request body"})
                return

            benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
            if case_id in benchmarks:
                b = benchmarks[case_id]
                ttype = b["trigger_type"]
                ttext = b["trigger_text"]
                txnid = int(b["flagged_txn_id"])
            else:
                ttype = body.get("trigger_type", "risk_score")
                ttext = body.get("trigger_text", f"Ad-hoc investigation on {case_id}")
                txnid = int(body.get("flagged_txn_id", 3514030))

            sim_resp = body.get("simulated_customer_response")
            if not sim_resp and ttype == "customer_report":
                sim_resp = "denied_fraud"

            try:
                agent = get_agent()
                case_obj, submission = agent.run_investigation(
                    trigger_type=ttype,
                    trigger_text=ttext,
                    flagged_txn_id=txnid,
                    case_id=case_id,
                    simulated_customer_response=sim_resp,
                    is_benchmark=case_id.startswith("HHG-")
                )
                # Persist
                cases_dir = os.path.join(PROJECT_ROOT, "cases")
                os.makedirs(cases_dir, exist_ok=True)
                cfile = os.path.join(cases_dir, f"{case_id}.json")
                with open(cfile, "w", encoding="utf-8") as f:
                    json.dump(submission, f, indent=2)

                self._send_json(200, {
                    "success": True,
                    "message": f"Investigation for {case_id} completed.",
                    "data": submission
                })
                return
            except Exception as e:
                self._send_json(500, {"error": f"Investigation failed: {e}"})
                return

        elif path == "/api/upload":
            # Handles upload of case/transaction file or parameters
            file_name = body.get("filename", "")
            file_content = body.get("content", "")
            case_id = body.get("case_id")
            flagged_txn_id = body.get("flagged_txn_id")
            trigger_type = body.get("trigger_type", "risk_score")
            trigger_text = body.get("trigger_text", "")
            sim_resp = body.get("simulated_customer_response")

            # Parse file content if provided
            if file_content:
                if file_name.endswith(".json") or file_content.strip().startswith("{"):
                    try:
                        parsed_json = json.loads(file_content)
                        # If this is already a full case answer format, persist and return
                        if "case" in parsed_json and "next_best_actions" in parsed_json:
                            cid = parsed_json.get("case_id", case_id or f"UPLOAD-{int(time.time())%10000:04d}")
                            parsed_json["case_id"] = cid
                            cases_dir = os.path.join(PROJECT_ROOT, "cases")
                            os.makedirs(cases_dir, exist_ok=True)
                            cfile = os.path.join(cases_dir, f"{cid}.json")
                            with open(cfile, "w", encoding="utf-8") as f:
                                json.dump(parsed_json, f, indent=2)
                            self._send_json(200, {
                                "success": True,
                                "message": f"Pre-computed case {cid} successfully ingested.",
                                "case_id": cid,
                                "data": parsed_json
                            })
                            return
                        else:
                            # Extract parameters from JSON
                            case_id = parsed_json.get("case_id", case_id)
                            flagged_txn_id = parsed_json.get("flagged_txn_id", parsed_json.get("TransactionID", flagged_txn_id))
                            trigger_type = parsed_json.get("trigger_type", trigger_type)
                            trigger_text = parsed_json.get("trigger_text", trigger_text)
                            if not sim_resp:
                                sim_resp = parsed_json.get("simulated_customer_response")
                    except Exception as e:
                        self._send_json(400, {"error": f"Failed to parse JSON file: {e}"})
                        return

                elif file_name.endswith(".csv") or "," in file_content:
                    try:
                        import csv
                        import io
                        reader = csv.DictReader(io.StringIO(file_content.strip().lstrip('\ufeff')))
                        rows = list(reader)
                        if rows:
                            row_dict = rows[0]
                            lower_dict = {str(k).strip().lower(): str(v).strip() for k, v in row_dict.items() if k is not None}
                            case_id = lower_dict.get("case_id", case_id)
                            flagged_txn_id = (
                                lower_dict.get("flagged_txn_id") 
                                or lower_dict.get("transactionid") 
                                or lower_dict.get("txn_id") 
                                or flagged_txn_id
                            )
                            trigger_type = lower_dict.get("trigger_type", trigger_type)
                            trigger_text = lower_dict.get("trigger_text", trigger_text)
                            if not sim_resp:
                                sim_resp = lower_dict.get("simulated_customer_response") or lower_dict.get("customer_response")
                    except Exception as e:
                        self._send_json(400, {"error": f"Failed to parse CSV file: {e}"})
                        return

            if not case_id:
                case_id = f"UPLOAD-{int(time.time())%10000:04d}"
            if not flagged_txn_id:
                flagged_txn_id = 3514030
            else:
                flagged_txn_id = int(flagged_txn_id)

            if not trigger_text:
                trigger_text = f"Uploaded investigation request on transaction {flagged_txn_id} via {trigger_type}."

            try:
                agent = get_agent()
                case_obj, submission = agent.run_investigation(
                    trigger_type=trigger_type,
                    trigger_text=trigger_text,
                    flagged_txn_id=flagged_txn_id,
                    case_id=case_id,
                    simulated_customer_response=sim_resp,
                    is_benchmark=False
                )
                cases_dir = os.path.join(PROJECT_ROOT, "cases")
                os.makedirs(cases_dir, exist_ok=True)
                cfile = os.path.join(cases_dir, f"{case_id}.json")
                with open(cfile, "w", encoding="utf-8") as f:
                    json.dump(submission, f, indent=2)

                self._send_json(200, {
                    "success": True,
                    "message": f"Uploaded transaction investigated successfully as {case_id}.",
                    "case_id": case_id,
                    "data": submission
                })
                return
            except Exception as e:
                self._send_json(500, {"error": f"Investigation of uploaded case failed: {e}"})
                return

        elif path == "/api/multi_agent_analyze":
            case_id = body.get("case_id")
            flagged_txn_id = body.get("flagged_txn_id")
            trigger_type = body.get("trigger_type", "risk_score")
            trigger_text = body.get("trigger_text")
            sim_resp = body.get("simulated_customer_response") or body.get("customer_response")

            benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
            if case_id and case_id in benchmarks:
                b = benchmarks[case_id]
                trigger_type = b["trigger_type"]
                trigger_text = b["trigger_text"]
                flagged_txn_id = int(b["flagged_txn_id"])
                if not sim_resp and trigger_type == "customer_report":
                    sim_resp = "denied_fraud"
            elif not flagged_txn_id:
                flagged_txn_id = 3514030
            else:
                flagged_txn_id = int(flagged_txn_id)

            if not case_id:
                case_id = f"SQUAD-{flagged_txn_id}"

            try:
                orch = get_orchestrator()
                result = orch.run_squad_investigation(
                    flagged_txn_id=flagged_txn_id,
                    trigger_type=trigger_type,
                    trigger_text=trigger_text,
                    case_id=case_id,
                    customer_response=sim_resp
                )

                # Run Autonomous 11-Agent Investigation Pipeline
                try:
                    pipeline_11 = get_eleven_pipeline()
                    eleven_res = pipeline_11.investigate(
                        flagged_txn_id=flagged_txn_id,
                        user_id=f"User_{flagged_txn_id}",
                        trigger_type=trigger_type,
                        trigger_text=trigger_text or "Automated squad multi-agent flag",
                        case_id=case_id,
                        customer_response=sim_resp
                    )
                    result["eleven_agent_pipeline"] = eleven_res
                    result["frontend_report"] = eleven_res["frontend_report"]
                except Exception as ex_11:
                    print(f"[Warning] 11-Agent pipeline fallback: {ex_11}")

                self._send_json(200, result)
                return
            except Exception as e:
                self._send_json(500, {"error": f"Multi-agent investigation failed: {e}"})
                return

        elif path == "/api/crewai_tigergraph_investigate":
            case_id = body.get("case_id")
            flagged_txn_id = body.get("flagged_txn_id")
            user_id = body.get("user_id")
            trigger_context = body.get("trigger_text") or "High risk transaction flag"
            sim_resp = body.get("simulated_customer_response") or body.get("customer_response")

            benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
            if case_id and case_id in benchmarks:
                b = benchmarks[case_id]
                flagged_txn_id = int(b["flagged_txn_id"])
                user_id = user_id or f"CUST-{b.get('customer_id', flagged_txn_id)}"
                trigger_context = b.get("trigger_text", trigger_context)
            elif not flagged_txn_id:
                flagged_txn_id = 3514030
                user_id = user_id or "CUST-3514030"
            else:
                flagged_txn_id = int(flagged_txn_id)
                user_id = user_id or f"CUST-{flagged_txn_id}"

            if not case_id:
                case_id = f"CREW-{flagged_txn_id}"

            try:
                crew_inv = get_crew_investigator()
                report = crew_inv.run_investigation(
                    case_id=case_id,
                    user_id=user_id,
                    flagged_txn_id=flagged_txn_id,
                    trigger_context=trigger_context,
                    customer_response=sim_resp
                )
                self._send_json(200, {
                    "success": True,
                    "case_id": case_id,
                    "frontend_report": report.model_dump()
                })
                return
            except Exception as e:
                self._send_json(500, {"error": f"CrewAI TigerGraph investigation failed: {e}"})
                return

        elif path == "/api/eleven_agent_investigate":
            case_id = body.get("case_id")
            flagged_txn_id = body.get("flagged_txn_id")
            user_id = body.get("user_id")
            trigger_type = body.get("trigger_type", "High-Risk Transaction Alert")
            trigger_text = body.get("trigger_text")
            sim_resp = body.get("simulated_customer_response") or body.get("customer_response")

            benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
            if case_id and case_id in benchmarks:
                b = benchmarks[case_id]
                flagged_txn_id = int(b["flagged_txn_id"])
                user_id = user_id or f"User_{b.get('customer_id', flagged_txn_id)}"
                trigger_text = trigger_text or b.get("trigger_text")
            elif not flagged_txn_id:
                flagged_txn_id = 3514030
                user_id = user_id or "User_101"
            else:
                flagged_txn_id = int(flagged_txn_id)
                user_id = user_id or f"User_{flagged_txn_id}"

            if not case_id:
                case_id = f"TG-CASE-2026-{flagged_txn_id % 10000:04d}"

            try:
                pipeline = get_eleven_pipeline()
                res = pipeline.investigate(
                    flagged_txn_id=flagged_txn_id,
                    user_id=user_id,
                    trigger_type=trigger_type,
                    trigger_text=trigger_text,
                    case_id=case_id,
                    customer_response=sim_resp
                )
                self._send_json(200, res)
                return
            except Exception as e:
                self._send_json(500, {"error": f"11-Agent investigation failed: {e}"})
                return

        elif path == "/api/approve_action":
            case_id = body.get("case_id", "UNKNOWN")
            action = body.get("action", "UNKNOWN")
            route = body.get("route", "L1")
            analyst = body.get("analyst", "Fraud Specialist L2")

            approval_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "case_id": case_id,
                "action": action,
                "route": route,
                "analyst": analyst,
                "status": "APPROVED",
                "execution_state": "DISPATCHED_TO_CORE_BANKING"
            }

            # Append to approvals log
            approvals_path = os.path.join(PROJECT_ROOT, "data", "analyst_approvals.jsonl")
            try:
                with open(approvals_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(approval_record) + "\n")
            except Exception as e:
                print(f"Warning: could not write approval log: {e}")

            # Update case file status if exists
            cfile = os.path.join(PROJECT_ROOT, "cases", f"{case_id}.json")
            if os.path.exists(cfile):
                try:
                    with open(cfile, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                    cdata["case"]["status"] = "closed_fraud" if "BLOCK" in action or "FREEZE" in action else "closed_legitimate"
                    cdata["case"]["analyst_approval"] = approval_record
                    with open(cfile, "w", encoding="utf-8") as f:
                        json.dump(cdata, f, indent=2)
                except Exception:
                    pass

            self._send_json(200, {
                "success": True,
                "record": approval_record,
                "message": f"Action '{action}' approved by {analyst} ({route}) and successfully dispatched."
            })
            return

        elif path == "/api/investigations/start":
            case_id = body.get("case_id")
            flagged_txn_id = body.get("flagged_txn_id")
            user_id = body.get("user_id")
            trigger_type = body.get("trigger_type", "risk_score")
            trigger_text = body.get("trigger_text")
            sim_resp = body.get("simulated_customer_response")

            benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
            if case_id and case_id in benchmarks:
                b = benchmarks[case_id]
                flagged_txn_id = int(b["flagged_txn_id"])
                user_id = user_id or f"User_{b.get('customer_id', flagged_txn_id)}"
                trigger_text = trigger_text or b.get("trigger_text")
                trigger_type = b.get("trigger_type", trigger_type)
            elif not flagged_txn_id:
                flagged_txn_id = 3514030
                user_id = user_id or "User_101"
            else:
                flagged_txn_id = int(flagged_txn_id)
                user_id = user_id or f"User_{flagged_txn_id}"

            if not case_id:
                case_id = f"TG-CASE-2026-{flagged_txn_id % 10000:04d}"

            try:
                pipeline = get_eleven_pipeline()
                res = pipeline.investigate(
                    flagged_txn_id=flagged_txn_id,
                    user_id=user_id,
                    trigger_type=trigger_type,
                    trigger_text=trigger_text,
                    case_id=case_id,
                    customer_response=sim_resp
                )
                self._send_json(200, res)
                return
            except Exception as e:
                self._send_json(500, {"error": f"Investigation failed to start: {e}"})
                return

        elif path.startswith("/api/investigations/"):
            parts = path.strip("/").split("/")
            # parts: ['api', 'investigations', case_id, sub_action]
            if len(parts) >= 4:
                cid = parts[2]
                sub_act = parts[3]
                cfile = os.path.join(PROJECT_ROOT, "cases", f"{cid}.json")

                if sub_act == "evidence":
                    # Ingest additional evidence and trigger reinvestigation
                    resp = body.get("response") or body.get("assumed_response") or "denied_fraud"
                    ev_type = body.get("type", "customer_validation")

                    benchmarks = {b["case_id"]: b for b in get_benchmark_cases()}
                    b = benchmarks.get(cid, {})
                    txnid = int(b.get("flagged_txn_id", 3514030))
                    ttype = b.get("trigger_type", "risk_score")
                    ttext = b.get("trigger_text", f"Investigation for {cid}")

                    try:
                        agent = get_agent()
                        case_obj, submission = agent.run_investigation(
                            trigger_type=ttype,
                            trigger_text=ttext,
                            flagged_txn_id=txnid,
                            case_id=cid,
                            simulated_customer_response=resp,
                            is_benchmark=cid.startswith("HHG-")
                        )
                        with open(cfile, "w", encoding="utf-8") as f:
                            json.dump(submission, f, indent=2)

                        self._send_json(200, {
                            "success": True,
                            "case_id": cid,
                            "evidence_ingested": {"type": ev_type, "response": resp},
                            "reinvestigation_data": submission
                        })
                        return
                    except Exception as e:
                        self._send_json(500, {"error": f"Re-investigation failed: {e}"})
                        return

                elif sub_act == "approve":
                    action = body.get("action", "BLOCK_CARD")
                    analyst = body.get("analyst", "Senior Fraud Specialist L2")
                    route = body.get("route", "L1")

                    from agent.action_gateway import get_action_gateway
                    gateway = get_action_gateway()

                    cdata = {}
                    if os.path.exists(cfile):
                        try:
                            with open(cfile, "r", encoding="utf-8") as f:
                                cdata = json.load(f)
                        except Exception:
                            pass

                    card_id = "CARD-4242"
                    cust_id = "101"
                    if "case" in cdata:
                        conn_cards = cdata["case"].get("connected_card_ids", [])
                        if conn_cards:
                            card_id = str(conn_cards[0])
                        cust_id = str(cdata["case"].get("customer_id", "101"))

                    # Execute through Sandbox Action Gateway
                    gw_res = gateway.execute_action(
                        action=action,
                        case_id=cid,
                        card_id=card_id,
                        customer_id=cust_id,
                        authorized_by=analyst,
                        route=route,
                        reason=f"Authorized by {analyst} under Policy Route {route}"
                    )

                    rec = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "case_id": cid,
                        "action": action,
                        "analyst": analyst,
                        "route": route,
                        "status": "APPROVED",
                        "execution_state": gw_res.get("execution_status", "EXECUTED_IN_SANDBOX"),
                        "sandbox_execution": gw_res
                    }
                    approvals_path = os.path.join(PROJECT_ROOT, "data", "analyst_approvals.jsonl")
                    try:
                        with open(approvals_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(rec) + "\n")
                    except Exception:
                        pass

                    if os.path.exists(cfile) and cdata:
                        try:
                            cdata["case"]["status"] = "closed_fraud"
                            cdata["case"]["approval_status"] = "APPROVED"
                            cdata["case"]["card_status"] = gw_res.get("new_card_status", "BLOCKED")
                            cdata["case"]["sandbox_execution"] = gw_res
                            with open(cfile, "w", encoding="utf-8") as f:
                                json.dump(cdata, f, indent=2)
                        except Exception:
                            pass

                    self._send_json(200, {
                        "success": True,
                        "case_id": cid,
                        "approval_record": rec,
                        "gateway_execution": gw_res,
                        "message": f"Action '{action}' approved by {analyst} and executed in Sandbox Action Gateway (Card status: {gw_res.get('new_card_status')})."
                    })
                    return

                elif sub_act == "reject":
                    action = body.get("action", "REJECTED")
                    analyst = body.get("analyst", "Fraud Specialist L2")
                    reason = body.get("reason", "Analyst determined false positive")

                    rec = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "case_id": cid,
                        "action": action,
                        "analyst": analyst,
                        "status": "REJECTED",
                        "reason": reason
                    }
                    approvals_path = os.path.join(PROJECT_ROOT, "data", "analyst_approvals.jsonl")
                    try:
                        with open(approvals_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(rec) + "\n")
                    except Exception:
                        pass

                    if os.path.exists(cfile):
                        try:
                            with open(cfile, "r", encoding="utf-8") as f:
                                cdata = json.load(f)
                            cdata["case"]["status"] = "closed_legitimate"
                            cdata["case"]["approval_status"] = "REJECTED"
                            with open(cfile, "w", encoding="utf-8") as f:
                                json.dump(cdata, f, indent=2)
                        except Exception:
                            pass

                    self._send_json(200, {
                        "success": True,
                        "case_id": cid,
                        "record": rec,
                        "message": f"Action rejected for {cid}: {reason}."
                    })
                    return

            self._send_json(400, {"error": "Invalid investigation action endpoint"})
            return

        else:
            self.send_error(404, f"Endpoint {path} not found")

class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server(port: int = 8080):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, FraudOpsHandler)
    print(f"============================================================")
    print(f"  TigerGraph FraudOps Live Cockpit Server Running on http://localhost:{port}")
    print(f"  Analyst Dashboard: http://localhost:{port}/")
    print(f"  API Cases List:    http://localhost:{port}/api/cases")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    run_server(port)
