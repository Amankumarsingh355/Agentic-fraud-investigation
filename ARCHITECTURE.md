# TigerGraph 11-Agent Autonomous Fraud Investigation System
## System Architecture & Technical Specifications (IEEE-CIS / Hacker House Goa)

---

## 1. System Overview

The **TigerGraph Agentic Fraud Investigation System** (`AGENTIC_NEURAL_SHIELD // v2.6`) is an enterprise-grade, graph-native autonomous fraud investigation platform. It marries multi-hop graph analytics via **TigerGraph** (Savanna cloud instance and pyTigerGraph GSQL execution layer) with an **11-Agent CrewAI orchestration pipeline**, a local **Ollama Llama 3** reasoning core, a mathematical **Uncertainty & Evidence Completeness Engine**, and a cyber-tactical **React + Tailwind CSS** investigation console.

```
                           [Inbound Transaction Alert]
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 1: Fraud Ingestion Agent             │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 2: TigerGraph Evidence Agent         │
             │       (Multi-Hop GSQL: findSharedDevices)        │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 3: Graph Pattern Classifier          │
             │       (ATO, Syndicate, Bust-Out, Testing)        │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 4: Case Initializer Agent            │
             │       (Immutable Ledger & State Machine)         │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 5: Vector / Case Memory Agent        │
             │       (ChromaDB + TigerGraph ClosedCase Graph)   │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 6: Step-Up & Uncertainty Agent       │
             │       (Decoupled Confidence & Completeness)      │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 7: Action Recommendation Engine      │
             │       (Initial vs Final Two-Stage Actions)       │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 8: Policy & Governance Validator     │
             │       (Bank Fraud Policy v1.0: Rules R1-R10)     │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 9: Early Stopping & Efficiency Gate  │
             │       (Evidence Saturation & Token Budgeting)    │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 10: Explainability & Narrative Agent │
             │       (Regulatory Narratives & FinCEN Filings)   │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │       AGENT 11: Master Decision Validator        │
             │       (4-Step CoT Audit & Pydantic JSON Output)  │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼
                  [Exact 3-Part JSON & React Cyberpunk UI]
```

---

## 2. The 11 Autonomous Specialized Agents

Each agent has a strictly delineated single responsibility, typed input/output interfaces, explicit tool bindings, and formal governance constraints:

| Agent | Name | Role & Responsibility | Core Tools & Technologies |
|---|---|---|---|
| **Agent 1** | **Fraud Ingestion Agent** | Normalizes alert triggers, parses incoming payload parameters, verifies transaction identity, and checks for preliminary risk flags. | Alert Normalizer, Ingestion Schema Validator |
| **Agent 2** | **TigerGraph Evidence Agent** | Executes multi-hop graph queries (`findSharedDevices`, circular loops, shared IP/device subgraphs) against the 590k transaction graph. | pyTigerGraph, GSQL Multi-Hop Engine, Subgraph Extractor |
| **Agent 3** | **Graph Pattern Classifier** | Detects topological fraud patterns: Account Takeover (ATO), Syndicate Mule Ring, Card Testing, Merchant Bust-Out, and Velocity Spikes. | Graph Topology Classifier, Community Detection |
| **Agent 4** | **Case Initializer Agent** | Creates persistent case identities, assigns tracking UUIDs, instantiates immutable event ledgers, and tracks investigation state. | State Machine Manager, Case Ledger Manager |
| **Agent 5** | **Vector / Case Memory Agent** | Conducts hybrid retrieval over past resolved fraud cases, precedent typologies, and regulatory manuals; writes back resolved cases to TigerGraph. | ChromaDB, Precedent Vector RAG, TigerGraph `ClosedCase` Vertex |
| **Agent 6** | **Step-Up & Uncertainty Agent** | Mathematically computes evidence completeness and uncertainty; orchestrates additional evidence loops (SMS, 3DS, biometric) when signals are incomplete. | Uncertainty Engine, Evidence Request Dispatcher |
| **Agent 7** | **Action Recommendation Engine** | Formulates two-stage action plans (Initial provisional containment vs. Final post-evidence mitigation) from the 14 bank policy actions. | Two-Stage Next-Best-Action Engine |
| **Agent 8** | **Policy & Governance Validator** | Enforces Bank Fraud Policy v1.0 (Rules R1–R10) and determines approval routes (`auto`, `L1`, `L2`) and FinCEN SAR eligibility. | Policy Engine (R1–R10), SAR Assessment Rulebase |
| **Agent 9** | **Early Stopping & Efficiency Gate** | Evaluates evidence density and confidence saturation to safely terminate redundant graph traversal hops, saving latency and tokens. | Entropy Decoupler, Early Stopping Evaluator |
| **Agent 10** | **Explainability & Narrative Agent** | Generates human-auditable rationales, FinCEN SAR forensic narratives, and customer communication summaries. | Ollama Llama 3 Forensic Summarizer |
| **Agent 11** | **Master Decision Validator** | Conducts a 4-step Chain-of-Thought audit (Completeness, Grounding, Policy, SAR), validates against Pydantic schema, and prevents CoT leakage. | Master Decision Validator, Pydantic `FrontendReportSchema` |

---

## 3. GraphRAG Context Synthesis Layer

The GraphRAG synthesis layer (`graph/graphrag_synthesizer.py`) compiles heterogeneous evidentiary sources into a unified, high-density structured prompt:

1. **Graph Subgraph Evidence**:
   - Multi-hop neighbor expansion from the target transaction vertex.
   - Shared hardware fingerprints (`Device` vertices) and network nodes (`IPAddress` vertices).
   - Cyclic funds flow detection across intermediate card/user nodes.
2. **Policy Knowledge Grounding**:
   - Full text of **Bank Fraud Policy v1.0** containing Rules R1 through R10.
   - Strict containment guidelines (e.g., Rule R10 limits total card cancellation when tokenized digital-wallet fraud is isolated).
3. **Regulatory Context**:
   - FinCEN 31 CFR § 1020.320 SAR thresholds ($5,000 general suspect activity, $1,000 direct bank loss).
   - FATF Recommendations on beneficial ownership and mule networks.
   - FFIEC authentication guidelines for out-of-band and step-up verification.
4. **Historical Case Memory**:
   - Vector similarity search against previously confirmed fraud rings and false-positive cases.
   - Live graph lookups in TigerGraph for linked `ClosedCase` records.

---

## 4. Mathematical Uncertainty & Confidence Decoupling

Conventional fraud models conflate fraud likelihood with prediction confidence. The **Uncertainty Engine** (`agent/uncertainty_engine.py`) enforces strict mathematical decoupling:

$$\text{Evidence Completeness} = \frac{\sum_{i=1}^{N} w_i \cdot \mathbb{I}(\text{evidence}_i \text{ present})}{\sum_{i=1}^{N} w_i}$$

$$\text{Confidence Score} = \min(1.0, 0.4 \cdot \text{Evidence Completeness} + 0.35 \cdot \text{Graph Signal Strength} + 0.25 \cdot \text{Precedent Match})$$

$$\text{Uncertainty Score} = 1.0 - \text{Confidence Score}$$

$$\text{Uncertainty Level} = \begin{cases} \text{HIGH} & \text{if } \text{Uncertainty Score} > 0.45 \\ \text{MEDIUM} & \text{if } 0.20 < \text{Uncertainty Score} \le 0.45 \\ \text{LOW} & \text{if } \text{Uncertainty Score} \le 0.20 \end{cases}$$

- **High Uncertainty Trigger**: When uncertainty is `HIGH` or evidence completeness $< 0.60$, the system enters `INSUFFICIENT_EVIDENCE` status and activates the **Additional Evidence Loop** rather than making a premature destructive decision.
- **Rule R1 Enforcement**: Suspicious activity without confirming device or customer dispute requires step-up authentication (`STEP_UP_AUTH`), not automatic card freezing.

---

## 5. Next-Best-Action & Multi-Tier Approval Governance

Actions are strictly drawn from the **14 Approved Policy Actions**:
1. `FREEZE_ACCOUNT` (Route: L2)
2. `BLOCK_CARD` (Route: L1 / auto)
3. `BLOCK_DEVICE` (Route: L1)
4. `RESTRICT_ONLINE_TXN` (Route: auto)
5. `RESTRICT_OFFSHORE_TXN` (Route: auto)
6. `FLAG_HIGH_RISK` (Route: auto)
7. `STEP_UP_AUTH` (Route: auto)
8. `HOLD_TRANSACTION` (Route: auto)
9. `DISPUTE_OPEN` (Route: L1)
10. `PROVISIONAL_CREDIT` (Route: L1)
11. `NOTIFY_CUSTOMER` (Route: auto)
12. `FILE_SAR` (Route: L2)
13. `RELEASE_TRANSACTION` (Route: auto)
14. `MONITOR_ACCOUNT` (Route: auto)

### Approval Hierarchy
- **`auto`**: Dispatched immediately with zero human latency (e.g., `HOLD_TRANSACTION`, `NOTIFY_CUSTOMER`, `RESTRICT_ONLINE_TXN`).
- **`L1`**: Requires Level 1 Fraud Analyst authorization (e.g., `BLOCK_CARD`, `DISPUTE_OPEN`, `PROVISIONAL_CREDIT`).
- **`L2`**: Mandates Senior Fraud Specialist / Compliance Officer sign-off (e.g., `FREEZE_ACCOUNT`, `FILE_SAR`).

---

## 6. Closed-Loop Additional Evidence Loop

The system operates a finite state machine:
`NEW` $\to$ `INVESTIGATING` $\to$ `INSUFFICIENT_EVIDENCE` $\to$ `EVIDENCE_REQUESTED` $\to$ `EVIDENCE_RECEIVED` $\to$ `REINVESTIGATION` $\to$ `AWAITING_APPROVAL` $\to$ `APPROVED` $\to$ `RESOLVED`.

1. **Trigger**: High uncertainty triggers an `EvidenceRequest` specifying request type (`customer_sms`, `3ds_verification`, `device_telemetry`, `merchant_inquiry`).
2. **Ingestion**: When the response arrives via `POST /api/investigations/{case_id}/evidence`, the case transitions to `EVIDENCE_RECEIVED`.
3. **Evolution**: A reinvestigation re-evaluates all graph signals under the new evidence, showing explicit evolution from `nba["initial"]` to `nba["final"]` and documenting the delta in `nba["what_changed"]`.
4. **Write-Back**: When the analyst clicks Approve, the decision is dispatched to core banking and written back to TigerGraph as an immutable `ClosedCase` vertex linked to target accounts and cards.

---

## 7. Submission Specification Compliance

Every generated case output adheres strictly to the official 3-part schema:
```json
{
  "case": {
    "case_id": "HHG-001",
    "status": "closed_fraud",
    "verdict": "fraud",
    "fraud_probability": 0.94,
    "confidence_score": 0.92,
    "evidence_completeness": 0.95,
    "uncertainty_level": "LOW",
    "pattern": "Syndicate Mule Ring",
    "first_suspicious_txn_id": 3514030,
    "exposure_usd": 77.07,
    "connected_card_ids": ["4242..."],
    "connected_device_profiles": ["dev_..."],
    "evidence": [...],
    "summary": "..."
  },
  "sar": {
    "file": true,
    "threshold_usd": 1000.0,
    "total_amount_usd": 77.07,
    "recommended_narrative": "...",
    "regulatory_citations": ["FinCEN 31 CFR § 1020.320", "Bank Fraud Policy v1.0 Section 4"]
  },
  "next_best_actions": {
    "initial": [...],
    "final": [...],
    "what_changed": "..."
  },
  "evidence_requests": [...],
  "tool_calls": 5,
  "tokens": 420
}
```
All outputs are tested against `tests/validate_submission.py` to ensure 100% compliance.
