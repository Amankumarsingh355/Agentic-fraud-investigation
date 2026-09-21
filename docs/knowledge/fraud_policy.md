# Bank Fraud Policy v1.0 — Governance, Rules & Decision Authority

## Section 0: Foundational Operating Principle
Every transaction carries a `risk_score` between 0.0 and 1.0 from the bank's machine learning model. The model is useful but imperfect: many high scores are legitimate customer activities (false positives), and some sophisticated fraud scores near zero. A risk score is an investigative trigger and input reason to examine the case, never a definitive verdict. Ground truth exists only in historical closed cases and verified customer confirmations.

---

## Section 1: Prescribed Actions Catalog
The agent may recommend one or more actions from the following canonical catalog. Actions must be ordered chronologically by execution sequence:

1. `ALLOW_TRANSACTION`: Authorize the flagged transaction to stand without intervention. Zero customer friction.
2. `DECLINE_TRANSACTION`: Decline the specific flagged authorization only. Card remains active and customer can attempt alternative spend. Low customer impact.
3. `MONITOR_CARD`: Keep the card active but heighten automated monitoring sensitivity for a rolling 72-hour window. Zero customer impact.
4. `MONITOR_CONNECTED_CARDS`: Place peer cards linked via device profile, geographic billing cluster, or merchant velocity ring under heightened surveillance. Zero customer impact.
5. `WARN_CUSTOMER`: Issue an informational advisory to the cardholder (e.g., recurring charge reminder, digital security tip). Zero customer impact.
6. `VERIFY_WITH_CUSTOMER`: Inquire if the cardholder initiated or authorized the transaction via SMS/app push. Card remains active pending cardholder response. Low customer impact.
7. `STEP_UP_AUTH`: Require multi-factor authentication (OTP, biometric app confirmation) before subsequent activity can proceed. Low customer impact.
8. `BLOCK_CARD`: Permanently block the card and initiate card replacement/reissue. High customer impact.
9. `BLOCK_ALL_CARDS`: Block all active debit and credit cards associated with the customer profile. Severe customer impact.
10. `GENERATE_REPORT`: Compile an internal investigation brief for the internal audit record without opening a formal fraud case. Zero customer impact.
11. `CREATE_CASE`: Open a formal internal fraud case, attach gathered evidence, and write the record into the TigerGraph knowledge graph as dynamic Case Memory.
12. `FILE_REPORT`: File a formal Suspicious Activity Report (SAR) with the financial regulator (FinCEN). Zero customer impact.
13. `ESCALATE_TO_ANALYST`: Route the investigation with attached graph subgraphs to a human fraud specialist for manual adjudication.
14. `CLOSE_NO_FRAUD`: Formally close the investigation as cleared/legitimate with zero customer impact.

---

## Section 2: Approval Routing & Authority Matrix
- `auto`: Autonomous agent execution without human intervention.
  - Applicable to: `ALLOW_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`, `GENERATE_REPORT`, `CREATE_CASE`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`.
- `L1` (Team Lead Sign-off):
  - Applicable to: `DECLINE_TRANSACTION`; `BLOCK_CARD` when financial exposure $\le \$2,500$.
- `L2` (Fraud Manager Sign-off):
  - Applicable to: `BLOCK_CARD` when financial exposure $>\$2,500$; `BLOCK_ALL_CARDS` (always); `FILE_REPORT` (always).

The agent recommends actions and assigns the correct approval route. The agent may autonomously execute only `auto` actions; `L1` and `L2` actions are recommended and paused for human authorization.

---

## Section 3: Operational Policy Rules (R1 - R10)

- **Rule R1: Verify Before You Block on a Weak Signal**
  If an investigation rests on a single signal (such as a model risk score alone) and assessed fraud probability is below 0.70, recommend `VERIFY_WITH_CUSTOMER` or `STEP_UP_AUTH` prior to any card block. Blocking a legitimate customer on uncorroborated evidence is a severe policy breach.

- **Rule R2: Customer Denies the Transaction**
  When a cardholder denies authorizing the transaction, recommend `BLOCK_CARD` and `CREATE_CASE`. Recommend `FILE_REPORT` if total exposure exceeds \$1,000 or if the investigation connects to a shared device profile or multi-card fraud ring.

- **Rule R3: Customer Confirms the Transaction**
  When a cardholder confirms authorizing the transaction, recommend `CLOSE_NO_FRAUD`. Explicitly record cardholder confirmation in the case summary.

- **Rule R4: Unresponsive Cardholder (No Reply in 24 Hours)**
  If no response is received from the customer within 24 hours of verification request, recommend `MONITOR_CARD` and `DECLINE_TRANSACTION` for any pending authorizations. If financial exposure exceeds \$500, recommend `ESCALATE_TO_ANALYST`.

- **Rule R5: Card Testing Sequence**
  Three or more small online authorizations (typically under \$5.00) on a card within one hour, followed by a larger transaction: recommend `DECLINE_TRANSACTION` and `STEP_UP_AUTH`. If a subsequent purchase exceeding \$100.00 has already cleared, recommend `BLOCK_CARD`.

- **Rule R6: Shared Origin & Syndicate Detection**
  When multiple cards exhibit unauthorized activity originating from the same device profile, identical billing region cluster, or common recipient email domain within a tight time window: identify the shared entity, recommend `CREATE_CASE` and `FILE_REPORT`, and recommend `MONITOR_CONNECTED_CARDS` for every card linked to that shared entity.

- **Rule R7: Disputed But Established Recurring Activity**
  When a cardholder disputes a charge that matches their historical recurring transaction pattern (same merchant, identical amount, consistent monthly cadence): recommend `CREATE_CASE`, `VERIFY_WITH_CUSTOMER`, and `WARN_CUSTOMER`. Do not block the card.

- **Rule R8: Escalation Under Ambiguity and High Exposure**
  If the assessed verdict is `uncertain` and total exposure exceeds \$500, or if gathered evidence exhibits irreconcilable contradictions: recommend `ESCALATE_TO_ANALYST`.

- **Rule R9: Undocumented Coordinated Patterns**
  When observed activity deviates from known typologies but graph evidence indicates coordinated, repeated exploitation across cardholders: recommend `CREATE_CASE`, `FILE_REPORT`, and `ESCALATE_TO_ANALYST`. Provide a distinct, detailed description of the novel pattern in `pattern_description`. Do not force into a known pattern.

- **Rule R10: Restraint on Total Account Blocking**
  Never recommend `BLOCK_ALL_CARDS` unless at least two distinct cards belonging to the customer show confirmed fraudulent activity or customer digital banking credentials are confirmed compromised.

---

## Section 4: Distinction Between Internal Case and Regulatory SAR
- **Internal Case (`CREATE_CASE`)**:
  Required whenever fraud probability reaches 0.30, whenever customer validation is requested, or when a customer disputes a transaction. Persisted into TigerGraph graph memory for future similarity retrieval.
- **Suspicious Activity Report (`FILE_REPORT`)**:
  Regulatory external filing under BSA/FinCEN regulations. Required ONLY when fraud is confirmed/strongly suspected AND:
  1. Financial exposure exceeds \$1,000, OR
  2. Activity links to a shared device profile, shared region syndicate, or another cardholder's fraud, OR
  3. Pattern represents coordinated or undocumented abuse (Rule R9).
