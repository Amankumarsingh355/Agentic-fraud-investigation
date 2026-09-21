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
| **Scene 2** | 0:45 – 2:00 | Case HHG-001 (Out-of-Region POS) | Reasoning Ticker Replay, Animated Confidence Meter, Before/After Diff |
| **Scene 3** | 2:00 – 3:30 | Case HHG-014 (Syndicate Ring) | 52-Account Ring, Slack Approval Router, FinCEN SAR Tab |
| **Scene 4** | 3:30 – 4:30 | Dual Persona Toggle & Graph Inspector | "See What the Agent Sees" (Raw GSQL & GraphRAG), Node Inspection |
| **Scene 5** | 4:30 – 5:15 | Case Memory Precedent Cluster Map | Searchable similarity cluster map, dynamic memory feedback |
| **Scene 6** | 5:15 – 5:45 | Benchmark Results & Conclusion | 20/20 benchmark evaluation, 100% schema validity, closing remarks |

---

## Detailed Script & Step-by-Step Directions

### Scene 1: Introduction & The Core Problem (0:00 – 0:45)
- **Visual**: Show the TigerGraph FraudOps Cockpit running in full-screen dark mode (`Obsidian Vector` design). Highlight the live `AGENT CORE: ACTIVE` badge and TigerGraph connection status. Point to the **Reasoning Pipeline Ticker** underneath the header.
- **Presenter Dialogue**:
  > *"Welcome! Today we are showcasing our autonomous AI fraud investigation solution built for the TigerGraph Agentic Fraud Investigation challenge.
  > 
  > In enterprise banking, machine learning models generate thousands of risk alerts every day. But a risk score is not a verdict. Above 0.70, most transactions turn out to be legitimate customers traveling or using new devices. Meanwhile, organized fraud rings deliberately keep transaction amounts low to fly under the radar.
  > 
  > We built an end-to-end agentic system that investigates alerts in real time: querying TigerGraph for multi-hop hardware rings, assessing uncertainty with a dynamic confidence meter, gathering customer evidence, enforcing bank policy approval gating via Slack/Ops notifications, and filing regulatory FinCEN SARs—all in under 100 milliseconds."*

---

### Scene 2: Case HHG-001 — Out-of-Region POS & The Replay Engine (0:45 – 2:00)
- **Visual**: In the case dropdown, select `HHG-001` ($77.07, Billing Region 444.0). Click **`▶ REPLAY INVESTIGATION`** on the top Reasoning Ticker bar!
- **UI Elements to Point Out**:
  1. Top Ticker: Watch the 6 steps scrub smoothly: `1. Trigger` ➔ `2. Graph Traversal` ➔ `3. Pattern Match` ➔ `4. Uncertainty` ➔ `5. Actions & Policy` ➔ `6. Case Memory`.
  2. Right Panel (Live Confidence Meter): Watch the needle and gauge arc sweep smoothly from baseline trigger risk (0.61) to final defensible probability (0.98).
  3. Right Panel ("What Changed" Diff View): Point out the side-by-side Before/After card showing risk, actions, and evidence count evolving.
  4. Conversational Copilot Voice: Point to the first-person reasoning summary.
- **Presenter Dialogue**:
  > *"Let's look at Case HHG-001. Rather than just showing a static case card, judges can literally scrub through or replay the agent's thought process live.
  > 
  > Watch the Reasoning Ticker as we hit Replay:
  > In Step 1, the model flagged transaction 3514030 at 0.61.
  > In Step 2, our agent traverses TigerGraph: Cardholder C12382 has a 6-month history in Region 204, but this in-person swipe occurred in Region 444.
  > 
  > Notice the Live Confidence Meter: under Bank Fraud Policy Rule R1—'Verify Before You Block'—an initial probability of 0.61 is not defensible to immediately freeze the card. The agent dispatches a customer verification request.
  > 
  > When the customer confirms they still hold the physical card and never made the purchase, watch the needle jump to 0.98 with HIGH confidence! In the 'What Changed' before-and-after diff, you can see the agent updating its own recommendation from customer verification to an automated case creation and a specialist card block."*

---

### Scene 3: Case HHG-014 — 52-Account Syndicate Ring & Slack Approval Router (2:00 – 3:30)
- **Visual**: Select `HHG-014` in the dropdown. Point out the model risk score: **0.05**.
- **UI Elements to Point Out**:
  1. Syndicate warning banner: `⚠️ SYNDICATE ALERT: Hardware profile linked to 52 customer accounts!`
  2. Center SVG Graph: Notice how the graph dynamically expands with red dashed `SHARED_HW` edges connecting to peer accounts (`C04921`, `C11894`).
  3. Interactive Approval Router Banner (Slack Style): Click **`✓ Sign-off & Dispatch`**! Watch the banner turn emerald green and dispatch to core banking!
  4. Right Panel: Switch to the **FINCEN SAR** tab.
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

### Scene 4: Dual Persona Toggle & Graph as Case File (3:30 – 4:30)
- **Visual**: 
  1. Click the header toggle **`👁️ Agent Working State`**! 
  2. Point out the raw telemetry view: Live GSQL queries executed (`query:hardware_rings`, `query:velocity_timeline`), GraphRAG vector chunks with cosine match scores (0.94), and serialized working memory buffer.
  3. Click **`📊 Analyst Cockpit`** to switch back.
  4. On the center SVG graph, click on the **Device / Terminal node** or **Customer node**. Watch the **Entity Inspector** drawer in the left column update instantly with live attributes!
- **Presenter Dialogue**:
  > *"Judges love transparency. With one click on 'Agent Working State', we can see what the agent sees: the exact GSQL queries executed against TigerGraph, the GraphRAG policy chunks pulled from our vector store with cosine similarity scores, and the raw working memory state.
  > 
  > And the graph isn't just decorative: clicking any entity on the canvas—like this device profile—instantly pulls up its full attributes in our Entity Inspector, proving the graph is actively driving the investigation."*

---

### Scene 5: Precedent Map, False Alarm Clearing & Case Memory (4:30 – 5:15)
- **Visual**: 
  1. Point out the **Case Memory Precedent Map**: show the SVG cluster with orbiting prior cases (`CC-0595`, `CC-2710`) and 94% similarity matches.
  2. Select `HHG-012` to showcase false alarm handling: customer verifies travel $\rightarrow$ needle sweeps down to 0.02 $\rightarrow$ case closes with `CLOSE_NO_FRAUD` without card blocking.
  3. Highlight TigerGraph Vertex persistence: `CASE-3553342` written back to graph memory.
- **Presenter Dialogue**:
  > *"Our system doesn't treat investigations in a vacuum. In the Precedent Map, you can see similar historical cases orbiting the detected fraud pattern, showing how past bank decisions inform the current investigation.
  > 
  > Furthermore, for legitimate transactions like Case HHG-012, customer travel confirmation causes our confidence meter to sweep down from 0.82 to 0.02, clearing the alert without blocking the card or causing customer friction.
  > 
  > Finally, every resolved outcome is committed back to TigerGraph as a Case vertex, closing the loop on continuous agent learning."*

---

### Scene 6: Benchmark Results & Closing (5:15 – 5:45)
- **Visual**: Display the Benchmark Evaluation Report summary (`docs/benchmark-evaluation-report.md`) and the 20 generated case files in `cases/`.
- **Presenter Dialogue**:
  > *"To validate our solution, we evaluated all 20 benchmark cases from the hackathon case pack.
  > 
  > 20 out of 20 cases passed strict schema validation with zero scoring penalties and zero crashes. The agent processed each investigation in an average of 0.08 seconds, uncovering syndicate rings, clearing false alarms, and generating compliant FinCEN SARs.
  > 
  > Thank you for watching, and we look forward to bringing autonomous graph intelligence to fraud operations!"*
