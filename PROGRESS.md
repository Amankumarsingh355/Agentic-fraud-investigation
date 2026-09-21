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
| **Phase 7** | **Decision Engine & Next Best Action Evolution** | Planned | Two-stage action progression (`initial` vs `final`), `what_changed`, and FinCEN SAR 6-question narrative generator. |
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 6 Detail Log: Case Memory & Dynamic Knowledge Feedback

- **Dynamic Case Memory Manager (`graph/case_memory.py`)**:
  - Implemented dynamic graph persistence for resolved cases:
    - **Vertices**: `Case` (status, outcome, pattern, exposure, is_benchmark, narrative) and `Evidence` entities.
    - **Edges**: `PART_OF_CASE` (from Transaction), `INVESTIGATED_CARD` (to Card), `INVESTIGATED_CUSTOMER` (to Customer), `ATTACHED_EVIDENCE` (to Evidence), `APPLIED_POLICY` (to PolicyRule).
    - Persisted into `data/dynamic_case_memory.json` maintaining strict benchmark isolation (`eval_benchmark` excluded).
- **Hybrid Case Memory Retrieval Engine (`graph/similar_cases_engine.py`)**:
  - Upgraded to search across both 5,565 static historical cases and newly resolved dynamic cases.
  - Computes blended score: $0.5 \times \text{VectorSemantic} + 0.5 \times \text{GraphStructural}$, matching on pattern, customer, exposure proximity, and dynamic recency boost.
- **Pattern Library Dynamic Feedback Registry (`graph/pattern_registry.py`)**:
  - Automatically feeds confirmed fraudulent entities (hardware profiles, proxy IPs, novel patterns) back into the pattern library stored in `data/pattern_registry.json`.
  - Informs subsequent investigations when identical devices or entities reappear across cardholder accounts.
- **Phase 6 Verification Gate (`agent/test_memory_gate.py`)**:
  - Tested running the same type of case twice:
    - **Run 1 (`MEM-RUN-1` / Txn `3000332`)**: Out-of-region in-person spend ($117.05). Customer denied charge; case resolved as confirmed fraud and persisted to dynamic graph memory.
    - **Run 2 (`MEM-RUN-2` / Txn `3000906`)**: Subsequent out-of-region in-person spend ($226.01).
    - **Memory Recall Verification**:
      - `MEM-RUN-1` was dynamically retrieved as the **#1 Top Precedent** (Score `0.55`), outscoring all 5,565 historical static cases!
      - Added to Case 2 evidence list under `[DYNAMIC MEMORY] Precedent Case MEM-RUN-1`.
      - Explicitly cited in Case 2 decision explanation under `Case Memory Precedents Informing Decision`.
  - Detailed report saved to `docs/phase6-memory-report.md`.
