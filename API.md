# TigerGraph Fraud Investigation REST API Reference
## API Documentation & Endpoints (Port 8080)

The backend server is hosted at `http://localhost:8080` and provides complete programmatic control over investigations, graph evidence retrieval, stateful human approval loops, and evidence ingestion.

---

## 1. System Health & Metadata

### `GET /api/health`
Checks server readiness.
- **Request**: None
- **Response** (`200 OK`):
  ```json
  {
    "status": "ok",
    "service": "tigergraph-fraud-investigation-backend"
  }
  ```

---

## 2. Cases & Benchmarks

### `GET /api/cases`
Lists all cases (both standard benchmark cases and ad-hoc investigations).
- **Request**: None
- **Response** (`200 OK`):
  ```json
  {
    "total": 20,
    "cases": [
      {
        "case_id": "HHG-001",
        "customer_id": "User_23910",
        "card_id": "4242-xxxx",
        "flagged_txn_id": "3514030",
        "trigger_type": "risk_score",
        "trigger_text": "High out-of-region POS swipe",
        "is_generated": true,
        "status": "closed_fraud",
        "verdict": "fraud",
        "amount": 77.07,
        "pattern": "Syndicate Mule Ring"
      }
    ]
  }
  ```

### `GET /api/case?id={case_id}`
Fetches the full 3-part submission payload for a specific case.
- **Parameters**: `id` (e.g., `HHG-001`)
- **Response** (`200 OK`): Exact 3-part JSON (`case`, `sar`, `next_best_actions`).

---

## 3. Investigation State & Forensics

### `GET /api/investigations/{case_id}/timeline`
Returns the chronological audit trail and multi-agent progression for a case.
- **Parameters**: `case_id` in path
- **Response** (`200 OK`):
  ```json
  {
    "case_id": "HHG-001",
    "status": "closed_fraud",
    "timeline": [
      {
        "step": 1,
        "stage": "INGESTION",
        "title": "Alert Ingested",
        "detail": "Flagged Transaction 3514030 entered investigation ledger."
      },
      {
        "step": 2,
        "stage": "EVIDENCE_GATHERED",
        "source": "graph",
        "claim": "Multi-hop graph query identified shared device with 3 flagged accounts."
      },
      {
        "step": 3,
        "stage": "DECISION_FORMULATED",
        "verdict": "fraud",
        "actions": ["BLOCK_CARD", "NOTIFY_CUSTOMER", "FILE_SAR"],
        "sar_filed": true
      }
    ]
  }
  ```

### `GET /api/investigations/{case_id}/evidence`
Returns raw evidentiary signals and open evidence requests.
- **Response** (`200 OK`):
  ```json
  {
    "case_id": "HHG-001",
    "evidence": [...],
    "evidence_requests": [
      {
        "type": "customer_sms",
        "urgency": "medium",
        "description": "Send SMS to confirm $77.07 POS charge"
      }
    ],
    "connected_cards": ["4242..."],
    "connected_devices": ["dev_android_..."]
  }
  ```

---

## 4. Multi-Agent Execution & Pipeline Triggers

### `POST /api/investigate`
Executes an investigation on a target case or transaction ID.
- **Request Body**:
  ```json
  {
    "case_id": "HHG-001",
    "simulated_customer_response": "denied_fraud"
  }
  ```
- **Response** (`200 OK`): Full investigation payload and persistence confirmation.

### `POST /api/eleven_agent_investigate`
Directly invokes the 11-Agent autonomous pipeline with fine-grained parameters.
- **Request Body**:
  ```json
  {
    "flagged_txn_id": 3514030,
    "user_id": "User_101",
    "trigger_type": "risk_score",
    "trigger_text": "Unusual high-velocity transfer"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "case_id": "TG-CASE-2026-4030",
    "agent_outputs": {
      "agent_1_ingestion": {...},
      "agent_2_tigergraph": {...},
      "agent_8_policy": {...},
      "agent_11_validator": {...}
    },
    "frontend_report": {...}
  }
  ```

---

## 5. Human-in-the-Loop & Evidence Ingestion

### `POST /api/investigations/{case_id}/evidence`
Ingests out-of-band evidence (e.g., customer SMS reply, 3DS authentication confirmation) and triggers automatic reinvestigation.
- **Request Body**:
  ```json
  {
    "evidence_type": "customer_sms",
    "response": "denied_fraud"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "case_id": "HHG-001",
    "evidence_ingested": {
      "type": "customer_sms",
      "response": "denied_fraud"
    },
    "reinvestigation_data": {...}
  }
  ```

### `POST /api/investigations/{case_id}/approve`
Records an analyst's formal authorization for high-consequence actions (`L1` or `L2`), dispatches to core banking, and updates case memory.
- **Request Body**:
  ```json
  {
    "action": "BLOCK_CARD",
    "analyst": "Senior Fraud Specialist L2",
    "route": "L1"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "case_id": "HHG-001",
    "action": "BLOCK_CARD",
    "status": "APPROVED",
    "dispatched_at": "2026-09-23T14:40:15Z"
  }
  ```

### `POST /api/investigations/{case_id}/reject`
Logs an analyst's rejection of an action recommendation.
- **Request Body**:
  ```json
  {
    "action": "FREEZE_ACCOUNT",
    "analyst": "Compliance Officer",
    "reason": "Customer travel notice verified via telephone support"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "case_id": "HHG-001",
    "status": "REJECTED"
  }
  ```
