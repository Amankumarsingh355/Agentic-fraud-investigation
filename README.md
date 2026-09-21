# TigerGraph Agentic Fraud Investigation Suite (HHGOA_IEEE)

[![TigerGraph](https://img.shields.io/badge/TigerGraph-Savanna%20%7C%20Enterprise-orange.svg)](https://www.tigergraph.com/)
[![GraphRAG](https://img.shields.io/badge/GraphRAG-Multi--Hop%20Evidence-06B6D4.svg)](https://github.com/tigergraph/tigergraph-mcp)
[![FinCEN SAR](https://img.shields.io/badge/FinCEN%20SAR-Compliant-10B981.svg)](https://www.fincen.gov/)
[![Benchmark Evaluation](https://img.shields.io/badge/Benchmark-20%2F20%20Cases%20(100%25)-brightgreen.svg)](cases/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An end-to-end, production-grade autonomous AI fraud investigation system built for the **TigerGraph × Hacker House Goa** hackathon. 

Powered by **TigerGraph GSQL**, **GraphRAG evidence synthesis**, an **8-stage stateful agent loop**, **traceable uncertainty engine**, **strict policy gating**, and a live **cyber-analyst cockpit** (`Obsidian Vector` design system).

---

## ⚡ Quick Start: One-Command Execution

### 1. Run Benchmark Evaluation (All 20 Cases)
Runs the autonomous agent across all 20 benchmark cases (`HHG-001` through `HHG-020`), enforces memory isolation, outputs schema-validated JSON files into `cases/`, and logs metrics:
```bash
python eval/evaluate_benchmark.py
```

### 2. Launch Interactive Analyst Cockpit UI
Launches the live threading HTTP server and dark-mode cybersecurity cockpit:
```bash
python ui/serve.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser to interact with the multi-hop SVG evidence graph, 72-hour rolling velocity timeline, uncertainty radial gauge, FinCEN SAR tab, and human sign-off action buttons.

### 3. Run Submission Integrity Audit
Runs strict validation on all 20 submission files, asserting 0 schema violations, 0 placeholders, valid entity grounding, and FinCEN SAR conditional compliance:
```bash
python tests/validate_submission.py
```

---

## 🏛️ System Architecture

```
                                  [ TRIGGER LAYER ]
                        Risk Score | Customer Dispute | Analyst
                                         │
                                         ▼
                     ┌────────────────────────────────────────┐
                     │   Autonomous Fraud Investigation Agent  │
                     └───────────────────┬────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [ TIGERGRAPH GSQL ENGINE ]                     [ SEMANTIC VECTOR STORE ]
  - 2-Hop Multi-Entity Subgraph                  - TF-IDF Dense Policy Index
  - Shared Hardware Syndicate Rings              - Fraud Typologies Store
  - 72-Hour Velocity Rolling Window              - Historical Case Memory Index
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
                       Bank Fraud Policy v1.0 Rules R1–R8
                            ├── auto: CREATE_CASE, CLOSE_NO_FRAUD
                            ├── L1:   BLOCK_CARD (≤ $2,500)
                            └── L2:   BLOCK_ALL_CARDS, FILE_REPORT (> $2,500 / Syndicate)
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

## 📊 Benchmark Evaluation Summary (20 Cases)

| Metric | Result | Benchmark Standard | Status |
|---|---|---|---|
| **Total Cases Evaluated** | **20 / 20** | 20 benchmark cases | **100.0% Complete** |
| **Schema Compliance Rate** | **20 / 20 (100.0%)** | Zero schema penalties | **PASS (0 errors)** |
| **System Crash Rate** | **0.0%** | Zero unhandled exceptions | **PERFECT** |
| **Confirmed Fraud Verdicts** | **17 cases (85.0%)** | Realistic attack distribution | **PASS** |
| **Cleared Legitimate Verdicts** | **3 cases (15.0%)** | False alarm resolution (Rule R3) | **PASS** |
| **FinCEN SAR Filings** | **6 filings** | Statutory SAR criteria (Rule R6) | **PASS** |
| **Average Latency** | **0.17 seconds / case** | Real-time banking SLA (< 5s) | **EXCEEDED (0.17s)** |
| **Average Tool Calls** | **9.0 calls / case** | Multi-hop graph & memory queries | **OPTIMAL** |
| **Average Context Tokens** | **11,200 tokens / case** | Structured markdown dossiers | **OPTIMAL** |

### Per-Case Benchmark Results (`cases/*.json`):

| Case ID | Flagged Txn | Trigger | Verdict | Status | Pattern | Exposure | SAR File | Actions (Final) |
|---|---|---|---|---|---|---|---|---|
| **HHG-001** | 3514030 | `risk_score` | `fraud` | `closed_fraud` | `out_of_region_use` | $77.07 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-002** | 3478782 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_fraud` | $292.36 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-003** | 3530164 | `customer_report` | `fraud` | `closed_fraud` | `out_of_region_use` | $49.00 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-004** | 3583227 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $128.33 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-005** | 3523199 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $100.07 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` |
| **HHG-006** | 3476682 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $482.12 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` |
| **HHG-007** | 3514948 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_fraud` | $111.92 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-008** | 3558054 | `customer_report` | `fraud` | `closed_fraud` | `card_testing` | $55.68 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-009** | 3581141 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_fraud` | $30.02 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-010** | 3506725 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $1,000.03 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` |
| **HHG-011** | 3583368 | `customer_report` | `fraud` | `closed_fraud` | `card_testing` | $131.30 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-012** | 3553342 | `risk_score` | `legitimate` | `closed_legitimate` | `none` | $0.00 | `False` | `CLOSE_NO_FRAUD` |
| **HHG-013** | 3526826 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $35.66 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-014** | 3478561 | `analyst_request` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $74.96 | `True` | `CREATE_CASE`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS`, `BLOCK_CARD` |
| **HHG-015** | 3464869 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $599.94 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` |
| **HHG-016** | 3534820 | `customer_report` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $59.67 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-017** | 3450629 | `risk_score` | `legitimate` | `closed_legitimate` | `none` | $0.00 | `False` | `CLOSE_NO_FRAUD` |
| **HHG-018** | 3491361 | `customer_report` | `fraud` | `closed_fraud` | `out_of_region_use` | $39.08 | `False` | `CREATE_CASE`, `BLOCK_CARD` |
| **HHG-019** | 3503878 | `risk_score` | `fraud` | `closed_fraud` | `card_not_present_new_device` | $99.92 | `True` | `CREATE_CASE`, `BLOCK_CARD`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` |
| **HHG-020** | 3509359 | `risk_score` | `legitimate` | `closed_legitimate` | `none` | $0.00 | `False` | `CLOSE_NO_FRAUD` |

---

## 📁 Repository Structure

```
├── PROGRESS.md                     # 10-Phase progression log and acceptance gate tracking
├── README.md                       # Primary system documentation and quickstart
├── cases/                          # 20 Submission-ready JSON files (HHG-001.json - HHG-020.json)
├── agent/                          # Core autonomous investigation loop
│   ├── agent.py                    # 8-stage stateful investigation orchestrator
│   ├── case.py                     # Case data object with audit trails & graph persistence
│   ├── uncertainty_engine.py       # Traceable Bayesian uncertainty scoring & confidence logic
│   ├── policy_engine.py            # Bank Fraud Policy v1.0 enforcement (Rules R1-R8)
│   ├── decision_engine.py          # Two-stage next best action evolution (initial vs final)
│   ├── sar_generator.py            # FinCEN 6-question regulatory narrative generator
│   ├── case_formatter.py           # Strict 3-part schema validator (zero penalties)
│   └── action_executor.py          # Action dispatch & side-effect stubs
├── graph/                          # TigerGraph database & GraphRAG layer
│   ├── schema.gsql                 # Formal GSQL schema definition (vertices & edges)
│   ├── loading_jobs.gsql           # GSQL bulk loading jobs
│   ├── subgraph_extractor.py       # 2-hop multi-entity connected subgraph extractor
│   ├── graphrag_synthesizer.py     # Structured markdown investigative dossier formatter
│   ├── similar_cases_engine.py     # Hybrid dense vector + graph precedent retrieval
│   ├── case_memory.py              # Graph vertex persistence of resolved cases
│   ├── pattern_registry.py         # Dynamic pattern feedback loop for recurring entities
│   ├── load_vector_store.py        # TF-IDF dense vector index over policies & closed cases
│   └── mcp_server.py               # TigerGraph Model Context Protocol (MCP) server
├── ui/                             # Analyst Cockpit Dashboard (Stitch Obsidian Vector)
│   ├── index.html                  # Interactive single-page application (SVG graph, timeline, gauge)
│   ├── serve.py                    # Threading HTTP server delivering dashboard & REST API
│   └── test_ui.py                  # End-to-end UI and API automated test suite
├── eval/                           # Benchmark evaluation suite
│   └── evaluate_benchmark.py       # Full benchmark runner across all 20 cases
├── tests/                          # Integrity testing
│   └── validate_submission.py      # End-to-end submission auditor (0 error assertion)
└── docs/                           # Documentation & Deliverables
    ├── blog-post.md                # Publication-ready technical blog post
    ├── demo-script.md              # 5-minute video demonstration script & recording guide
    ├── social-post.md              # Formatted Twitter/X and LinkedIn announcements
    ├── benchmark-evaluation-report.md # Comprehensive Phase 9 evaluation report
    ├── phase8-ui-report.md         # UI/UX verification report
    └── decisions.md                # Technical decisions and architectural rationale
```

---

## 🎯 10-Phase Progression Checklist

- [x] **Phase 0: Setup**: Environment configured, `tigergraph-mcp` installed, framework decisions recorded in `docs/decisions.md`.
- [x] **Phase 1: Data Understanding & Graph Schema**: All data files profiled, vector vs graph partitioned, schema authored in `graph/schema.gsql`.
- [x] **Phase 2: Data Ingestion & Vector Store**: 5,587 documents embedded and indexed into `data/vector_store/`, 0 failed rows in `docs/ingestion-report.md`.
- [x] **Phase 3: Graph Algorithms & Pattern Library**: Parameterized GSQL pattern queries for all 5 typologies and hardware ring detection in `docs/query-test-report.md`.
- [x] **Phase 4: GraphRAG Layer & MCP Tools**: Structured LLM dossiers synthesized without raw JSON dumps, 6 MCP tools exposed in `docs/graphrag-test-report.md`.
- [x] **Phase 5: Agent Core (Investigation Loop)**: 8-stage stateful loop, traceable uncertainty, strict policy gating in `docs/phase5-agent-report.md`.
- [x] **Phase 6: Case Memory & Dynamic Knowledge Feedback**: Resolved cases persisted to TigerGraph, dynamic precedent recall verified in `docs/phase6-memory-report.md`.
- [x] **Phase 7: Explainability & Exact Output Format**: Exact 3-part JSON format, two-stage action evolution, FinCEN SAR generator in `docs/phase7-output-format-report.md`.
- [x] **Phase 8: UI / UX Analyst Dashboard**: Interactive dark-mode cockpit (Stitch `Obsidian Vector`), SVG evidence graph, live sign-offs in `docs/phase8-ui-report.md`.
- [x] **Phase 9: Benchmark Evaluation (20 Cases)**: All 20 cases evaluated, 100% schema valid (0 penalties), 0 crashes in `docs/benchmark-evaluation-report.md`.
- [x] **Phase 10: Submission Polish & Deliverables**: Final integrity audit passed, technical blog post, video demo script, and social posts completed.

---

## ⚖️ License
Licensed under the Apache License, Version 2.0. Built for the TigerGraph × Hacker House Goa Agentic Fraud Investigation Hackathon.
