# Hackathon Progress: TigerGraph Agentic Fraud Investigation (HHGOA_IEEE)

## Phase Status Summary

| Phase | Title | Status | Gate Criteria / Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Setup** | **COMPLETED** | Repo scaffolded, `tigergraph-mcp` cloned & installed, framework/LLM choices documented in `docs/decisions.md`. |
| **Phase 1** | **Data Understanding & Graph Schema** | **COMPLETED** | README synthesized in `docs/dataset-notes.md`, all data files profiled in `docs/data-profile.md`, vector vs. graph partitioned in `docs/vector-vs-graph.md`, schema & loading jobs authored in `graph/schema.gsql` and `graph/loading_jobs.gsql`. |
| **Phase 2** | **Data Ingestion & Vector Store** | **COMPLETED** | GSQL loading jobs written, 5,587 documents embedded and indexed into `data/vector_store/`, 20 benchmark cases isolated in namespace `eval_benchmark`, 0 failed rows, 5/5 spot checks passed in `docs/ingestion-report.md`. |
| **Phase 3** | **GSQL Queries & Graph Pattern Detection** | Planned | Parameterized GSQL pattern detection queries for all 5 typologies + syndicate / device sharing traversals. |
| **Phase 4** | **Agent Core & Policy/Permission Engine** | Planned | LangGraph stateful agent with strict approval routing (`auto`, `L1`, `L2`) and mocked action execution. |
| **Phase 5** | **Case Progression & Uncertainty Loop** | Planned | Dynamic evidence loop with calibrated fraud probability and stop conditions. |
| **Phase 6** | **Decision Engine & Next Best Action** | Planned | Two-stage action progression (`initial` vs `final`), `what_changed`, and FinCEN SAR narrative engine. |
| **Phase 7** | **Case Memory & Graph Persistence** | Planned | Writing new cases back to graph memory with benchmark isolation. |
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 2 Detail Log

- **GSQL Loading Jobs**:
  - Authored `graph/loading_jobs.gsql` with jobs: `load_transactions`, `load_identity`, `load_closed_cases`, and `load_benchmark_cases`.
  - Authored `graph/load_data.py` providing automated deployment and execution via `pyTigerGraph`.
- **Knowledge Corpora Created**:
  - `docs/knowledge/fraud_policy.md`: Complete text of Bank Fraud Policy v1.0 (rules R1–R10, approval routes, actions).
  - `docs/knowledge/fraud_typologies.md`: Detailed signatures, graph traversal patterns, and indicators for the 5 canonical patterns + undocumented abuse.
  - `docs/knowledge/regulatory_fincen_fatf_ffiec.md`: Regulatory narrative guidelines (FinCEN 6 mandatory questions: Who, What, When, Where, How, Why), FATF typologies, and FFIEC red flags.
- **Vector Store Indexed**:
  - Implemented `graph/load_vector_store.py`.
  - Successfully indexed 5,587 documents (10 policy rules, 6 typology guides, regulatory standards, and 5,565 closed case analyst notes) into `data/vector_store/`.
  - Smoke tests passed: semantic search correctly retrieves policy rules and precedent cases based on natural language queries.
- **Benchmark Case Isolation**:
  - 20 evaluation cases loaded with `is_benchmark = TRUE` and `namespace = "eval_benchmark"`.
  - Historical memory cases loaded with `is_benchmark = FALSE` and `namespace = "case_memory"`.
  - Verified 0 overlap between evaluation cases and historical case memory.
- **Validation Suite & Spot-Checks**:
  - `graph/validate_ingestion.py` executed with 0 failed rows:
    - `transactions.csv`: 590,742 rows verified.
    - `identity.csv`: 144,432 rows verified.
    - `closed_cases_history.csv`: 5,565 rows verified.
    - `case_pack.csv`: 20 rows verified.
  - Spot-checked 5 graph entities:
    1. Customer `C00259`: `OWNS` edge to `C00259-K1`, `PERFORMED` edge to 14 transactions.
    2. Card `C00259-K1`: Temporal sequence `NEXT` edge verified with positive `delta_s`.
    3. Transaction `3005755`: Online `USED_DEVICE` edge to composite device profile verified.
    4. Transaction `3000001`: Geographic `BILLED_IN` edge to billing region verified.
    5. Case `CC-0001`: `ON_CARD` and `INVOLVES` edges to primary card and first fraud transaction verified.
  - Full validation log saved to `docs/ingestion-report.md`.
