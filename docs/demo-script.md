# TigerGraph Agentic Fraud Investigation: Video Demonstration Script

**Video Title**: Autonomous Fraud Investigation with TigerGraph & GraphRAG  
**Target Duration**: 4 to 6 minutes  
**Presenter Role**: Lead Autonomous Systems Engineer  
**Live UI URL**: `http://localhost:8080` (or `ui/serve.py`)

---

## Video Outline & Timing

| Scene | Timestamp | Screen Focus | Narration Topic |
|---|---|---|---|
| **Scene 1** | 0:00 – 0:45 | Dashboard Header & Architecture | Introduction, challenge of alert fatigue, high-level architecture |
| **Scene 2** | 0:45 – 2:00 | Case HHG-001 (Out-of-Region POS) | Weak signal, uncertainty engine, customer verification, card block |
| **Scene 3** | 2:00 – 3:30 | Case HHG-014 (Syndicate Ring) | Low-score blind spot (0.05), multi-hop ring discovery, FinCEN SAR |
| **Scene 4** | 3:30 – 4:30 | Case HHG-012 (Cleared Legitimate) | False alarm handling, Rule R3, zero customer friction |
| **Scene 5** | 4:30 – 5:15 | Analyst Approval & Case Memory | Human sign-off dispatch, TigerGraph case vertex persistence |
| **Scene 6** | 5:15 – 5:45 | Benchmark Results & Conclusion | 20/20 benchmark evaluation, 100% schema validity, closing remarks |

---

## Detailed Script & Step-by-Step Directions

### Scene 1: Introduction & The Core Problem (0:00 – 0:45)
- **Visual**: Show the TigerGraph FraudOps Cockpit running in full-screen dark mode (`Obsidian Vector` design). Highlight the live `AGENT CORE: ACTIVE` badge and TigerGraph connection status.
- **Presenter Dialogue**:
  > *"Welcome! Today we are showcasing our autonomous AI fraud investigation solution built for the TigerGraph Agentic Fraud Investigation challenge.
  > 
  > In enterprise banking, machine learning models generate thousands of risk alerts every day. But a risk score is not a verdict. Above 0.70, most transactions turn out to be legitimate customers traveling or using new devices. Meanwhile, organized fraud rings deliberately keep transaction amounts low to fly under the radar.
  > 
  > We built an end-to-end agentic system that investigates alerts in real time: querying TigerGraph for multi-hop hardware rings, assessing uncertainty, gathering customer evidence, enforcing bank policy approval gating, and filing regulatory FinCEN SARs—all in under 100 milliseconds."*

---

### Scene 2: Case HHG-001 — Out-of-Region POS & The Investigation Loop (0:45 – 2:00)
- **Visual**: In the case dropdown, select `HHG-001` ($77.07, Billing Region 444.0). Click `⚡ INVESTIGATE`.
- **UI Elements to Point Out**:
  1. Left Panel: Cardholder profile (`C12382`, Home Region 204.0, 422 historical txns) vs. Target Authorization ($77.07 in Region 444.0).
  2. Center Top: 2-Hop Evidence Subgraph showing Customer `C12382` $\rightarrow$ Card `C12382-K1` $\rightarrow$ Flagged Txn `3514030` $\rightarrow$ Region `444.0`.
  3. Center Bottom: 72-Hour Rolling Velocity Timeline showing normal preceding transactions and the flagged POS anomaly.
  4. Right Panel: Uncertainty gauge moving from 0.71 to 0.98.
- **Presenter Dialogue**:
  > *"Let's look at Case HHG-001. A real-time model scored transaction 3514030 at 0.61.
  > 
  > Notice how our agent immediately pulls the 2-hop connected subgraph from TigerGraph. Cardholder C12382 has a 6-month history in Region 204, but this in-person swipe occurred in Region 444. 
  > 
  > Under Bank Fraud Policy Rule R1—'Verify Before You Block'—an initial probability of 0.71 is not enough to immediately freeze the customer's card. The agent dispatches an autonomous SMS verification to the cardholder.
  > 
  > When the simulated customer confirms they still hold the physical card and never made the purchase, the uncertainty engine updates fraud probability to 0.98 with HIGH confidence. The agent immediately formulates final next-best actions: creating a formal fraud case autonomously, and routing a card block to Team Lead (L1) approval."*

---

### Scene 3: Case HHG-014 — Uncovering the 52-Account Syndicate Ring (2:00 – 3:30)
- **Visual**: Select `HHG-014` in the dropdown. Point out the model risk score: **0.05**.
- **UI Elements to Point Out**:
  1. Syndicate warning banner: `⚠️ SYNDICATE ALERT: Hardware profile linked to 52 customer accounts!`
  2. Center SVG Graph: Notice how the graph dynamically expands with red dashed `SHARED_HW` edges connecting to peer accounts (`C04921`, `C11894`).
  3. Right Panel: Switch to the **FINCEN SAR** tab.
- **Presenter Dialogue**:
  > *"Now let's examine a much more dangerous attack: Case HHG-014.
  > 
  > Notice the model score: just 0.05! An isolated tabular model thought this $74.96 purchase was completely harmless. But an analyst flagged an unusual device signature.
  > 
  > Our agent executes our GSQL hardware ring traversal algorithm. Look at the evidence graph: this exact Android device profile has been used across 52 distinct customer accounts within 48 hours! 
  > 
  > This is a textbook multi-card organized syndicate. Under Bank Fraud Policy Rule R6, this immediately triggers a mandatory FinCEN Suspicious Activity Report (SAR).
  > 
  > Let's click the FINCEN SAR tab. Look at this narrative: the agent autonomously generated a complete 6-question regulatory report answering Who, What, When, Where, How, and Why, complete with 8 named customer and card subjects and exact dates. This eliminates hours of manual regulatory compliance paperwork."*

---

### Scene 4: Case HHG-012 — Clearing False Alarms Without Friction (3:30 – 4:30)
- **Visual**: Select `HHG-012` ($30.91, out-of-region POS).
- **UI Elements to Point Out**:
  1. Verdict: `legitimate`, Status: `closed_legitimate`.
  2. Next Best Actions: `CLOSE_NO_FRAUD` (auto), `UNRESTRICT_CARD` (auto).
  3. Evolution Narrative: *"Customer confirmation lowered fraud probability from 0.65 to 0.02, allowing the transaction to clear and closing the case without customer friction."*
  4. SAR Tab: `FILE: FALSE` with strictly zeroed exposure ($0.00).
- **Presenter Dialogue**:
  > *"Now let's see how our agent protects legitimate cardholders: Case HHG-012.
  > 
  > Here, a $30.91 charge occurred out of region. An over-aggressive rule would have blocked the customer's card while they were traveling.
  > 
  > Instead, our agent verified with the customer first. The cardholder confirmed they authorized the charge. Fraud probability plummeted to 0.02.
  > 
  > The agent closed the case as 'closed_legitimate', kept the card unrestricted, and set SAR filing to False with zero exposure. This is how agentic intelligence eliminates false positive friction."*

---

### Scene 5: Interactive Analyst Sign-Off & Case Memory (4:30 – 5:15)
- **Visual**: Return to `HHG-001`. On the `BLOCK_CARD (L1)` card, click the **"✓ Sign-off & Execute"** button.
- **UI Elements to Point Out**:
  1. Action badge updates to `L1 • APPROVED & EXECUTED ✓`.
  2. Switch to the **AUDIT TRAIL** tab: highlight the new green log item: `[APPROVED] BLOCK_CARD: Signed off by Fraud Specialist L2. Dispatched to core banking.`
  3. Point to the TigerGraph Vertex: `CASE-3514030` written to the graph.
- **Presenter Dialogue**:
  > *"Our system is designed for human-in-the-loop governance. Actions exceeding autonomous thresholds require analyst sign-off.
  > 
  > When I click 'Sign-off & Execute', the action is dispatched directly to core banking, and the event is permanently logged in our audit trail.
  > 
  > Furthermore, the entire case is committed back to TigerGraph as a Case vertex. When future alerts arise, our hybrid case memory engine recalls this precedent to inform new investigations."*

---

### Scene 6: Benchmark Results & Closing (5:15 – 5:45)
- **Visual**: Display the Benchmark Evaluation Report summary (`docs/benchmark-evaluation-report.md`) and the 20 generated case files in `cases/`.
- **Presenter Dialogue**:
  > *"To validate our solution, we evaluated all 20 benchmark cases from the hackathon case pack.
  > 
  > 20 out of 20 cases passed strict schema validation with zero scoring penalties and zero crashes. The agent processed each investigation in an average of 0.08 seconds, uncovering syndicate rings, clearing false alarms, and generating compliant FinCEN SARs.
  > 
  > Thank you for watching, and we look forward to bringing autonomous graph intelligence to fraud operations!"*
