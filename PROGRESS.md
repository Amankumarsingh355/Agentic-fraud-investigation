# Hackathon Progress: TigerGraph Agentic Fraud Investigation (HHGOA_IEEE)

## Phase Status Summary

| Phase | Title | Status | Gate Criteria / Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Setup** | **COMPLETED** | Repo scaffolded, `tigergraph-mcp` cloned & installed, framework/LLM choices documented in `docs/decisions.md`. |
| **Phase 1** | **Data Understanding & Graph Schema** | **COMPLETED** | README synthesized in `docs/dataset-notes.md`, all data files profiled in `docs/data-profile.md`, vector vs. graph partitioned in `docs/vector-vs-graph.md`, schema & loading jobs authored in `graph/schema.gsql` and `graph/loading_jobs.gsql`. |
| **Phase 2** | **Graph Ingestion & Pattern Detection Queries** | Planned | Load transactions, identity & closed cases; implement GSQL pattern detection queries for all 5 typologies + ring detection. |
| **Phase 3** | **Vector Store & Hybrid GraphRAG** | Planned | Vectorize 5,565 closed case notes, fraud policy, and regulatory guidelines for hybrid retrieval. |
| **Phase 4** | **Agent Core & Policy/Permission Engine** | Planned | LangGraph stateful agent with strict approval routing (`auto`, `L1`, `L2`) and mocked action execution. |
| **Phase 5** | **Case Progression & Uncertainty Loop** | Planned | Dynamic evidence loop with calibrated fraud probability and stop conditions. |
| **Phase 6** | **Decision Engine & Next Best Action** | Planned | Two-stage action progression (`initial` vs `final`), `what_changed`, and FinCEN SAR narrative engine. |
| **Phase 7** | **Case Memory & Graph Persistence** | Planned | Writing new cases back to graph memory with benchmark isolation. |
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 1 Detail Log

- **Data Downloaded**: All 4 files successfully obtained from Google Drive and verified in `data/`:
  - `transactions.csv`: 590,742 transactions, 397 columns (675.14 MB).
  - `identity.csv`: 144,432 identity records, 41 columns (26.7 MB).
  - `closed_cases_history.csv`: 5,565 closed cases, 15 columns (2.7 MB).
  - `case_pack.csv`: 20 benchmark test cases (3.5 KB).
- **Profiling Completed**:
  - Full statistical breakdown compiled in `docs/data-profile.md`.
  - Analyzed distribution across channels (74.4% in-person, 25.6% online), networks (Visa 65.2%, MC 32.0%), and risk scores (median 0.12, 99th percentile 0.83).
  - Mapped composite `DeviceProfile` from `DeviceInfo | OS | Browser | Screen` yielding 9,706 distinct hardware signatures.
- **Architectural Division**:
  - Partitioned structural graph topology from dense vector knowledge in `docs/vector-vs-graph.md`.
  - Graph: Entity linkages, 2-hop device sharing rings, and temporal transaction chains (`NEXT`).
  - Vector: 5,565 closed case notes, policy rules R1–R10, and FinCEN/FATF regulatory texts.
- **Graph Schema Design**:
  - Created `graph/schema.gsql` containing vertices (`Customer`, `Account`, `Card`, `Transaction`, `Device`, `Merchant`, `IPAddress`, `EmailDomain`, `BillingRegion`, `Case`, `Evidence`, `Policy`) and edges (`OWNS`, `HAS_ACCOUNT`, `HAS_CARD`, `PERFORMED`, `USED_DEVICE`, `BILLED_IN`, `PURCHASER_EMAIL`, `RECIPIENT_EMAIL`, `PROCESSED_BY`, `USES_IP`, `LINKED_TO`, `NEXT`, `INVOLVES`, `ON_CARD`, `CONNECTED_TO`, `HAS_EVIDENCE`, `GOVERNED_BY`, `SIMILAR_TO`).
  - Created `graph/loading_jobs.gsql` mapping all CSV columns directly to graph elements.
