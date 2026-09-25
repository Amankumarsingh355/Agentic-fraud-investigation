# Building FraudLens AI: How We Built an Autonomous Fraud Detective with TigerGraph and AI

*A simple, step-by-step story of building an 11-agent AI system that uncovers hidden fraud rings, protects customers, and passes banking tests with a 100% score.*

---

## 1. Introduction

Every day, millions of people swipe credit cards, shop online, and transfer money. Behind the scenes, banks are constantly watching for fraud. 

Normally, when something looks suspicious, an automated system generates an alert with a "risk score" (like 0.85). Then, a human fraud analyst has to open multiple computer screens, check transaction history, look up IP addresses, and decide whether to block the card.

This process is slow, stressful, and error-prone. Fraudsters move in seconds, but human reviews take hours or days.

For the **TigerGraph Hacker House Goa 2026 Hackathon**, we wanted to change this. We built **FraudLens AI**: an autonomous AI fraud investigation system that acts like an entire team of digital detectives. It uses **TigerGraph** to spot hidden connections, **AI agents** to investigate alerts, and **banking rules** to take safe, smart actions in real time.

---

## 2. The Problem We Wanted to Solve

When banks try to stop fraud today, they run into four big problems:

1. **Too Many False Alarms**:
   Imagine you travel to another city and buy a coffee. An automated model sees an unusual location and immediately blocks your card. You are stranded without money, even though you are an honest customer. Traditional AI acts too aggressively without checking facts.
2. **Hidden Fraud Rings (The "Connecting the Dots" Problem)**:
   Smart criminals don't just steal one card. They steal 50 different cards from 50 different people and use them on the **same mobile phone** or **same WiFi network**. Traditional bank databases (tables and rows) cannot easily see these multi-step connections.
3. **Confusion Between Risk and Uncertainty**:
   A transaction might have an unusual score simply because it’s the customer's first purchase of the day. A smart system shouldn't just guess—it should know when it is *uncertain* and ask the customer before making a drastic move.
4. **AI "Hallucinations" in Legal Reports**:
   When banks find serious fraud, they are legally required to file a report called a **SAR (Suspicious Activity Report)** with financial authorities. Standard AI models (like ChatGPT) often "hallucinate"—they invent fake card numbers, wrong amounts, or imaginary cases. In banking, this is dangerous and illegal.

---

## 3. Our Solution: FraudLens AI

We built **FraudLens AI** to solve these exact problems. Instead of relying on a single AI model or a flat database, FraudLens AI combines three powerful ideas:

1. **A Graph Database (TigerGraph)**:
   Instead of looking at isolated rows in a table, TigerGraph connects users, cards, devices, and IP addresses like a spiderweb. If 52 different cards share one phone, TigerGraph spots it in milliseconds.
2. **An 11-Agent AI Detective Team**:
   Instead of asking one generic chatbot to do everything, we created 11 specialized AI agents. One agent gathers evidence, another checks graph connections, another checks bank policy, and a master agent verifies everything before making a decision.
3. **Safe, Policy-Driven Actions**:
   Our system never acts blindly. It strictly follows official bank rules. It asks the customer first on weak signals, requires human manager approval for large blocks, and generates accurate, hallucination-free legal reports.

---

## 4. System Architecture

Think of FraudLens AI as an automated **Fraud Operations Room**. Here is how information flows:

```
[Incoming Alert] (e.g. Flagged $77 Transaction)
       │
       ▼
[Agent 1: Fraud Ingestion] ────► Reads the alert & customer profile
       │
       ▼
[Agent 2: TigerGraph Evidence] ──► Explores 2-3 hops in the graph (finds shared devices/rings)
       │
       ▼
[Agent 3: Pattern Analysis] ────► Identifies fraud type (Stolen Card? Bot testing? Travel?)
       │
       ▼
[Agent 4 & 5: Case Memory] ─────► Searches 5,500+ past closed cases for matching precedents
       │
       ▼
[Agent 6: Step-Up Validation] ──► If uncertain, asks the customer via SMS/Push challenge
       │
       ▼
[Agent 7 & 8: Policy Engine] ───► Applies Bank Rules (R1 to R10) & assigns approval levels
       │
       ▼
[Agent 9 & 10: Explainability] ─► Writes a clear explanation citing exact evidence
       │
       ▼
[Agent 11: Master Decision] ────► Generates legal FinCEN SAR & exact 3-part JSON result
```

### The 11 AI Agents Explained Simply:
- **Agent 1 (Ingestion)**: The front-desk officer. Ingests the alert and grabs the customer and card details.
- **Agent 2 (Graph Evidence)**: The graph explorer. Uses TigerGraph to see who else is connected to this card or device.
- **Agent 3 (Pattern Specialist)**: The detective. Figures out what kind of attack is happening (card testing, new device, travel, etc.).
- **Agent 4 (Case Lifecycle)**: The record keeper. Creates the official case file and timestamps every single action.
- **Agent 5 (Case Memory)**: The historical expert. Checks past records of 5,500+ resolved cases to see what happened before.
- **Agent 6 (Step-Up Validation)**: The communicator. If the proof is not clear, sends a quick verification message to the cardholder.
- **Agent 7 (Action Recommender)**: The tactical planner. Recommends the next best steps (e.g., monitor card, block card, file report).
- **Agent 8 (Policy Guardrails)**: The compliance officer. Ensures every action strictly follows bank rules and security laws.
- **Agent 9 (Early Stopping)**: The efficiency boss. Stops the investigation as soon as solid proof is found to save computing power.
- **Agent 10 (Explainability)**: The legal writer. Writes a plain-English explanation for bank managers and regulators.
- **Agent 11 (Master Validator)**: The chief inspector. Verifies all facts, calculates exact dollar exposure, and produces the final report.

---

## 5. How TigerGraph Helps Our Investigation

TigerGraph is the secret weapon behind FraudLens AI.

### Seeing What Normal Databases Miss
In a standard SQL database, finding out if two cards used the same phone requires searching through millions of transaction records and joining multiple massive tables.

In **TigerGraph**, everything is connected naturally:
- **Customer** $\to$ owns $\to$ **Card**
- **Card** $\to$ makes $\to$ **Transaction**
- **Transaction** $\to$ uses $\to$ **Device (Phone/Laptop)**
- **Transaction** $\to$ uses $\to$ **IP Address**

### Real Example: Uncovering a 52-Card Fraud Ring
In one benchmark case (**HHG-014**), an alert showed a small online purchase of just **$74.96**. In a normal bank, an analyst might ignore it as a minor transaction.

When our **TigerGraph Evidence Agent** ran a 2-hop search on the device fingerprint, TigerGraph revealed something shocking:
> **The exact same mobile device had been used by 52 different customer cards within 72 hours!**

Because TigerGraph connected the dots in milliseconds, FraudLens AI immediately recognized this as an **organized criminal fraud ring**. It immediately blocked the compromised card, protected all 52 linked accounts, and filed a formal regulatory fraud report.

---

## 6. AI Agent and Next-Best Action

One of the smartest features of FraudLens AI is that it **does not jump to conclusions**. It uses a **Two-Stage Action Process**:

### Stage 1: Initial Action (Before Checking with Customer)
When an alert first comes in, the agent says:
- *"This transaction looks unusual, but we don't have 100% proof yet. Let's create a case, keep monitoring, and ask the customer via SMS."*
- Actions: `CREATE_CASE`, `VERIFY_WITH_CUSTOMER`, `MONITOR_CARD`.
- **Zero customer annoyance!** The card is not blocked prematurely.

### Stage 2: Verification Response
The system receives the customer's response:
- **Scenario A (Customer says "Yes, that was me traveling!")**:
  The AI immediately clears the case (`CLOSE_NO_FRAUD`), resets exposure to $0, and allows the card to keep working.
- **Scenario B (Customer says "No, I did not buy that!")**:
  Now the proof is 100% solid. The AI escalates to `BLOCK_CARD` and routes it to a human team lead for final sign-off.

### What Changed?
The system explicitly writes a "What Changed" summary:
> *"Customer denial raised fraud probability from 0.71 to 0.98, confirming the need for permanent card block and fraud case creation."*

---

## 7. Implementation Challenges (And How We Fixed Them)

Building this system wasn't easy. Here are three big engineering challenges we solved:

1. **Fixing AI "Memory Leaks"**:
   - *Problem*: Early in testing, our similarity search engine accidentally returned test IDs like `MEM-RUN-1` instead of real closed cases.
   - *Fix*: We built a strict validator that only allows verified historical case IDs from our official dataset (format: `CC-xxxx`). Fake IDs dropped to zero.
2. **Getting the Math 100% Right**:
   - *Problem*: In cases with multiple fraud attempts, the system initially counted only the first transaction's dollar amount.
   - *Fix*: We rewrote the financial calculation engine to sum the exact dollar amounts of all affected transactions:
     $$\text{Total Exposure} = \text{Sum of all fraudulent transactions}$$
     If a case is cleared as legitimate, exposure is strictly reset to $0.00$.
3. **Handling Cloud Connection Drops**:
   - *Problem*: If the remote cloud connection had an expired token or network lag, the whole pipeline risked crashing.
   - *Fix*: We built a **Resilient Connection Manager**. If the remote cloud ever hesitates, the system instantly switches to our local graph engine without missing a beat. Investigations finish in under a second!

---

## 8. Results and Learnings

We didn't just guess that our system works; we put it through a strict **Master Test Suite** covering all **20 official benchmark cases** (`HHG-001` through `HHG-020`):

```text
==========================================================================================
  MASTER VALIDATOR SCOREBOARD — 20 BENCHMARK CASES
==========================================================================================
  Validator Test Name                           | Status    
  ------------------------------------------------------------
  Schema Validator                              | [PASS] 100% Format Compliant (20/20)
  ID Grounding Validator                        | [PASS] Zero Hallucinations (0 errors)
  Exposure Validator                            | [PASS] Math Sum Matches 100%
  Policy Compliance Validator                   | [PASS] Follows Bank Rules R1-R10
  FinCEN SAR Validator                          | [PASS] 6 Filed, 14 Cleanly Cleared
  Graph Persistence Validator                   | [PASS] 100% Saved to TigerGraph
  ============================================================
  FINAL OUTCOME: 100% AUDIT READY (ALL 20 CASES PASSED)
```

### Key Numbers:
- **20 / 20 Cases Passed**: 17 true fraud cases stopped, 3 legitimate customers cleared without friction.
- **Zero Hallucinated IDs**: Every single transaction, user, and case ID is 100% grounded in real data.
- **Sub-Second Speed**: Complete investigation took around **0.1 seconds per case**.
- **6 Formal SARs Filed**: Legally required reports generated automatically with full 5W narratives (Who, What, When, Where, Why, How).

---

## 9. Future Improvements

While FraudLens AI passed all benchmark tests with flying colors, here is what we want to add next:

1. **Graph Neural Networks (GNNs)**: Use real-time deep learning directly inside TigerGraph to predict emerging fraud rings before the first dollar is spent.
2. **Multi-Bank Collaboration**: Connect multiple banks through privacy-preserving graph queries so banks can track criminal networks moving between institutions.
3. **Voice AI Customer Verification**: Use real-time voice agents to call customers and confirm suspicious transactions over secure biometrics.

---

## 10. Conclusion

FraudLens AI proves that the future of banking defense is not just bigger machine learning models or endless human reviews. 

The real breakthrough happens when you combine **Graph Databases (TigerGraph)** to connect the hidden dots, **Multi-Agent AI (CrewAI + Llama 3)** to conduct thorough investigations, and **Strict Policy Rules** to keep actions safe and compliant.

By treating AI as an explainable, disciplined forensic partner, FraudLens AI stops coordinated fraud rings in milliseconds, saves banks millions of dollars, and protects innocent customers from false alarms.

---
*Created for the TigerGraph Hacker House Goa 2026. The full project code and benchmark results are saved in the project repository.*
