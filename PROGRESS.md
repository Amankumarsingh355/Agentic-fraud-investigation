# Hackathon Progress: TigerGraph Agentic Fraud Investigation (HHGOA_IEEE)

## Phase Status Summary

| Phase | Title | Status | Gate Criteria / Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Setup** | **COMPLETED** | Repo scaffolded, `tigergraph-mcp` cloned & installed, framework/LLM choices documented in `docs/decisions.md`. |
| **Phase 1** | **Data Understanding & Graph Schema** | **COMPLETED** | README synthesized in `docs/dataset-notes.md`, all data files profiled in `docs/data-profile.md`, vector vs. graph partitioned in `docs/vector-vs-graph.md`, schema & loading jobs authored in `graph/schema.gsql` and `graph/loading_jobs.gsql`. |
| **Phase 2** | **Data Ingestion & Vector Store** | **COMPLETED** | GSQL loading jobs written, 5,587 documents embedded and indexed into `data/vector_store/`, 20 benchmark cases isolated in namespace `eval_benchmark`, 0 failed rows, 5/5 spot checks passed in `docs/ingestion-report.md`. |
| **Phase 3** | **Graph Algorithms & Pattern Library** | **COMPLETED** | Parameterized GSQL pattern queries implemented for all 5 typologies (`card_testing`, `cnp`, `cnp_new_device`, `out_of_region`, `ato`), ring detection algorithms written, hybrid similar prior cases engine built, spot checks passed in `docs/query-test-report.md`. |
| **Phase 4** | **GraphRAG Layer & MCP Tools** | **COMPLETED** | Multi-hop subgraph extractor, policy vector retrieval, structured LLM-ready markdown dossiers synthesized, MCP server exposing 6 tools, gate tested on 3 sample transactions in `docs/graphrag-test-report.md`. |
| **Phase 5** | **Agent Core: Investigation Loop** | **COMPLETED** | Stateful 8-stage investigation loop, inspectable uncertainty/confidence engine, strict policy gating (`auto`, `L1`, `L2`), realistic action stubs, gate passed across 3 non-benchmark cases in `docs/phase5-agent-report.md`. |
| **Phase 6** | **Case Memory & Dynamic Knowledge Feedback** | **COMPLETED** | Graph persistence of case outcomes, hybrid case memory retrieval, pattern library feedback registry, gate verified: running same type of case twice retrieves memory from first run in `docs/phase6-memory-report.md`. |
| **Phase 7** | **Explainability & Output Format** | **COMPLETED** | Exact 3-part JSON submission format (`case`, `sar`, `next_best_actions`), two-stage action evolution (`initial` vs `final` + `what_changed`), FinCEN SAR 6-question narrative generator, graph persistence confirmed, gate passed with 0 schema errors in `docs/phase7-output-format-report.md`. |
| **Phase 8** | **UI / UX Analyst Dashboard** | **COMPLETED** | StitchMCP project `8720938275256246642` (`Obsidian Vector`), interactive SVG evidence graph, 72h velocity timeline, uncertainty radial gauge, policy sign-off workflow, live HTTP/REST server in `ui/serve.py`, gate verified in `docs/phase8-ui-report.md`. |
| **Phase 9** | **Benchmark Evaluation (20 Cases)** | **COMPLETED** | Executed agent across all 20 benchmark cases, 100% schema valid (0 penalties) in `cases/HHG-*.json`, 0 crashes, 6 SAR filings, 0.08s avg latency, documented in `docs/benchmark-evaluation-report.md`. |
| **Phase 10** | **Submission Deliverables & Final Polish** | In Progress | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 7 Detail Log: Explainability & Exact Output Format

- **Exact 3-Part Submission Schema Formatter (`agent/case_formatter.py`)**:
  - Implemented strict translation and validation logic conforming to README.md specifications:
    1. **Part 1 (`case`)**: `status`, `verdict`, `fraud_probability`, `pattern`, `pattern_description`, `affected_txn_ids`, `first_suspicious_txn_id`, `connected_card_ids`, `connected_device_profiles`, `exposure_usd`, `evidence` (each with `claim`, `source`, `ref`, `entity_ids`), `similar_prior_cases`, `summary`, `written_to_graph`, `graph_case_id`.
    2. **Part 2 (`sar`)**: FinCEN Suspicious Activity Report block (`file`, `reason`, `narrative`, `subjects`, `total_amount_usd`, `activity_dates`). Strictly formatted: when `file == false`, fields are empty (`""`, `[]`, `0`, `[]`).
    3. **Part 3 (`next_best_actions`)**: Two-stage progression (`initial`, `final`, and `what_changed`), with actions, approval routes (`auto`, `L1`, `L2`), and rule justifications.
  - Implemented comprehensive `validate_schema()` asserting 100% compliance on enums, ranges, and cross-field constraints.
- **FinCEN SAR 6-Question Compliance Generator (`agent/sar_generator.py`)**:
  - Automatically synthesizes complete regulatory narratives answering **Who, What, When, Where, How, and Why** (6 to 12 sentences).
  - Resolves subject IDs (customer, card, connected syndicate cards, device profile) and active date windows.
- **Two-Stage Decision Evolution Engine (`agent/decision_engine.py`)**:
  - Formulates initial recommendations before evidence gathering (e.g. `VERIFY_WITH_CUSTOMER`, `MONITOR_CARD`).
  - Dispatches controlled evidence requests (`customer_validation`, `step_up_auth`, `analyst_info`) with explicit assumed responses.
  - Formulates final recommendations after evidence (e.g. `BLOCK_CARD`, `CREATE_CASE`, `FILE_REPORT`).
  - Summarizes the decision delta in `what_changed`.
- **Phase 7 Verification Gate (`agent/test_output_format.py`)**:
  - Validated sample case `HHG-001` (Txn `3514030`):
    - Status: `closed_fraud`, Verdict: `fraud`, Fraud Prob: `0.98`, Pattern: `out_of_region_use`.
    - Next Best Actions: 3 initial (`CREATE_CASE`, `VERIFY_WITH_CUSTOMER`, `MONITOR_CARD`) $\rightarrow$ 2 final (`CREATE_CASE`, `BLOCK_CARD`).
    - What Changed: *"Customer denial raised fraud probability from 0.71 to 0.98, confirming the need for permanent card block and fraud case creation."*
    - Written to Graph: `True` (`CASE-3514030`).
    - Schema Validation: **0 errors**, 100% compliant with README requirements.
  - Validated SAR generation on syndicate case `HHG-014` (Txn `3478561`):
    - `sar.file = True`, Rule R6 triggered, 8 subjects resolved, full 6-question narrative generated with **0 validation errors**.
  - Detailed report saved to `docs/phase7-output-format-report.md`.

---

## Phase 8 Detail Log: UI / UX Analyst Dashboard

- **Stitch Design System & Screen Generation**:
  - Leveraged `StitchMCP` to scaffold project `projects/8720938275256246642` and generated cyber-analyst screen `c14071494d6e48c1b33613e72f51e620`.
  - Applied the `Obsidian Vector` design theme: deep obsidian background (`#0A0E17`), telemetry cyan accents (`#06B6D4`), elevated slate panels (`#101726`), emerald safe states (`#10B981`), and crimson fraud alerts (`#EF4444`).
- **Interactive Single-Page Application (`ui/index.html`)**:
  - **Dynamic Case Selector**: Populates dropdown from `/api/cases` with status indicators (`✓` generated, `○` pending), pattern labels, and exposure amounts.
  - **Interactive 2-Hop Subgraph (SVG)**: Visualizes Customer, Card, Target Txn, Billing Region, and Device/Terminal nodes. Dynamically expands into syndicate ring topology with red dashed `SHARED_HW` edges when syndicate patterns are detected.
  - **72-Hour Rolling Velocity Timeline**: Chronologically visualizes preceding authorization events relative to the flagged transaction.
  - **Uncertainty & Probability Radial Gauge**: Real-time SVG circular gauge illustrating fraud probability, uncertainty scores, and confidence classifications.
  - **Interactive Policy Sign-off Workflow**: Policy-gated actions render with a **"✓ Sign-off & Execute"** button; analyst approvals dispatch live via POST `/api/approve_action` and update UI badges in real time.
  - **FinCEN SAR Tab & Audit Trail**: Full regulatory 6-question filing tab and chronological audit trail logging all investigation stages.
- **RESTful API Backend (`ui/serve.py`)**:
  - Threading HTTP server delivering static assets and REST endpoints (`/api/cases`, `/api/case`, `/api/investigate`, `/api/approve_action`).
  - Supports on-demand live investigation trigger and persistent approval auditing in `data/analyst_approvals.jsonl`.
- **Phase 8 Verification Gate (`ui/test_ui.py`)**:
  - Executed automated test suite across 5 test vectors:
    1. HTML dashboard delivery (`GET /`) - Status 200 OK.
    2. Case list retrieval (`GET /api/cases`) - 23 cases enumerated.
    3. Case record schema check (`GET /api/case?id=HHG-001`) - Validated with 0 errors.
    4. Analyst sign-off workflow (`POST /api/approve_action`) - Approval logged & executed.
    5. Live Agent Investigation Trigger (`POST /api/investigate`) - Executed `HHG-003` end-to-end, validated with 0 schema errors.
  - Verification report recorded in `docs/phase8-ui-report.md`.

---

## Phase 9 Detail Log: Benchmark Evaluation (20 Cases)

- **Execution of All 20 Benchmark Cases (`eval/evaluate_benchmark.py`)**:
  - Investigated all 20 cases from `data/case_pack.csv` (`HHG-001` through `HHG-020`) using the autonomous agent.
  - Strictly enforced evaluation case isolation: all 20 cases were run with `is_benchmark=True`, ensuring benchmark cases were tagged with namespace `eval_benchmark` and excluded from case memory recall.
  - Persisted all 20 individual submission artifacts to `cases/HHG-001.json` through `cases/HHG-020.json`.
- **100% Schema Validation & Zero Scoring Penalties**:
  - Every single generated file was validated against `CaseFormatter.validate_schema()`.
  - Result: **20 / 20 cases (100.0%) passed strict schema validation with 0 errors**.
- **Performance & Detection Metrics**:
  - **Confirmed Fraud**: 17 cases (85.0%) across typologies: `card_not_present_new_device` (9), `out_of_region_use` (3), `card_testing` (2), `card_not_present_fraud` (3).
  - **Cleared Legitimate**: 3 cases (15.0%) — `HHG-012` (authorized travel spend), `HHG-017` (authorized recurring spend), `HHG-020` (authorized online spend). When cardholder verified legitimacy, the agent formulated `CLOSE_NO_FRAUD` / `UNRESTRICT_CARD`, cleanly clearing false alarms without customer friction.
  - **FinCEN SAR Regulatory Filings**: 6 cases triggered statutory filing under Rule R6 / exposure thresholds (`HHG-005`, `HHG-006`, `HHG-010`, `HHG-014`, `HHG-015`, `HHG-019`).
  - **Syndicate Ring Discovery**: Successfully uncovered the 52-account syndicate ring on `HHG-014` despite a near-zero model score (0.05).
  - **Turnaround Latency**: Average of **0.08 seconds per case**, demonstrating real-time banking scalability.
- **Baseline Comparisons**:
  - Documented in `docs/benchmark-evaluation-report.md`: superior to static threshold baseline (which misses low-scoring syndicate rings and produces excess false alarms) and human-analyst baseline (which suffers 20-45 min latency bottlenecks).


