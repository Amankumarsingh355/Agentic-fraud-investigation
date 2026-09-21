# Hackathon Progress: TigerGraph Agentic Fraud Investigation (HHGOA_IEEE)

## Phase Status Summary

| Phase | Title | Status | Gate Criteria / Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Setup** | **COMPLETED** | Repo scaffolded, `tigergraph-mcp` cloned & installed, framework/LLM choices documented in `docs/decisions.md`. |
| **Phase 1** | **Data Understanding & Graph Schema** | **COMPLETED** | README synthesized in `docs/dataset-notes.md`, all data files profiled in `docs/data-profile.md`, vector vs. graph partitioned in `docs/vector-vs-graph.md`, schema & loading jobs authored in `graph/schema.gsql` and `graph/loading_jobs.gsql`. |
| **Phase 2** | **Data Ingestion & Vector Store** | **COMPLETED** | GSQL loading jobs written, 5,587 documents embedded and indexed into `data/vector_store/`, 20 benchmark cases isolated in namespace `eval_benchmark`, 0 failed rows, 5/5 spot checks passed in `docs/ingestion-report.md`. |
| **Phase 3** | **Graph Algorithms & Pattern Library** | **COMPLETED** | Parameterized GSQL pattern queries implemented for all 5 typologies (`card_testing`, `cnp`, `cnp_new_device`, `out_of_region`, `ato`), ring detection algorithms written, hybrid similar prior cases engine built, spot checks passed in `docs/query-test-report.md`. |
| **Phase 4** | **GraphRAG Layer & MCP Tools** | **COMPLETED** | Multi-hop subgraph extractor, policy vector retrieval, structured LLM-ready markdown dossiers synthesized, MCP server exposing 6 tools, gate tested on 3 sample transactions in `docs/graphrag-test-report.md`. |
| **Phase 5** | **Agent Core & Policy/Permission Engine** | Planned | Stateful investigation loop (`Trigger -> Investigate -> Gather Evidence -> Assess Uncertainty -> Gather More Evidence -> Recommend Actions -> Explain Decision -> Update Case Memory`), permission tiers (`auto`, `L1`, `L2`), non-destructive action stub execution. |
| **Phase 6** | **Decision Engine & Next Best Action Evolution** | Planned | Two-stage action progression (`initial` vs `final`), `what_changed`, and FinCEN SAR 6-question narrative generator. |
| **Phase 7** | **Case Memory & Graph Persistence** | Planned | Writing new cases back to graph memory with benchmark isolation. |
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 4 Detail Log: GraphRAG Layer & MCP Tools

- **Subgraph Extraction Engine (`graph/subgraph_extractor.py`)**:
  - Implemented multi-hop graph retrieval: Cardholder profile $\rightarrow$ Card lineage $\rightarrow$ 72-hour sliding transaction timeline $\rightarrow$ Device / Hardware fingerprint $\rightarrow$ Billing vs. Home region mapping $\rightarrow$ Shared device syndicate rings.
  - Automatically evaluates indicator flags for the 5 documented typologies (card testing, CNP burst, CNP new device, out-of-region in-person, account takeover).
- **Structured Evidence Dossier Synthesizer (`graph/graphrag_synthesizer.py`)**:
  - Eliminates raw JSON dumps by synthesizing a 7-section LLM-ready markdown investigative dossier:
    1. Target Transaction & Cardholder Baseline (tenure, historical volume, baseline region)
    2. Graph Traversal & Hardware Footprint (device signature, proxy status, syndicate ring alert)
    3. Recent Transaction Velocity (72-hour timeline with timestamps, amounts, channels, deltas)
    4. Automated Graph Pattern Signals (testing indicators, CNP flags, ATO indicators)
    5. Governing Bank Policy Rules (semantically matched rules with relevance scores)
    6. Historical Case Memory Precedents (ground-truth closed cases with outcomes & notes)
    7. Evidence Gaps & Investigative Guidance (ambiguity analysis, Rule R1 verification protocols)
- **Model Context Protocol (MCP) Server (`graph/mcp_server.py`)**:
  - Built with official `mcp.server.mcpserver.MCPServer` exposing 6 core investigative tools:
    1. `get_transaction_subgraph`
    2. `detect_fraud_patterns`
    3. `check_device_rings`
    4. `retrieve_similar_cases`
    5. `retrieve_policy_guidance`
    6. `synthesize_case_dossier`
  - Registered and tested with MCP tool dispatch and stdio transport.
- **Phase 4 Verification Gate (`graph/test_graphrag.py`)**:
  - Executed test suite across 3 diverse benchmark cases:
    - **Sample 1 (HHG-001 / Txn 3514030)**: Out-of-region physical charge ($77.07 in Region 444 vs Home 204), 8 txns in 72h timeline, Rule R1 verified customer confirmation precedent retrieved.
    - **Sample 2 (HHG-003 / Txn 3530164)**: Customer unauthorized charge dispute ($49.00 in Region 330 vs Home 299), 22 transactions in 72h velocity window, precedent case retrieved.
    - **Sample 3 (HHG-014 / Txn 3478561)**: Analyst syndicate alert, online CNP charge from `SM-G935F` on anonymous proxy, multi-account device ring across 52 customer accounts identified, Rule R6 syndicate protocol activated.
  - All 3 samples produced 100% compliant, evidence-grounded dossiers with all 7 sections verified.
  - Verification report logged to `docs/graphrag-test-report.md`.
