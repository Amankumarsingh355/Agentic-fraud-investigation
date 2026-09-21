# Hackathon Progress: TigerGraph Agentic Fraud Investigation (HHGOA_IEEE)

## Phase Status Summary

| Phase | Title | Status | Gate Criteria / Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Setup** | **COMPLETED** | Repo scaffolded, `tigergraph-mcp` cloned & installed, framework/LLM choices documented in `docs/decisions.md`. |
| **Phase 1** | **Data Understanding & Graph Schema** | **COMPLETED** | README synthesized in `docs/dataset-notes.md`, all data files profiled in `docs/data-profile.md`, vector vs. graph partitioned in `docs/vector-vs-graph.md`, schema & loading jobs authored in `graph/schema.gsql` and `graph/loading_jobs.gsql`. |
| **Phase 2** | **Data Ingestion & Vector Store** | **COMPLETED** | GSQL loading jobs written, 5,587 documents embedded and indexed into `data/vector_store/`, 20 benchmark cases isolated in namespace `eval_benchmark`, 0 failed rows, 5/5 spot checks passed in `docs/ingestion-report.md`. |
| **Phase 3** | **Graph Algorithms & Pattern Library** | **COMPLETED** | Parameterized GSQL pattern queries implemented for all 5 typologies (`card_testing`, `cnp`, `cnp_new_device`, `out_of_region`, `ato`), ring detection algorithms written, hybrid similar prior cases engine built, spot checks passed in `docs/query-test-report.md`. |
| **Phase 4** | **Agent Core & Policy/Permission Engine** | Planned | LangGraph stateful agent with strict approval routing (`auto`, `L1`, `L2`) and mocked action execution. |
| **Phase 5** | **Case Progression & Uncertainty Loop** | Planned | Dynamic evidence loop with calibrated fraud probability and stop conditions. |
| **Phase 6** | **Decision Engine & Next Best Action** | Planned | Two-stage action progression (`initial` vs `final`), `what_changed`, and FinCEN SAR narrative engine. |
| **Phase 7** | **Case Memory & Graph Persistence** | Planned | Writing new cases back to graph memory with benchmark isolation. |
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 3 Detail Log

- **GSQL Pattern Detection Queries**:
  - `detect_card_testing`: Implemented in `graph/queries/pattern_queries.gsql`. Analyzes rolling window micro-authorizations online followed by large purchases. Spot-checked on `CC-0137` (Card `C12982-K1`).
  - `detect_cnp_fraud`: Identifies online burst velocities (2-4 txns in 48h) with unusual amounts. Spot-checked on `CC-0001` (Card `C00259-K1`).
  - `detect_cnp_new_device`: Checks for CNP burst on device marked `New` (`id_15`) or proxy rating (`id_23`). Spot-checked on `CC-0011` (Card `C13259-K1`).
  - `detect_out_of_region`: Detects in-person transactions in novel `addr1` concurrent with domestic home activity. Spot-checked on `CC-0002` (Card `C06403-K2`).
  - `detect_account_takeover`: Analyzes mixed-channel shifts, new hardware access, and credential mismatches. Spot-checked on `CC-0008`.
  - Negative control on cleared case `CC-0003` confirmed zero false positive card-testing alarms.
- **Graph Structural Algorithms**:
  - `find_shared_device_rings`: Multi-hop neighborhood expansion (`Card -> Txn -> Device -> Txn -> Card`) detecting hardware syndicates. Successfully uncovered 2,517 multi-customer shared hardware profiles.
  - `find_transaction_velocity_anomalies`: Computes sliding window burst ratios against 30-day baseline rates.
  - `find_account_hopping_velocity`: Measures cross-card velocity surges under single customer profiles.
  - `detect_fraud_communities`: Aggregates device-to-card clusters for ring discovery.
- **Hybrid Similar Prior Case Engine**:
  - Authored `graph/queries/similar_prior_cases.gsql` and `graph/similar_cases_engine.py`.
  - Computes hybrid fusion score: $0.5 \times \text{GraphStructural} + 0.5 \times \text{VectorSemantic}$.
  - Filters strictly for `namespace == "case_memory"` and `is_benchmark == FALSE`.
  - Retrieval verified: Card testing query returns known testing precedents (`CC-0370`, `CC-4225`) with verified ground truth notes.
- **Gate Status**:
  - Automated test harness `graph/test_queries.py` executed with 100% pass rate.
  - Full report saved to `docs/query-test-report.md`.
