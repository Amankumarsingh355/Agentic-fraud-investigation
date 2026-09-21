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
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

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
