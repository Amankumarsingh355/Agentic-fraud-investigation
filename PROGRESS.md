# Hackathon Progress: TigerGraph Agentic Fraud Investigation (HHGOA_IEEE)

## Phase Status Summary

| Phase | Title | Status | Gate Criteria / Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Setup** | **COMPLETED** | Repo scaffolded, `tigergraph-mcp` cloned & installed, framework/LLM choices documented in `docs/decisions.md`. |
| **Phase 1** | **Data Understanding & Graph Schema** | **COMPLETED** | README synthesized in `docs/dataset-notes.md`, all data files profiled in `docs/data-profile.md`, vector vs. graph partitioned in `docs/vector-vs-graph.md`, schema & loading jobs authored in `graph/schema.gsql` and `graph/loading_jobs.gsql`. |
| **Phase 2** | **Data Ingestion & Vector Store** | **COMPLETED** | GSQL loading jobs written, 5,587 documents embedded and indexed into `data/vector_store/`, 20 benchmark cases isolated in namespace `eval_benchmark`, 0 failed rows, 5/5 spot checks passed in `docs/ingestion-report.md`. |
| **Phase 3** | **Graph Algorithms & Pattern Library** | **COMPLETED** | Parameterized GSQL pattern queries implemented for all 5 typologies (`card_testing`, `cnp`, `cnp_new_device`, `out_of_region`, `ato`), ring detection algorithms written, hybrid similar prior cases engine built, spot checks passed in `docs/query-test-report.md`. |
| **Phase 4** | **GraphRAG Layer & MCP Tools** | **COMPLETED** | Multi-hop subgraph extractor, policy vector retrieval, structured LLM-ready markdown dossiers synthesized, MCP server exposing 6 tools, gate tested on 3 sample transactions in `docs/graphrag-test-report.md`. |
| **Phase 5** | **Agent Core & Policy/Permission Engine** | **COMPLETED** | Stateful 8-stage investigation loop, inspectable uncertainty/confidence engine, strict policy gating (`auto`, `L1`, `L2`), realistic action stubs, gate passed across 3 non-benchmark cases in `docs/phase5-agent-report.md`. |
| **Phase 6** | **Decision Engine & Next Best Action Evolution** | Planned | Two-stage action progression (`initial` vs `final`), `what_changed`, and FinCEN SAR 6-question narrative generator. |
| **Phase 7** | **Case Memory & Graph Persistence** | Planned | Writing new cases back to graph memory with benchmark isolation. |
| **Phase 8** | **Benchmark Evaluation (20 Cases)** | Planned | Execute agent across all 20 benchmark cases and output schema-validated `cases/<case_id>.json`. |
| **Phase 9** | **Interactive UI / Dashboard** | Planned | Analyst dashboard with graph visualization, progression timeline, and action approval. |
| **Phase 10** | **Submission Deliverables & Final Polish** | Planned | Technical blog post, demo script/video, social media post, and code audit. |

---

## Phase 5 Detail Log: Agent Core & Policy/Permission Engine

- **Case Object & Lifecycle Model (`agent/case.py`)**:
  - Implemented the unified `Case` data model managing:
    - Status lifecycle (`OPEN` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `GATHER_EVIDENCE` $\rightarrow$ `EVIDENCE_PENDING` $\rightarrow$ `RECOMMENDING_ACTIONS` $\rightarrow$ `EXPLAINING_DECISION` $\rightarrow$ `RESOLVED` / `CLOSED`).
    - Typed evidence catalog (graph subgraphs, 72h timelines, hardware fingerprints, policy citations, case precedents).
    - Findings store with severity rankings and graph proof metadata.
    - Inspectable risk assessment dictionary and structured decision explanation.
    - Immutable audit trail logging every timestamped state transition, analytical finding, and policy dispatch.
- **Inspectable Uncertainty & Confidence Engine (`agent/uncertainty_engine.py`)**:
  - Eliminates black-box decisions by decomposing fraud probability into auditable mathematical components:
    - Base trigger priors (model score, customer dispute, analyst alert).
    - Corroborating graph evidence deltas (out-of-region POS, new device, proxy IP, card testing sequence, multi-card syndicate ring).
    - Mitigating customer signals (customer tenure $>90$ days, established home region match).
    - Explicit evidence gap detection (e.g. uncorroborated single risk score under Rule R1, unverified out-of-region travel).
    - Confidence metric and "sufficient evidence to act" gate preventing premature card blocks.
- **Bank Policy & Approval Authority Engine (`agent/policy_engine.py`)**:
  - Strictly encodes Bank Fraud Policy v1.0, Operational Rules (R1 - R10), and Approval Routing Matrix:
    - `auto`: Executed autonomously (`ALLOW_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`, `GENERATE_REPORT`, `CREATE_CASE`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`).
    - `L1` (Team Lead Sign-off): `DECLINE_TRANSACTION`, `BLOCK_CARD` ($\le \$2,500$).
    - `L2` (Fraud Manager Sign-off): `BLOCK_CARD` ($> \$2,500$), `BLOCK_ALL_CARDS`, `FILE_REPORT`.
- **Action Execution & Policy Gating Layer (`agent/action_executor.py`)**:
  - Autonomous actions execute realistic simulated side-effects (SMS/Push dispatch, MFA session token, ticket queueing, card monitoring level update).
  - High-impact `L1`/`L2` actions are intercepted by the policy gate and held in `PENDING_HUMAN_APPROVAL` with designated roles and approval tokens—guaranteeing the agent never exceeds its authority.
- **Autonomous Investigation Orchestrator (`agent/agent.py`)**:
  - Coordinates all 8 loop stages end-to-end:
    `Trigger -> Investigate -> Gather Evidence -> Assess Uncertainty -> Gather More Evidence -> Take Next Actions -> Explain Decision -> Update Case Memory`.
- **Phase 5 Verification Gate (`agent/test_agent.py`)**:
  - Executed across 3 non-benchmark historical cases from months 1-4:
    - **TEST-01 (Txn 3000332 / Customer C06403)**: Out-of-region in-person spend ($117.05). Controlled verification triggered; customer denied charge. Fraud probability escalated to 0.98. `CREATE_CASE` auto-executed, `BLOCK_CARD` staged for L1 approval. Status: `RESOLVED`.
    - **TEST-02 (Txn 3000196 / Customer C12982)**: Customer dispute on online card testing sequence ($30.12). Low confidence single signal. `MONITOR_CARD` auto-executed. Status: `RESOLVED`.
    - **TEST-03 (Txn 3001018 / Customer C03667)**: High risk score (0.84) on $49.04 spend. Controlled customer confirmation received. Fraud probability collapsed to 0.02. `CLOSE_NO_FRAUD` auto-executed under Rule R3. Status: `CLOSED`.
  - Zero crashes, 100% compliant policy routing, full audit trails logged, and complete case JSON records saved to `cases/`.
  - Detailed report saved to `docs/phase5-agent-report.md`.
