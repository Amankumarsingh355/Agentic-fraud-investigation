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
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import urllib.parse

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent import FraudInvestigationAgent
from agent.case_formatter import CaseFormatter

# Global lazy agent instance
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        print("[FraudOps Server] Initializing FraudInvestigationAgent...")
        _agent = FraudInvestigationAgent()
        print("[FraudOps Server] Agent initialized successfully.")
    return _agent

def get_benchmark_cases():
    cases_pack_path = os.path.join(PROJECT_ROOT, "data", "case_pack.csv")
    cases = []
    if os.path.exists(cases_pack_path):
        with open(cases_pack_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cases.append(row)
    return cases

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

        if path == "/" or path == "/index.html":
            index_path = os.path.join(PROJECT_ROOT, "ui", "index.html")
            self._send_file(index_path, "text/html; charset=utf-8")
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

        if path == "/api/investigate":
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

        elif path == "/api/approve_action":
            case_id = body.get("case_id", "UNKNOWN")
            action = body.get("action", "UNKNOWN")
            route = body.get("route", "L1")
            analyst = body.get("analyst", "Fraud Specialist L2")

            approval_record = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
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

            self._send_json(200, {
                "success": True,
                "record": approval_record,
                "message": f"Action '{action}' approved by {analyst} ({route}) and successfully dispatched."
            })
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
