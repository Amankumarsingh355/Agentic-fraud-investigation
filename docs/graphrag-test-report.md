# Phase 4 Verification Report: GraphRAG Retrieval & Dossier Synthesis

**Status**: VERIFIED & PASSING
**Date**: September 21, 2026
**Scope**: Validation of GraphRAG multi-hop retrieval, policy vector grounding, case memory precedent matching, and LLM-ready structured dossier generation across 3 sample cases.

---

## Sample Case HHG-001 (Txn ID: `3514030`)
**Trigger**: `risk_score` — *"Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide."*

### Generated GraphRAG Dossier
```markdown
# FRAUD INVESTIGATION DOSSIER: HHG-001
**Target Transaction**: `3514030` | **Trigger Type**: `risk_score`
**Trigger Detail**: "Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide."

## SECTION 1: TARGET TRANSACTION & CARDHOLDER BASELINE
- **Customer**: `C12382` (Tenure: 2016-07-06 to 2016-12-31, 422 historical txns, $48,783.68 total volume)
- **Primary Card**: `C12382-K1` (Network: `visa`, Type: `debit`)
- **Flagged Spend**: **$77.07 USD** at `2016-12-04 19:55:28`
- **Channel / Product**: `in_person` (ProductCD: `W`)
- **Bank Model Risk Score**: `0.61` (Input signal only, not a verdict)
- **Geographic Billing**: Region `444.0` (Country `87.0` | Established Home Region: `204.0`)

## SECTION 2: GRAPH TRAVERSAL & HARDWARE FOOTPRINT
- **Channel**: Physical in-person point of sale (Product code W). Zero digital identity footprint recorded.
- **Device Linkage**: Device is isolated to this customer profile (0 shared card rings discovered).

## SECTION 3: RECENT TRANSACTION VELOCITY (72-HOUR TIMELINE)
- Recorded 8 transactions on this card within 72 hours:
  * Txn `3510115`: $23.99 (in_person, Product W) at 2016-12-03 15:53:45 (delta: +0s, Risk: 0.04)
  * Txn `3510225`: $35.92 (in_person, Product W) at 2016-12-03 16:32:25 (delta: +2320s, Risk: 0.08)
  * Txn `3510464`: $107.96 (in_person, Product W) at 2016-12-03 17:47:05 (delta: +4480s, Risk: 0.3)
  * Txn `3510612`: $34.52 (in_person, Product W) at 2016-12-03 18:24:53 (delta: +2268s, Risk: 0.06)
  * Txn `3511596`: $59.06 (in_person, Product W) at 2016-12-03 23:03:54 (delta: +16741s, Risk: 0.15)
  * Txn `3512936`: $160.00 (in_person, Product W) at 2016-12-04 14:28:34 (delta: +55480s, Risk: 0.08)
  * Txn `3513814`: $116.97 (in_person, Product W) at 2016-12-04 18:51:28 (delta: +15774s, Risk: 0.09)
  * Txn `3514030`: $77.07 (in_person, Product W) at 2016-12-04 19:55:28 (delta: +3840s, Risk: 0.61) [TARGET ALERT]

## SECTION 4: AUTOMATED GRAPH PATTERN SIGNALS
- **Card Testing Indicator (R5)**: `NEGATIVE` (0 micro-auths under $10, 0 large auths)
- **Card-Not-Present Burst**: `NEGATIVE` (0 online txns in window)
- **CNP via New Device**: `NEGATIVE`
- **Out-of-Region Use**: `FLAGGED` (Current: 444.0 vs Home: 204.0)
- **Account Takeover**: `NEGATIVE`

## SECTION 5: GOVERNING BANK POLICY RULES
- ****Rule R1: Verify Before You Block on a Weak Signal**** (Relevance: 0.2633):
  - **Rule R1: Verify Before You Block on a Weak Signal**
  If an investigation rests on a single signal (such as a model risk score alone) and assessed fraud probability is below 0.70, recommend `VERIF...
- **Policy Section 0** (Relevance: 0.1366):
  # Bank Fraud Policy v1.0 — Governance, Rules & Decision Authority

## Section 0: Foundational Operating Principle
Every transaction carries a `risk_score` between 0.0 and 1.0 from the bank's machine l...

## SECTION 6: HISTORICAL CASE MEMORY PRECEDENTS
- **Case CC-1541** (Outcome: `confirmed_fraud`, Pattern: `out_of_region_use`, Exposure: $77.02, Hybrid Score: 0.5642):
  "Case CC-1541: cardholder C02250 reported unrecognized activity on card C02250-K2. 1 transaction(s) between 2016-08-01 and 2016-08-01 totaling $77.02 were confirmed fraudulent. Card-present use in a billing region the car..."
- **Case CC-2923** (Outcome: `confirmed_fraud`, Pattern: `out_of_region_use`, Exposure: $77.00, Hybrid Score: 0.5619):
  "Case CC-2923: cardholder C00088 reported unrecognized activity on card C00088-K1. 1 transaction(s) between 2016-08-31 and 2016-08-31 totaling $77.00 were confirmed fraudulent. Card-present use in a billing region the car..."

## SECTION 7: EVIDENCE GAPS & INVESTIGATIVE GUIDANCE
- **Ambiguity**: Out-of-region in-person charge observed. Could represent legitimate travel or counterfeit clone.
- **Mandatory Policy Rule R1**: If assessed fraud probability < 0.70 on single indicator, recommend `VERIFY_WITH_CUSTOMER` before any card block.
```

---

## Sample Case HHG-003 (Txn ID: `3530164`)
**Trigger**: `customer_report` — *"Customer C08623 message: 'I never made this $49.00 purchase. Please check my card.' Refers to 3530164."*

### Generated GraphRAG Dossier
```markdown
# FRAUD INVESTIGATION DOSSIER: HHG-003
**Target Transaction**: `3530164` | **Trigger Type**: `customer_report`
**Trigger Detail**: "Customer C08623 message: 'I never made this $49.00 purchase. Please check my card.' Refers to 3530164."

## SECTION 1: TARGET TRANSACTION & CARDHOLDER BASELINE
- **Customer**: `C08623` (Tenure: 2016-07-06 to 2016-12-31, 1140 historical txns, $147,472.87 total volume)
- **Primary Card**: `C08623-K1` (Network: `mastercard`, Type: `credit`)
- **Flagged Spend**: **$49.00 USD** at `2016-12-10 13:01:21`
- **Channel / Product**: `in_person` (ProductCD: `W`)
- **Bank Model Risk Score**: `0.4` (Input signal only, not a verdict)
- **Geographic Billing**: Region `330.0` (Country `87.0` | Established Home Region: `299.0`)

## SECTION 2: GRAPH TRAVERSAL & HARDWARE FOOTPRINT
- **Channel**: Physical in-person point of sale (Product code W). Zero digital identity footprint recorded.
- **Device Linkage**: Device is isolated to this customer profile (0 shared card rings discovered).

## SECTION 3: RECENT TRANSACTION VELOCITY (72-HOUR TIMELINE)
- Recorded 22 transactions on this card within 72 hours:
  * Txn `3521781`: $369.46 (in_person, Product W) at 2016-12-07 13:34:49 (delta: +0s, Risk: 0.02)
  * Txn `3521801`: $226.05 (in_person, Product W) at 2016-12-07 13:42:02 (delta: +433s, Risk: 0.11)
  * Txn `3521954`: $58.95 (in_person, Product W) at 2016-12-07 14:45:41 (delta: +3819s, Risk: 0.09)
  * Txn `3522026`: $59.08 (in_person, Product W) at 2016-12-07 15:08:37 (delta: +1376s, Risk: 0.13)
  * Txn `3522790`: $226.06 (in_person, Product W) at 2016-12-07 19:30:24 (delta: +15707s, Risk: 0.03)
  * Txn `3523274`: $43.02 (in_person, Product W) at 2016-12-07 21:59:06 (delta: +8922s, Risk: 0.16)
  * Txn `3523351`: $213.48 (in_person, Product W) at 2016-12-07 22:24:02 (delta: +1496s, Risk: 0.17)
  * Txn `3523643`: $29.98 (in_person, Product W) at 2016-12-07 23:52:12 (delta: +5290s, Risk: 0.29)
  * Txn `3524444`: $38.53 (in_person, Product W) at 2016-12-08 12:05:49 (delta: +44017s, Risk: 0.17)
  * Txn `3524629`: $117.04 (in_person, Product W) at 2016-12-08 13:55:40 (delta: +6591s, Risk: 0.03)
  * Txn `3524740`: $255.08 (in_person, Product W) at 2016-12-08 14:41:13 (delta: +2733s, Risk: 0.18)
  * Txn `3525595`: $1749.88 (in_person, Product W) at 2016-12-08 19:43:34 (delta: +18141s, Risk: 0.6)
  * Txn `3527130`: $29.06 (in_person, Product W) at 2016-12-09 11:18:05 (delta: +56071s, Risk: 0.06)
  * Txn `3527215`: $59.00 (in_person, Product W) at 2016-12-09 12:36:58 (delta: +4733s, Risk: 0.3)
  * Txn `3527397`: $58.97 (in_person, Product W) at 2016-12-09 14:03:01 (delta: +5163s, Risk: 0.16)
  * Txn `3527532`: $193.04 (in_person, Product W) at 2016-12-09 14:49:46 (delta: +2805s, Risk: 0.11)
  * Txn `3528392`: $117.06 (in_person, Product W) at 2016-12-09 19:39:12 (delta: +17366s, Risk: 0.1)
  * Txn `3528902`: $141.00 (in_person, Product W) at 2016-12-09 22:19:33 (delta: +9621s, Risk: 0.07)
  * Txn `3529041`: $34.09 (in_person, Product W) at 2016-12-09 23:01:44 (delta: +2531s, Risk: 0.55)
  * Txn `3529981`: $108.43 (in_person, Product W) at 2016-12-10 10:50:46 (delta: +42542s, Risk: 0.08)
  * Txn `3530056`: $116.93 (in_person, Product W) at 2016-12-10 12:12:41 (delta: +4915s, Risk: 0.88)
  * Txn `3530164`: $49.00 (in_person, Product W) at 2016-12-10 13:01:21 (delta: +2920s, Risk: 0.4) [TARGET ALERT]

## SECTION 4: AUTOMATED GRAPH PATTERN SIGNALS
- **Card Testing Indicator (R5)**: `NEGATIVE` (0 micro-auths under $10, 0 large auths)
- **Card-Not-Present Burst**: `NEGATIVE` (0 online txns in window)
- **CNP via New Device**: `NEGATIVE`
- **Out-of-Region Use**: `FLAGGED` (Current: 330.0 vs Home: 299.0)
- **Account Takeover**: `NEGATIVE`

## SECTION 5: GOVERNING BANK POLICY RULES
- ****Rule R1: Verify Before You Block on a Weak Signal**** (Relevance: 0.2633):
  - **Rule R1: Verify Before You Block on a Weak Signal**
  If an investigation rests on a single signal (such as a model risk score alone) and assessed fraud probability is below 0.70, recommend `VERIF...
- **Policy Section 0** (Relevance: 0.1366):
  # Bank Fraud Policy v1.0 — Governance, Rules & Decision Authority

## Section 0: Foundational Operating Principle
Every transaction carries a `risk_score` between 0.0 and 1.0 from the bank's machine l...

## SECTION 6: HISTORICAL CASE MEMORY PRECEDENTS
- **Case CC-2817** (Outcome: `confirmed_fraud`, Pattern: `out_of_region_use`, Exposure: $38.96, Hybrid Score: 0.5968):
  "Case CC-2817: cardholder C08623 reported unrecognized activity on card C08623-K2. 1 transaction(s) between 2016-08-30 and 2016-08-30 totaling $38.96 were confirmed fraudulent. Card-present use in a billing region the car..."
- **Case CC-4957** (Outcome: `confirmed_fraud`, Pattern: `out_of_region_use`, Exposure: $48.02, Hybrid Score: 0.5921):
  "Case CC-4957: cardholder C08623 reported unrecognized activity on card C08623-K2. 1 transaction(s) between 2016-10-16 and 2016-10-16 totaling $48.02 were confirmed fraudulent. Card-present use in a billing region the car..."

## SECTION 7: EVIDENCE GAPS & INVESTIGATIVE GUIDANCE
- **Ambiguity**: Out-of-region in-person charge observed. Could represent legitimate travel or counterfeit clone.
- **Mandatory Policy Rule R1**: If assessed fraud probability < 0.70 on single indicator, recommend `VERIFY_WITH_CUSTOMER` before any card block.
```

---

## Sample Case HHG-014 (Txn ID: `3478561`)
**Trigger**: `analyst_request` — *"Analyst request: several cards this month show purchases from the same unusual device profile. Review transaction 3478561 on card C13487-K1 and look for related activity."*

### Generated GraphRAG Dossier
```markdown
# FRAUD INVESTIGATION DOSSIER: HHG-014
**Target Transaction**: `3478561` | **Trigger Type**: `analyst_request`
**Trigger Detail**: "Analyst request: several cards this month show purchases from the same unusual device profile. Review transaction 3478561 on card C13487-K1 and look for related activity."

## SECTION 1: TARGET TRANSACTION & CARDHOLDER BASELINE
- **Customer**: `C13487` (Tenure: 2016-07-04 to 2016-12-27, 85 historical txns, $4,881.62 total volume)
- **Primary Card**: `C13487-K1` (Network: `mastercard`, Type: `debit`)
- **Flagged Spend**: **$74.96 USD** at `2016-11-22 16:11:00`
- **Channel / Product**: `online` (ProductCD: `C`)
- **Bank Model Risk Score**: `0.05` (Input signal only, not a verdict)
- **Geographic Billing**: Region `191.0` (Country `87.0` | Established Home Region: `191.0`)

## SECTION 2: GRAPH TRAVERSAL & HARDWARE FOOTPRINT
- **Channel**: Online authenticated session
- **Device Profile**: `SM-G935F Build/NRD90M | Android 7.0 | chrome 62.0 for android | 1920x1080`
- **Device Status**: `NEW to account (id_15=New)`
- **Proxy Status**: `IP_PROXY:ANONYMOUS`
- **SYNDICATE ALERT (Rule R6)**: Hardware profile is SHARED across 52 distinct accounts: ['C03744', 'C09354', 'C12033', 'C09174', 'C01935']
## SECTION 3: RECENT TRANSACTION VELOCITY (72-HOUR TIMELINE)
- Recorded 2 transactions on this card within 72 hours:
  * Txn `3477218`: $36.04 (in_person, Product W) at 2016-11-21 23:39:05 (delta: +0s, Risk: 0.06)
  * Txn `3478561`: $74.96 (online, Product C) at 2016-11-22 16:11:00 (delta: +59515s, Risk: 0.05) [TARGET ALERT]

## SECTION 4: AUTOMATED GRAPH PATTERN SIGNALS
- **Card Testing Indicator (R5)**: `NEGATIVE` (0 micro-auths under $10, 1 large auths)
- **Card-Not-Present Burst**: `FLAGGED` (1 online txns in window)
- **CNP via New Device**: `FLAGGED`
- **Out-of-Region Use**: `NEGATIVE` (Current: 191.0 vs Home: 191.0)
- **Account Takeover**: `FLAGGED`

## SECTION 5: GOVERNING BANK POLICY RULES
- ****Rule R1: Verify Before You Block on a Weak Signal**** (Relevance: 0.2634):
  - **Rule R1: Verify Before You Block on a Weak Signal**
  If an investigation rests on a single signal (such as a model risk score alone) and assessed fraud probability is below 0.70, recommend `VERIF...
- **Policy Section 0** (Relevance: 0.1367):
  # Bank Fraud Policy v1.0 — Governance, Rules & Decision Authority

## Section 0: Foundational Operating Principle
Every transaction carries a `risk_score` between 0.0 and 1.0 from the bank's machine l...

## SECTION 6: HISTORICAL CASE MEMORY PRECEDENTS
- **Case CC-0595** (Outcome: `confirmed_fraud`, Pattern: `card_not_present_new_device`, Exposure: $74.96, Hybrid Score: 0.5924):
  "Case CC-0595: cardholder C04865 reported unrecognized activity on card C04865-K1. 1 transaction(s) between 2016-07-15 and 2016-07-15 totaling $74.96 were confirmed fraudulent. Online purchases from a device not previousl..."
- **Case CC-2710** (Outcome: `confirmed_fraud`, Pattern: `card_not_present_new_device`, Exposure: $74.96, Hybrid Score: 0.5894):
  "Case CC-2710: cardholder C11871 reported unrecognized activity on card C11871-K1. 1 transaction(s) between 2016-08-28 and 2016-08-28 totaling $74.96 were confirmed fraudulent. Online purchases from a device not previousl..."

## SECTION 7: EVIDENCE GAPS & INVESTIGATIVE GUIDANCE
- **Policy Rule R6**: Shared origin syndicate detected across multiple cardholders. Mandatory `CREATE_CASE`, `FILE_REPORT`, and `MONITOR_CONNECTED_CARDS`.
```

---
