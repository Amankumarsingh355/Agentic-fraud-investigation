# Social Media Announcement Posts: TigerGraph Agentic Fraud Investigation

## 1. Twitter / X Thread (5 Tweets)

### Tweet 1 (Hook & Announcement)
Thrilled to unveil our submission for the @TigerGraph × Hacker House Goa Agentic Fraud Investigation hackathon! 🐅⚡

We built an autonomous AI fraud investigation system combining GraphRAG, 8-stage stateful agent loops, and FinCEN SAR regulatory compliance.

Here's how we solved alert fatigue and multi-card syndicates 🧵👇
#AI #GraphRAG #CyberSecurity #FinTech #TigerGraph

---

### Tweet 2 (The Graph Advantage)
🚨 The Core Challenge: A high risk score is an alert, NOT a verdict.
Above 0.70, most transactions are legitimate customers traveling.
Meanwhile, organized syndicates keep charges small ($20–$80) to score near zero.

Enter TigerGraph: 2-hop GSQL queries instantly uncover hidden device rings across 50+ accounts in milliseconds! 🕸️

---

### Tweet 3 (Explainable Uncertainty & Policy Gating)
No black boxes allowed in banking.
Our Uncertainty Engine implements traceable Bayesian scoring:
Confidence = Prior + Corroborating Signals - Mitigating Factors.

Under Policy Rule R1 ("Verify Before You Block"), the agent asks for customer validation before freezing cards. Zero false alarm friction! 🛡️

---

### Tweet 4 (Regulatory FinCEN SAR Generation)
Writing Suspicious Activity Reports (SARs) takes human analysts 30–45 mins per case.

Our agent automatically writes legally compliant 6-question FinCEN narratives answering Who, What, When, Where, How, and Why—with named subjects and exact dollar amounts. ⚖️

---

### Tweet 5 (Benchmark Results & GitHub Repo)
📊 Benchmark Evaluation across all 20 exam cases:
✅ 20/20 cases passed strict schema validation (0 penalties)
✅ 0 crashes
✅ Uncovered 52-account syndicate ring on a 0.05 score
✅ Average turnaround: 0.17 seconds per case

Check out the interactive cockpit and open-source repo! 🚀
#TigerGraph #AgenticAI #FraudInvestigation #OpenSource

---

## 2. LinkedIn Post

**🚀 Announcing: Autonomous Fraud Investigation with TigerGraph & GraphRAG**

In retail banking, fraud detection models generate thousands of risk alerts every day. But human analysts face a double-edged sword:
1. **High false-positive friction**: Most flagged high-risk transactions turn out to be legitimate cardholders traveling or using new devices.
2. **Hidden syndicates**: Sophisticated fraud rings intentionally execute low-dollar transactions ($20–$80) that score near zero on tabular ML models.

For the **TigerGraph × Hacker House Goa Agentic Fraud Investigation Hackathon**, we built an end-to-end autonomous AI fraud operations platform that transforms alert triage into real-time decision intelligence.

### 🔑 Key Architectural Highlights:
1. **TigerGraph GSQL Engine**: Implements parameterized queries for 5 core fraud typologies (Card Testing, Out-of-Region POS, CNP New Device, Account Takeover, and Shared Hardware Syndicate Rings).
2. **GraphRAG Evidence Synthesis**: Synthesizes 2-hop connected subgraphs, vector policy embeddings, and closed case memories into structured, LLM-ready investigative dossiers via the Model Context Protocol (MCP).
3. **Traceable Uncertainty Engine**: Replaces "black-box" predictions with inspectable Bayesian scoring and explicit evidence gaps.
4. **Policy-Governed Action Routing**: Enforces strict bank policy authorization limits (`auto`, `L1` Team Lead $\le \$2,500$, `L2` Fraud Manager $> \$2,500$ or Syndicate).
5. **FinCEN SAR Regulatory Automation**: Autonomously drafts legally compliant Suspicious Activity Reports answering the statutory 6 questions (Who, What, When, Where, How, Why).
6. **Interactive Analyst Cockpit**: Built with the `Obsidian Vector` design system, featuring live SVG multi-hop graph visualization, 72-hour velocity timelines, and human-in-the-loop action approval.

### 📈 Evaluation Benchmark Results (20 Exam Cases):
- **100% Schema Compliance**: 20/20 cases validated with zero scoring penalties.
- **Zero Crashes**: 100% execution reliability.
- **Syndicate Discovery**: Successfully detected a 52-account syndicate ring on case HHG-014 despite an initial model score of just 0.05.
- **Real-Time Latency**: Average investigation turnaround time of **0.17 seconds** (down from 25–45 minutes for manual human review).

A huge thank you to TigerGraph and Hacker House Goa for organizing this incredible challenge!

#ArtificialIntelligence #GraphDatabase #TigerGraph #GraphRAG #FraudDetection #FinTech #Banking #CyberSecurity #MachineLearning
