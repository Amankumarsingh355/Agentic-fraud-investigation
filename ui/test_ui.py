"""
Phase 8 UI Verification Test Suite
Tests live HTTP server, dashboard HTML delivery, REST API endpoints,
analyst approval workflow, and live investigation trigger.
"""

import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.serve import ThreadingHTTPServer, FraudOpsHandler
from agent.case_formatter import CaseFormatter

TEST_PORT = 8088
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

def run_test_suite():
    print(f"=== Starting Phase 8 UI Verification Tests on port {TEST_PORT} ===")
    
    server_address = ("127.0.0.1", TEST_PORT)
    httpd = ThreadingHTTPServer(server_address, FraudOpsHandler)
    
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.5)
    print("Test HTTP server started successfully.")

    try:
        # 1. Test GET / (HTML delivery)
        print("\n[Test 1/5] Testing GET / (Dashboard HTML)...")
        with urllib.request.urlopen(f"{BASE_URL}/") as resp:
            status = resp.getcode()
            html = resp.read().decode("utf-8")
            assert status == 200, f"Expected 200, got {status}"
            assert "TigerGraph FraudOps" in html, "Dashboard title missing"
            assert "Multi-Hop Evidence Subgraph" in html, "Evidence graph canvas missing"
            assert "72-Hour Rolling Velocity Timeline" in html, "Velocity timeline missing"
            assert "Assessed Uncertainty" in html, "Uncertainty gauge missing"
            print(f"  ✓ Dashboard HTML delivered ({len(html)} bytes). Status {status} OK.")

        # 2. Test GET /api/cases (List of cases)
        print("\n[Test 2/5] Testing GET /api/cases...")
        with urllib.request.urlopen(f"{BASE_URL}/api/cases") as resp:
            status = resp.getcode()
            data = json.loads(resp.read().decode("utf-8"))
            assert status == 200, f"Expected 200, got {status}"
            assert "cases" in data, "Missing 'cases' array"
            assert data["total"] >= 20, f"Expected at least 20 cases, got {data['total']}"
            hhg_001 = next((c for c in data["cases"] if c["case_id"] == "HHG-001"), None)
            assert hhg_001 is not None, "HHG-001 not found in case pack"
            print(f"  ✓ Retrieved {data['total']} cases. HHG-001 status: {hhg_001['status']}.")

        # 3. Test GET /api/case?id=HHG-001 (Existing case payload)
        print("\n[Test 3/5] Testing GET /api/case?id=HHG-001...")
        with urllib.request.urlopen(f"{BASE_URL}/api/case?id=HHG-001") as resp:
            status = resp.getcode()
            data = json.loads(resp.read().decode("utf-8"))
            assert status == 200, f"Expected 200, got {status}"
            assert data["case_id"] == "HHG-001"
            assert "case" in data and "sar" in data and "next_best_actions" in data
            
            # Validate against README Answer Format schema
            formatter = CaseFormatter()
            formatter.validate_schema(data)
            print(f"  ✓ Case HHG-001 retrieved. Schema validated with 0 errors. Exposure: ${data['case']['exposure_usd']}.")

        # 4. Test POST /api/approve_action (Analyst sign-off workflow)
        print("\n[Test 4/5] Testing POST /api/approve_action (L1/L2 Sign-off)...")
        req_data = json.dumps({
            "case_id": "HHG-001",
            "action": "BLOCK_CARD",
            "route": "L1",
            "analyst": "Lead Fraud Specialist"
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/api/approve_action",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            res = json.loads(resp.read().decode("utf-8"))
            assert status == 200, f"Expected 200, got {status}"
            assert res["success"] is True
            assert res["record"]["status"] == "APPROVED"
            assert res["record"]["execution_state"] == "DISPATCHED_TO_CORE_BANKING"
            print(f"  ✓ Action BLOCK_CARD approved & dispatched. Server message: {res['message']}")

        # 5. Test POST /api/investigate (Live Agent Investigation Trigger)
        print("\n[Test 5/5] Testing POST /api/investigate on HHG-003 (Customer Dispute)...")
        inv_data = json.dumps({
            "case_id": "HHG-003",
            "simulated_customer_response": "denied_fraud"
        }).encode("utf-8")
        req2 = urllib.request.Request(
            f"{BASE_URL}/api/investigate",
            data=inv_data,
            headers={"Content-Type": "application/json"}
        )
        t_start = time.time()
        with urllib.request.urlopen(req2) as resp:
            duration = time.time() - t_start
            status = resp.getcode()
            res2 = json.loads(resp.read().decode("utf-8"))
            assert status == 200, f"Expected 200, got {status}"
            assert res2["success"] is True
            case_data = res2["data"]
            assert case_data["case_id"] == "HHG-003"
            assert case_data["case"]["status"] == "closed_fraud"
            formatter.validate_schema(case_data)
            print(f"  ✓ Live investigation for HHG-003 completed in {duration:.2f}s.")
            print(f"    Verdict: {case_data['case']['verdict']}, Exposure: ${case_data['case']['exposure_usd']}")
            print(f"    Actions formulated: {[a['action'] for a in case_data['next_best_actions']['final']]}")
            print(f"    Schema validated: 0 errors.")

        print("\n============================================================")
        print("  ALL 5 UI & API ENDPOINT VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("============================================================")

    finally:
        print("Shutting down test server...")
        httpd.shutdown()
        httpd.server_close()
        print("Test server stopped.")

if __name__ == "__main__":
    run_test_suite()
