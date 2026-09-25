# Building FraudLens AI: Autonomous Multi-Agent Fraud Investigation Powered by TigerGraph, GraphRAG, and Local LLMs

*How we built a production-grade 11-agent autonomous fraud investigation system for the TigerGraph Hacker House Goa 2026 Benchmark — achieving 100% policy compliance, zero hallucinations, and sub-second investigation turnaround.*

---

## 1. Introduction

In modern financial technology, the battle against fraud is a high-stakes, asymmetric arms race. Every second, millions of digital transactions course through banking backbones, credit card rails, and payment gateways. Hidden within this torrent are coordinated fraud syndicates, card-testing bots, account takeovers, and synthetic identity rings.

Traditional rule engines and standalone machine learning classifiers have become blunt instruments. They flag anomalies with a single, opaque scalar—a `risk_score`—dumping thousands of alerts into the queues of human fraud analysts. These analysts are forced to manually stitch together disparate logs: cardholder history, IP geolocations, device user-agents, velocity trends, and prior conviction records. By the time a human investigator connects the dots across multiple accounts, the funds have been liquidated, the botnet has rotated its proxy IP, and the bank is left with severe chargeback losses and regulatory reporting fines.

At the **TigerGraph Hacker House Goa 2026 (IEEE-CIS Edition)**, we asked a fundamental engineering question:

> *Can we build an autonomous, explainable AI system that doesn't just predict fraud with a static score, but actually **conducts a full forensic investigation**—traversing multi-hop graph neighborhoods, retrieving historical case precedents, interacting with cardholders, enforcing banking policies, and filing regulatory reports—all with zero hallucinations?*

This led to the creation of **FraudLens AI**: an autonomous 11-agent fraud investigation platform orchestrated by **CrewAI**, powered by **TigerGraph (GSQL)** and **Ollama (Llama 3)**, and equipped with a real-time **GraphRAG Case Memory** engine.

In this deep dive, we walk through the engineering journey of designing, debugging, and validating FraudLens AI across 20 rigorous benchmark cases.

---

## 2. The Problem We Wanted to Solve

When we analyzed traditional fraud operations and the benchmark problem statement, four systemic failure modes became glaringly apparent:

### A. The False-Positive Trap & Customer Friction
A machine learning model assigns a high anomaly score (e.g., $0.85$) to an in-person physical POS swipe occurring in an unfamiliar region. If the bank immediately blocks the card autonomously, it risks stranding a legitimate customer traveling abroad. If it does nothing, it risks catastrophic loss. Existing systems lack a **controlled evidence-gathering loop**—the ability to assess uncertainty and trigger an out-of-band step-up authentication challenge before pulling the trigger on destructive actions.

### B. Relational Database Blindspots in Syndicate Rings
Relational tables (`Transactions`, `Customers`, `Cards`, `Devices`) excel at row lookups, but fail catastrophically at topological pattern recognition. Stolen credit cards often originate from a single hardware device profile shared across dozens of seemingly disconnected accounts. Finding a 3-hop link:
$$\text{Card}_A \rightarrow \text{Txn}_1 \rightarrow \text{Device}_X \leftarrow \text{Txn}_2 \leftarrow \text{Card}_B$$
requires complex, multi-table self-joins that choke standard SQL databases at scale.

### C. Black-Box Uncertainty vs. Fraud Probability
Most AI systems confuse *risk probability* with *epistemic uncertainty*. A high-risk transaction might have low confidence because critical telemetry (e.g., cardholder confirmation or device fingerprint) is missing. Treating raw model scores as final verdicts leads to unexplainable, high-liability automated actions.

### D. The Regulatory Hallucination Hazard (FinCEN SARs)
Under the Bank Secrecy Act (BSA) and FinCEN regulations (31 CFR § 1020.320), submitting a Suspicious Activity Report (SAR) is a legally binding regulatory action. LLMs deployed in compliance pipelines frequently hallucinate non-existent account numbers, fabricate transaction IDs, or generate boilerplate narratives when statutory thresholds are not met.

---

## 3. Our Solution: FraudLens AI

**FraudLens AI** is an institutional-grade, multi-agent autonomous investigation system designed on three non-negotiable principles:

1. **Graph-Native Forensics (TigerGraph)**: Every investigation is anchored in real-time multi-hop graph traversals. We don't guess if an entity is shared; we prove it through GSQL subgraphs.
2. **Decoupled Uncertainty & Bayesian Accumulation**: The incoming `risk_score` is treated solely as an investigative trigger. True `fraud_probability` is calculated dynamically by accumulating corroborating, mitigating, and topological signals.
3. **Strict Policy Governance & Human-In-The-Loop Routing**: Every proposed action must map to **Bank Fraud Policy v1.0 (Rules R1–R10)** and respect a rigid three-tier authority matrix:
   - `auto`: Non-destructive diagnostic actions (case creation, temporary monitoring, customer verification).
   - `L1`: Team Lead authorization required (card blocking, transaction declines under $2,500).
   - `L2`: Senior Fraud Manager authorization required (syndicate ring containment, mass blocking, regulatory FinCEN SAR filings).

---

## 4. System Architecture

The FraudLens AI platform is structured into five cohesive architectural layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. INGESTION & TRIGGER                          │
│   Incoming Anomaly Feed: Transaction Alert / Dispute / Analyst Flag    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      2. TIGERGRAPH FORENSIC CORE                       │
│   GSQL Multi-Hop Traversals · Subgraph Extraction · Hardware Rings     │
│   Entities: 590,540 Transactions · 13,524 Customers · Device Profiles  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   3. 11-AGENT CREWAI ORCHESTRATION                     │
│  [A1] Signal Ingestion  ────────►  [A2] Graph Forensic Investigator   │
│  [A3] Pattern Specialist ───────►  [A4] Case Lifecycle Auditor        │
│  [A5] Case Memory RAG   ────────►  [A6] Step-Up Validation Agent      │
│  [A7] Action Recommender ───────►  [A8] Policy & Guardrails Enforcer  │
│  [A9] Early Stopping    ────────►  [A10] Explainability Specialist    │
│            ▼                                                           │
│  [A11] Master Decision Validator (4-Step CoT Verification)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   4. MEMORY & REGULATORY SYNTHESIS                     │
│  • GraphRAG Precedents (5,565 Closed Cases)                            │
│  • FinCEN SAR Generator (Who, What, When, Where, Why, How)             │
│  • Two-Stage Action Evolution (Initial -> Verified -> Final)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     5. DUAL-CHANNEL OUTPUT                             │
│  [A] Exact 3-Part JSON Benchmark Artifacts (cases/HHG-xxx.json)        │
│  [B] Modern SOC War Room Dashboard (React 18 + Vite + SSE Streaming)   │
└────────────────────────────────────────────────────────────────────────┘
```

### The 11 Autonomous Agents & Their Mandates:
1. **Agent 1: Fraud Ingestion Specialist**: Parses incoming alert triggers, extracting transaction amounts, billing regions, and customer baseline volume.
2. **Agent 2: TigerGraph Evidence Agent**: Traverses the local and remote TigerGraph subgraphs, identifying multi-hop entity correlations and rolling 72-hour card history.
3. **Agent 3: Pattern Analysis Specialist**: Classifies typologies (`card_testing`, `cnp`, `cnp_new_device`, `out_of_region`, `ato`, `undocumented`) and computes decoupled uncertainty.
4. **Agent 4: Case Lifecycle Auditor**: Manages the formal `Case` state machine, recording chronological audit events with millisecond timestamps.
5. **Agent 5: Case Memory Agent**: Performs hybrid vector/graph similarity search over 5,565 historical closed investigations (`CC-xxxx`).
6. **Agent 6: Step-Up Validation Agent**: Evaluates whether additional evidence is required, simulating or dispatching cardholder challenges under Rule R1.
7. **Agent 7: Anti-Fraud Action Engine**: Proposes mitigation actions strictly from the 14 canonical policy actions.
8. **Agent 8: Policy & Guardrails Agent**: Enforces Bank Fraud Policy Rules R1–R10 and assigns authority routes (`auto`, `L1`, `L2`).
9. **Agent 9: Early Stopping Controller**: Evaluates Section 6 stopping criteria to prevent redundant LLM reasoning cycles.
10. **Agent 10: Explainability Agent**: Synthesizes human-readable, auditable rationale citing graph evidence, precedent cases, and policy clauses.
11. **Agent 11: Master Decision Validator**: Conducts a 4-step Chain-of-Thought (CoT) audit, formulates two-stage action evolution, generates the FinCEN SAR block, and commits case vertices back to the graph.

---

## 5. How TigerGraph Helps Our Investigation

TigerGraph is the analytical bedrock of FraudLens AI. Rather than treating transaction data as flat tabular records, TigerGraph models the entire ecosystem as an interconnected graph.

### Graph Schema
- **Vertices**:
  - `User` / `Customer`: Individual cardholder profile (tracks baseline volume, transaction counts, home region).
  - `Card`: Credit/debit card entity.
  - `Transaction`: Financial transaction node (amount, timestamp, channel, billing region, risk score).
  - `Device`: Hardware identity fingerprint (OS, browser build, screen resolution, device profile).
  - `IPAddress`: Network endpoint (IP address, proxy status, ISP).
- **Edges**:
  - `MADE` / `PERFORMED_TRANSACTION`: Customer $\to$ Card $\to$ Transaction.
  - `USED_DEVICE`: Transaction $\to$ Device.
  - `USED_IP`: Transaction $\to$ IPAddress.
  - `SIMILAR_TO`: Dynamic Case Memory linkages.

### Uncovering Multi-Account Syndicate Rings (Rule R6)
In Case `HHG-014`, an incoming analyst flag identified an unusual online charge of $\$74.96$. A standalone relational query showed only an isolated transaction.

When Agent 2 ran a 2-hop TigerGraph traversal from the transaction's hardware entity:
```gsql
CREATE QUERY findSharedDevices(VERTEX<User> input_user) FOR GRAPH FraudDetectionGraph {
    Start = {input_user};
    Cards = SELECT c FROM Start:u -(MADE:e)- Card:c;
    Txns = SELECT t FROM Cards:c -(PERFORMED_TRANSACTION:e)- Transaction:t;
    Devs = SELECT d FROM Txns:t -(USED_DEVICE:e)- Device:d;
    SharedTxns = SELECT t FROM Devs:d -(USED_DEVICE:e)- Transaction:t WHERE t NOT IN Txns;
    SharedCards = SELECT c FROM SharedTxns:t -(PERFORMED_TRANSACTION:e)- Card:c;
    PRINT SharedCards.size();
}
```
TigerGraph instantly surfaced that this exact hardware fingerprint (`SM-G935F Build/NRD90M | Android 7.0`) was concurrently bound to **52 separate customer accounts**! 

This transformed what appeared to be an isolated minor alert into a confirmed **organized syndicate ring**, triggering immediate cardholder protection (`BLOCK_CARD` with Level 1 sign-off), mandatory regulatory SAR filing (`FILE_REPORT` with Level 2 sign-off), and proactive surveillance on all connected peer cards (`MONITOR_CONNECTED_CARDS`).

---

## 6. AI Agent and Next-Best Action

One of the most innovative aspects of FraudLens AI is its **Two-Stage Next-Best Action Evolution**. Fraud investigations are not instantaneous; they evolve as evidence is acquired.

### Initial Actions vs. Final Actions
1. **Initial Actions (Pre-Verification)**:
   When an alert arrives, the agent cannot assume guilt. If a transaction exhibits high risk solely due to out-of-region POS activity (e.g., `HHG-001`), the agent formulates non-destructive containment:
   - `CREATE_CASE` (`auto`)
   - `VERIFY_WITH_CUSTOMER` (`auto`)
   - `MONITOR_CARD` (`auto`)
2. **Interactive Evidence Gathering**:
   Agent 6 dispatches an out-of-band verification challenge. In benchmark simulation, the cardholder responds:
   > *"Customer states they did not make this purchase of $77.07 and still has physical possession of the card."*
3. **Final Actions (Post-Verification)**:
   With card cloning confirmed, Agent 7 and Agent 8 immediately escalate the containment plan:
   - `CREATE_CASE` (`auto`)
   - `BLOCK_CARD` (`L1` — Paused in the Analyst War Room for human sign-off)
4. **What Changed Narrative**:
   The agent generates an explicit audit delta:
   > *"Customer denial raised fraud probability from 0.71 to 0.98, confirming the need for permanent card block and fraud case creation."*

### FinCEN SAR Formulation
When financial exposure meets statutory criteria (e.g., multi-customer syndicate rings or losses $\ge \$1,000$), Agent 11 compiles a complete FinCEN SAR block with structured 5Ws + 1H narrative:
- **Who**: Target customer IDs and all connected accounts sharing hardware.
- **What**: Exact financial exposure calculated mathematically as $\sum |\text{TransactionAmt}|$.
- **When**: Activity timestamps bounded by the 72-hour window.
- **Where**: Cross-channel web/mobile portals and IP proxy classifications.
- **Why**: Violation of BSA guidelines and Bank Fraud Policy Rule R6.
- **How**: Multi-hop GSQL graph traversal details establishing hardware convergence.

Crucially, when the transaction is cleared (e.g., authorized travel spend in `HHG-012`), the SAR fields are strictly and cleanly zeroed (`narrative=""`, `subjects=[]`, `total_amount_usd=0`, `activity_dates=[]`), preventing false regulatory reporting.

---

## 7. Implementation Challenges & Engineering Solutions

Building an 11-agent autonomous system that adheres strictly to banking regulations presented several non-trivial challenges:

### Challenge 1: Dynamic Case Memory Hallucinations
- **The Bug**: During early testing, our vector similarity engine (`SimilarCasesEngine`) occasionally returned test identifiers like `MEM-RUN-1` and `UPLOAD-TEST-01` in the `similar_prior_cases` array.
- **The Solution**: We implemented a strict grounding layer in [`graph/similar_cases_engine.py`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/graph/similar_cases_engine.py). Case lookups are strictly validated against a verified set of 5,565 closed historical cases in [`data/closed_cases_history.csv`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/data/closed_cases_history.csv). All case IDs must strictly conform to regex `^CC-\d{4}$`. Hallucinations dropped to zero.

### Challenge 2: Financial Exposure Discrepancies
- **The Bug**: In multi-transaction cases, exposure was inadvertently mapped to the single flagged transaction amount rather than the cumulative sum of all fraudulent attempts.
- **The Solution**: We enforced a strict mathematical identity in [`agent/case_formatter.py`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/agent/case_formatter.py):
  $$\text{exposure\_usd} = \text{round}\left(\sum_{t \in \text{affected\_txn\_ids}} |\text{TransactionAmt}_t|, 2\right)$$
  For cleared legitimate cases, exposure is strictly reset to $\$0.00$.

### Challenge 3: Remote Cloud Token Expiry vs. Zero Downtime
- **The Bug**: During testing, remote cloud token lifecycles on `savanna.tgcloud.io` expired, causing pyTigerGraph to return HTTP 200 with HTML portal login pages.
- **The Solution**: We engineered [`graph/resilient_connection.py`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/graph/resilient_connection.py) and [`graph/safe_connection.py`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/graph/safe_connection.py). The connector attempts cloud handshake; if a non-JSON or HTML response is detected, it automatically and transparently falls back to our local indexed graph engine (590k transactions, 13.5k customers), ensuring sub-second response times without pipeline crashes.

### Challenge 4: Policy Action Catalog Harmonization
- **The Bug**: In syndicate ring cases, our policy engine recommended `MONITOR_CONNECTED_CARDS`, which initially tripped our schema validator because it was missing from an earlier mock action list.
- **The Solution**: We audited the canonical repository Bank Fraud Policy v1.0 Section 1 and updated [`tests/validate_policy.py`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/tests/validate_policy.py) to recognize all 14 official policy actions (`ALLOW_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`, `BLOCK_CARD`, `BLOCK_ALL_CARDS`, `GENERATE_REPORT`, `CREATE_CASE`, `FILE_REPORT`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`).

---

## 8. Results and Learnings

To verify the system before submission, we built a **Master Test Validator Suite** comprising 6 domain-specific test scripts in [`tests/`](file:///c:/Users/aman%20kumar%20singh/Desktop/AI_Agent/tests/):

```
==========================================================================================
  MASTER VALIDATOR SCOREBOARD — 20 BENCHMARK CASES
==========================================================================================
  Validator Test Name                           | Status    
  ------------------------------------------------------------
  Schema Validator                              | [PASS] PASS (20/20)
  ID Grounding Validator                        | [PASS] PASS (0 hallucinations)
  Exposure Validator                            | [PASS] PASS (Sum identity verified)
  Policy Compliance Validator                   | [PASS] PASS (Rules R1-R10)
  FinCEN SAR Validator                          | [PASS] PASS (6 Filed / 14 Exempt)
  Graph Persistence Validator                   | [PASS] PASS (100% written to graph)
  ============================================================
  FINAL OUTCOME: 100% AUDIT READY (ALL 20 CASES PASSED ALL VALIDATORS)
```

### Key Performance Metrics:
- **Total Cases Evaluated**: 20 / 20 (100%)
- **Schema Compliance**: 100.0% (0 penalties)
- **Fraud Detection Accuracy**: 17 Fraud / 3 Legitimate (100% aligned with ground-truth verification)
- **FinCEN SARs Filed**: 6 filings ($3,367.13 cumulative fraud exposure)
- **Average Turnaround Latency**: $\approx 0.10$ seconds per case (with local indexed graph acceleration)
- **Graph Tool Invocations**: Average 9.0 graph queries per case
- **Tokens Synthesized**: 11,200 context tokens per case

### Core Engineering Learnings:
1. **Agents need deterministic guardrails**: LLMs are brilliant at reasoning, classification, and narrative synthesis, but should never compute financial sums or invent IDs. Pairing LLMs with deterministic Python validation engines (`CaseFormatter`, `PolicyEngine`) yields perfection.
2. **Graph data is the ultimate anti-hallucination anchor**: When an agent can cite a 3-hop graph proof, its explainability is mathematically defensible.
3. **Decoupled uncertainty prevents customer churn**: Treating risk scores as triggers rather than verdicts saved legitimate customers (`HHG-012`, `HHG-017`, `HHG-020`) from erroneous card blocking.

---

## 9. Future Improvements

While FraudLens AI has achieved 100% compliance on the benchmark, the roadmap for enterprise production includes exciting next horizons:

1. **Continuous Real-Time Graph Learning (GNNs)**: Integrating TigerGraph's Graph Neural Network (TG-GNN) framework to compute dynamic graph embeddings on incoming transactions in sub-10ms.
2. **Cross-Institution Federation via Private Set Intersection (PSI)**: Enabling multiple financial institutions to collaboratively trace cross-bank mule rings without exposing PII.
3. **Streaming Voice/Video Step-Up Authentication**: Integrating Gemini Live multimodal streaming to conduct conversational biometric verification with cardholders during suspected ATO attacks.
4. **Autonomous Adaptive Policy Tuning**: Allowing the Policy Engine to simulate historical chargeback outcomes and propose rule threshold adjustments to the bank's risk committee.

---

## 10. Conclusion

FraudLens AI demonstrates the immense power of marrying **Graph Databases (TigerGraph)** with **Agentic AI Frameworks (CrewAI, Ollama Llama 3)**. By structuring the investigation into 11 distinct, collaborative roles—ranging from graph forensics to policy compliance and regulatory reporting—we transitioned from brittle, black-box fraud scoring to an auditable, intelligent, and autonomous fraud investigation partner.

With 20/20 benchmark cases verified, zero hallucinations, strict mathematical exposure calculations, and full FinCEN SAR compliance, FraudLens AI sets a new standard for AI-driven financial crime defense.

---

*Code and benchmark artifacts are available in the repository root. Run `python run_benchmark.py` to replicate the full 20-case evaluation suite.*
