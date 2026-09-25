# TigerGraph Agentic Fraud Investigation Suite (HHGOA_IEEE)

[![TigerGraph](https://img.shields.io/badge/TigerGraph-Savanna%20%7C%20Enterprise-orange.svg)](https://www.tigergraph.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-11%20Autonomous%20Agents-red.svg)](docs/AGENT_RESPONSIBILITIES.md)
[![GraphRAG](https://img.shields.io/badge/GraphRAG-Multi--Hop%20Evidence-06B6D4.svg)](https://github.com/tigergraph/tigergraph-mcp)
[![FinCEN SAR](https://img.shields.io/badge/FinCEN%20SAR-Compliant-10B981.svg)](https://www.fincen.gov/)
[![Benchmark Evaluation](https://img.shields.io/badge/Benchmark-20%2F20%20Cases%20(100%25)-brightgreen.svg)](cases/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An end-to-end, production-grade autonomous AI fraud investigation system built for the **TigerGraph × Hacker House Goa** hackathon.

Engineered with **Production-Inspired Institutional Sandbox Architecture**: Powered by **TigerGraph GSQL**, **11-Agent CrewAI Hierarchy**, **GraphRAG Evidence Synthesis**, an **Observable Hybrid Graph Engine**, **Multi-Factor Case Similarity Engine**, **Strict Policy & HITL Guardrails**, and a live **Cyber-Analyst Cockpit** (`Obsidian Vector` design system).

---

## ⚡ Quick Start: Core Commands

### 1. Run Hackathon Judge Readiness Self-Check
Validates environment, dataset integrity, hybrid graph status, 20/20 benchmark files, 6 domain validators, anti-hallucination audits, and sandbox gateway:
```bash
python tests/judge_readiness.py
```

### 2. Run Canonical Investigation Pipeline (Single Case or All)
Run an autonomous forensic investigation for a specific case with two-stage action evolution and customer verification:
```bash
# Single benchmark case (fast mode)
python -m agent.run_investigation --case-id HHG-001

# Single benchmark case with customer denial simulation
python -m agent.run_investigation --case-id HHG-001 --customer-response denied_fraud

# Run all 20 benchmark cases in canonical pipeline
python -m agent.run_investigation --all
```

### 3. Run One-Command Interactive Guided Demo
Walks judges through key forensic attack typologies, syndicates, customer verification, and institutional sandbox action execution:
```bash
python run_demo.py
```

### 4. Run Official 20-Case Benchmark Evaluation & Validator Suite
Executes the full pipeline across all 20 benchmark cases (`HHG-001` through `HHG-020`), enforces 100% schema compliance, and runs the 6-part Master Validator Suite:
```bash
python run_benchmark.py
```

### 5. Launch Interactive Analyst Cockpit UI
Launches the live threading HTTP backend and dark-mode cybersecurity cockpit:
```bash
python ui/serve.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser to interact with the multi-hop SVG evidence graph, 72-hour rolling velocity timeline, uncertainty radial gauge, FinCEN SAR tab, and human sign-off action buttons.

---

## 🏛️ System Architecture

```
                                  [ TRIGGER LAYER ]
                        Risk Score | Customer Dispute | Analyst
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │   11-Agent CrewAI Autonomous Pipeline  │
                      │  (Ingestion ➔ Forensic ➔ Anomaly ➔     │
                      │   Memory ➔ Step-Up ➔ Policy ➔ Master)  │
                      └───────────────────┬────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
      [ TIGERGRAPH HYBRID ENGINE ]                   [ SEMANTIC VECTOR STORE ]
   - Live Savanna TG Cloud Cluster                - TF-IDF Dense Policy Index
   - Observable Local Fallback Engine             - Fraud Typologies Store
   - 2-Hop Multi-Entity Subgraph                  - Dynamic Case Memory Index
   - Shared Hardware Syndicate Rings              - Multi-Factor Similarity Engine
   - 72-Hour Velocity Rolling Window                 (Text 0.4 + Graph 0.4 + Pattern 0.2)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                              [ GRAPHRAG SYNTHESIS ]
                      Structured LLM Dossiers (No Raw Dumps)
                                          │
                                          ▼
                           [ TRACEABLE UNCERTAINTY ]
                      P(Fraud) = Prior + Corroboration - Mitigating
                                          │
                          Sufficient Evidence to Act?
                             ├── [NO] ──> [CONTROLLED INQUIRY]
                             │            SMS Verification / Step-Up Auth
                             │            Re-assess with ground truth
                             └── [YES] ─> Continue
                                          │
                                          ▼
                               [ STRICT POLICY ENGINE ]
                        Bank Fraud Policy v1.0 Rules R1–R10
                             ├── auto: CREATE_CASE, CLOSE_NO_FRAUD
                             ├── L1:   BLOCK_CARD (≤ $2,500)
                             └── L2:   BLOCK_ALL_CARDS, FILE_REPORT (> $2,500 / Syndicate)
                                          │
                                          ▼
                   [ INSTITUTIONAL SANDBOX ACTION GATEWAY ]
                        - State-Machine Card Transitions (ACTIVE ➔ BLOCKED)
                        - HITL Authorization Gateways
                        - Nonce-Protected Idempotent Audit Trails
                                          │
                                          ▼
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
           [ EXPLAINABILITY & SAR ]               [ GRAPH CASE MEMORY ]
        - Two-Stage Action Evolution           - Write Case Vertex to TigerGraph
          (initial vs final + what_changed)    - Dynamic Precedent Recall
        - FinCEN SAR 6-Question Narrative      - Pattern Feedback Loop
          (Who, What, When, Where, How, Why)
```

---

## 🤖 11-Agent Architecture Breakdown

For complete forensic details, tools, schemas, and fallback procedures, see [docs/AGENT_RESPONSIBILITIES.md](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/docs/AGENT_RESPONSIBILITIES.md).

| Agent # | Agent Name | Primary Specialty | Key GSQL / Tool Invocation |
|---|---|---|---|
| **Agent 1** | **Fraud Ingestion Agent** | Alert ingestion & parameter validation | Alert Feed, IEEE-CIS Transaction Ingest |
| **Agent 2** | **TigerGraph Evidence Agent** | Multi-hop graph traversal & subgraph expansion | `find_shared_devices_tool`, `trace_fraud_ring` |
| **Agent 3** | **Pattern Analysis Agent** | Typology pattern & anomaly recognition | Card Testing, ATO, CNP, Out-of-Region engines |
| **Agent 4** | **Case Lifecycle Agent** | Case ledger & millisecond audit trail | Audit state machine (`ACTIVE` ➔ `RESOLVED`) |
| **Agent 5** | **Case Memory Agent** | Graph & vector historical case retrieval | `SimilarCasesEngine` (Text + Graph + Pattern) |
| **Agent 6** | **Step-Up Validation Agent** | Controlled cardholder verification | `CustomerVerificationProvider` (SMS/Push) |
| **Agent 7** | **Action Recommender Agent** | Multi-action recommendation engine | `DecisionEngine` two-stage action evolution |
| **Agent 8** | **Policy & Guardrails Agent** | Bank Fraud Policy v1.0 (Rules R1-R10) | Authority route gating (`auto`, `L1`, `L2`) |
| **Agent 9** | **Early Stopping Agent** | Efficiency & stopping criteria controller | Uncertainty threshold & confidence saturation |
| **Agent 10** | **Explainability Agent** | FinCEN SAR & transparent plain-English audit | 6-Question FinCEN SAR narrative synthesis |
| **Agent 11** | **Master Decision Validator** | 4-rule cross-consistency verification | Final 3-part schema audit & route reconciliation |

---

## 📊 Benchmark Evaluation Summary (20 Cases)

| Metric | Result | Benchmark Standard | Status |
|---|---|---|---|
| **Total Cases Evaluated** | **20 / 20** | 20 benchmark cases | **100.0% Complete** |
| **Schema Compliance Rate** | **20 / 20 (100.0%)** | Zero schema penalties | **PASS (0 errors)** |
| **System Crash Rate** | **0.0%** | Zero unhandled exceptions | **PERFECT** |
| **Confirmed Fraud Verdicts** | **17 cases (85.0%)** | Realistic attack distribution | **PASS** |
| **Cleared Legitimate Verdicts** | **3 cases (15.0%)** | False alarm resolution (Rule R3) | **PASS** |
| **FinCEN SAR Filings** | **6 filings** | Statutory SAR criteria (Rule R6) | **PASS** |
| **Average Latency** | **0.18 seconds / case** | Real-time banking SLA (< 5s) | **EXCEEDED (0.18s)** |
| **Average Tool Calls** | **9.0 calls / case** | Multi-hop graph & memory queries | **OPTIMAL** |
| **Average Context Tokens** | **11,200 tokens / case** | Structured markdown dossiers | **OPTIMAL** |

### Per-Case Benchmark Results (`cases/*.json`):

| Case ID | Flagged Txn | Trigger | Verdict | Status | Pattern | Exposure | SAR File | Actions (Final) |
|---|---|---|---|---|---|---|---|---|
| **HHG-001** | 3514030 | `risk_score` | `fraud` | `closed_fraud` | `out_of_region_use` | $77.07 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-002** | 3478782 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_fraud` | $292.36 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-003** | 3530164 | `customer_report` | `fraud` | `closed_fraud` | `out_of_region_use` | $49.00 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-004** | 3583227 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $128.33 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-005** | 3523199 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $100.07 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT` |
| **HHG-006** | 3476682 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $482.12 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT` |
| **HHG-007** | 3514948 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_fraud` | $111.92 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-008** | 3558054 | `customer_report` | `fraud` | `closed_fraud` | `card_testing` | $55.68 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-009** | 3581141 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_fraud` | $30.02 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-010** | 3506725 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $1,000.03 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT` |
| **HHG-011** | 3583368 | `customer_report` | `fraud` | `closed_fraud` | `card_testing` | $131.30 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-012** | 3553342 | `risk_score` | `legitimate` | `closed_legitimate` | `none` | $0.00 | `False` | `CLOSE_NO_FRAUD` |
| **HHG-013** | 3526826 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $35.66 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-014** | 3478561 | `analyst_request` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $74.96 | `True` | `CREATE_CASE`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` |
| **HHG-015** | 3464869 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $599.94 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT` |
| **HHG-016** | 3534820 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $59.67 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-017** | 3450629 | `risk_score` | `legitimate` | `closed_legitimate` | `none` | $0.00 | `False` | `CLOSE_NO_FRAUD` |
| **HHG-018** | 3491361 | `customer_report` | `fraud` | `closed_fraud` | `out_of_region_use` | $39.08 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-019** | 3503878 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $99.92 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT` |
| **HHG-020** | 3509359 | `risk_score` | `legitimate` | `closed_legitimate` | `none` | $0.00 | `False` | `CLOSE_NO_FRAUD` |

---

## 🧪 Comprehensive Test & Verification Suite

Our repository is rigorously verified with dedicated test suites covering all audit layers:

```bash
# 1. Master Judge Readiness Suite (All 8 Subsystems)
python tests/judge_readiness.py

# 2. Dynamic Next-Best-Action Scenarios (A through E)
python -m unittest tests/test_next_best_action_dynamics.py

# 3. Real Human-In-The-Loop Enforcement & Policy Gating
python -m unittest tests/test_hitl_enforcement.py

# 4. Multi-Factor Case Similarity Engine (Text + Graph + Pattern)
python -m unittest tests/test_graph_case_similarity.py

# 5. Full 6-Part Master Domain Validators on 20 Cases
python -m tests.validate_cases cases/
```

---

## 📁 Repository Structure

```
├── README.md                       # Primary system documentation and quickstart
├── run_demo.py                     # One-command guided interactive demo for judges
├── run_benchmark.py                # Official 20-case benchmark runner & evaluation
├── cases/                          # 20 Submission-ready JSON files (HHG-001.json - HHG-020.json)
├── benchmark_results/              # Detailed evaluation summary, metrics, and report
├── agent/                          # Core autonomous investigation loop
│   ├── run_investigation.py        # Canonical CLI entry point
│   ├── eleven_agents_pipeline.py   # 11-Agent CrewAI pipeline orchestration
│   ├── agent.py                    # 8-stage stateful investigation orchestrator
│   ├── case.py                     # Case data object with audit trails & graph persistence
│   ├── action_gateway.py           # Production-inspired institutional sandbox action gateway
│   ├── customer_verification.py    # Customer verification provider abstraction (mock/webhook)
│   ├── uncertainty_engine.py       # Traceable Bayesian uncertainty scoring & confidence logic
│   ├── policy_engine.py            # Bank Fraud Policy v1.0 enforcement (Rules R1-R10)
│   ├── decision_engine.py          # Two-stage next best action evolution (initial vs final)
│   ├── sar_generator.py            # FinCEN 6-question regulatory narrative generator
│   └── case_formatter.py           # Strict 3-part schema validator (zero penalties)
├── graph/                          # TigerGraph database & GraphRAG layer
│   ├── tigergraph_tools.py         # Multi-tenant TigerGraph connection & observable cloud probe
│   ├── subgraph_extractor.py       # Observable hybrid subgraph extractor (Cloud + resilient local)
│   ├── similar_cases_engine.py     # Multi-factor similarity engine (Text 0.4 + Graph 0.4 + Pattern 0.2)
│   ├── graphrag_synthesizer.py     # Structured markdown investigative dossier formatter
│   ├── case_memory.py              # Graph vertex persistence of resolved cases
│   ├── pattern_registry.py         # Dynamic pattern feedback loop for recurring entities
│   ├── load_vector_store.py        # TF-IDF dense vector index over policies & closed cases
│   └── schema.gsql                 # Formal GSQL schema definition (vertices & edges)
├── ui/                             # Analyst Cockpit Dashboard
│   ├── serve.py                    # Multi-endpoint REST API server & action execution gateway
│   └── test_ui.py                  # End-to-end UI and API automated test suite
├── src/                            # React 18 frontend (Obsidian Vector design system)
├── tests/                          # Integrity testing & judge validation
│   ├── judge_readiness.py          # Master 8-subsystem pre-flight judge readiness test
│   ├── test_next_best_action_dynamics.py # Scenarios A-E dynamic NBA verification
│   ├── test_hitl_enforcement.py    # Negative & positive HITL authorization tests
│   ├── test_graph_case_similarity.py # Tri-factor graph similarity verification
│   ├── validate_submission.py      # End-to-end submission auditor (0 error assertion)
│   └── validate_cases.py           # 6-part domain validator suite
└── docs/                           # Documentation & Deliverables
    ├── AGENT_RESPONSIBILITIES.md   # Deep-dive 11-agent forensic specification
    ├── blog-post.md                # Publication-ready technical blog post
    ├── demo-script.md              # 5-minute video demonstration script & recording guide
    └── decisions.md                # Technical decisions and architectural rationale
```

---

## ⚖️ License
Licensed under the Apache License, Version 2.0. Built for the TigerGraph × Hacker House Goa Agentic Fraud Investigation Hackathon.
