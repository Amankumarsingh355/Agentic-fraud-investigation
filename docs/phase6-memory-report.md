# Phase 6 Verification Report: Case Memory & Dynamic Knowledge Feedback

**Status**: VERIFIED & PASSING
**Date**: September 21, 2026
**Scope**: Validation of dynamic graph persistence, hybrid case memory retrieval, pattern library feedback, and the memory gate test.

---

## Gate Test: Running the Same Type of Case Twice

### Run 1: Initial Case `MEM-RUN-1`
- **Transaction ID**: `3000332` (Customer `C06403`)
- **Trigger**: Real-time model risk score (0.73) on out-of-region POS spend
- **Outcome**: Confirmed Fraud (Fraud Prob: `0.98`)
- **Actions**: `CREATE_CASE` (auto), `BLOCK_CARD` (staged L1)
- **Persistence**: Written to `data/dynamic_case_memory.json` with graph edges (`PART_OF_CASE`, `INVESTIGATED_CARD`, `INVESTIGATED_CUSTOMER`, `ATTACHED_EVIDENCE`).

### Run 2: Subsequent Similar Case `MEM-RUN-2`
- **Transaction ID**: `3000906` (Customer `C13440`)
- **Trigger**: Real-time model scored transaction at 0.75 in novel billing region
- **Pattern Match**: Identical typology (`out_of_region_use`)
- **Memory Retrieval**: **SUCCESSFULLY RETRIEVED `MEM-RUN-1` as Top Precedent!**
- **Hybrid Relevance Score**: `0.55`
- **Evidence Source**: `TigerGraph Dynamic Case Memory`

### Precedents Recalled in Case 2 Evidence List
| Case ID | Type | Outcome | Pattern | Hybrid Score | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `[DYNAMIC MEMORY] Precedent Case MEM-RUN-1 (confirmed_fraud, out_of_region_use)` | `Precedent` | `confirmed_fraud` | `out_of_region_use` | `0.55` | `TigerGraph Dynamic Case Memory` |
| `Precedent Case CC-5101 (confirmed_fraud, out_of_region_use)` | `Precedent` | `confirmed_fraud` | `out_of_region_use` | `0.5177` | `TigerGraph Case Memory (Historical)` |
| `Precedent Case CC-1617 (confirmed_fraud, account_takeover)` | `Precedent` | `confirmed_fraud` | `out_of_region_use` | `0.3103` | `TigerGraph Case Memory (Historical)` |

### Decision Explanation from Run 2 (Citing Memory from Run 1)
```markdown
### Investigation Summary for Case MEM-RUN-2
**Transaction**: `3000906` | **Amount**: `$226.01` | **Trigger**: `risk_score`

**Assessed Fraud Probability**: `0.43` | **Confidence**: `LOW` (Uncertainty: `0.65`)

#### Traceable Evidence & Reasoning
- **Trigger Prior**: Bank Risk Model Score (0.33) (+0.13): Real-time automated transaction scoring model.
- **Corroborating Signal**: Out-of-Region In-Person POS (+0.20): Physical card used in region 433.0 away from established home 325.0.
- **Mitigating Signal**: Established Customer History (-0.10): Customer has 14932 historical transactions totaling $1,511,269.75.

#### Identified Evidence Gaps
- *Gap*: Missing confirmation whether out-of-region spend is legitimate travel vs cloned card.

#### Case Memory Precedents Informing Decision
- **[DYNAMIC MEMORY] Precedent Case MEM-RUN-1 (confirmed_fraud, out_of_region_use)** (Score: 0.55 | Source: *TigerGraph Dynamic Case Memory*):
  "### Investigation Summary for Case MEM-RUN-1
**Transaction**: `3000332` | **Amount**: `$117.05` | **Trigger**: `risk_score`

**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertaint..."
- **Precedent Case CC-5101 (confirmed_fraud, out_of_region_use)** (Score: 0.5177 | Source: *TigerGraph Case Memory (Historical)*):
  "Case CC-5101: cardholder C04196 reported unrecognized activity on card C04196-K2. 1 transaction(s) between 2016-10-20 and 2016-10-20 totaling $226.01 were confirmed fraudulent. Card-present use in a b..."
- **Precedent Case CC-1617 (confirmed_fraud, account_takeover)** (Score: 0.3103 | Source: *TigerGraph Case Memory (Historical)*):
  "Case CC-1617: cardholder C02902 reported unrecognized activity on card C02902-K2. 1 transaction(s) between 2016-08-02 and 2016-08-02 totaling $226.01 were confirmed fraudulent. Mixed-channel activity ..."

#### Policy Gated Actions & Next Steps
- **CREATE_CASE** (`auto` - EXECUTED): Out-of-region in-person spend recorded. (Governing: *Rule R1 / Section 4*)
- **VERIFY_WITH_CUSTOMER** (`auto` - EXECUTED): Verify out-of-region POS charge in Region 433.0 with cardholder before taking blocking action. (Governing: *Rule R1*)
- **MONITOR_CARD** (`auto` - EXECUTED): Temporarily monitor card while awaiting cardholder verification response. (Governing: *Rule R1*)
```

---

## Dynamic Memory Graph Record
```json
{
  "case_id": "MEM-RUN-1",
  "outcome": "confirmed_fraud",
  "pattern": "out_of_region_use",
  "exposure_usd": 117.05,
  "customer_id": "C06403",
  "card_id": "C06403-K1",
  "flagged_txn_id": 3000332,
  "is_benchmark": false,
  "namespace": "case_memory",
  "narrative": "### Investigation Summary for Case MEM-RUN-1\n**Transaction**: `3000332` | **Amount**: `$117.05` | **Trigger**: `risk_score`\n\n**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertainty: `0.02`)\n\n#### Traceable Evidence & Reasoning\n- **Trigger Prior**: Bank Risk Model Score (0.73) (+0.53): Real-time automated transaction scoring model.\n- **Corroborating Signal**: Out-of-Region In-Person POS (+0.20): Physical card used in region 476.0 away from established home 299.0.\n- **Corroborating Signal**: Explicit Customer Denial of Charge (Rule R2) (+0.90): Cardholder explicitly stated they did not authorize this purchase.\n- **Mitigating Signal**: Established Customer History (-0.10): Customer has 1051 historical transactions totaling $97,241.71.\n\n#### Case Memory Precedents Informing Decision\n- **Precedent Case CC-0002 (confirmed_fraud, out_of_region_use)** (Score: 0.711 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-0002: cardholder C06403 reported unrecognized activity on card C06403-K2. 1 transaction(s) between 2016-07-02 and 2016-07-02 totaling $117.05 were confirmed fraudulent. Card-present use in a b...\"\n- **Precedent Case CC-3328 (confirmed_fraud, out_of_region_use)** (Score: 0.5475 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-3328: cardholder C01982 reported unrecognized activity on card C01982-K2. 1 transaction(s) between 2016-09-10 and 2016-09-10 totaling $117.05 were confirmed fraudulent. Card-present use in a b...\"\n- **Precedent Case CC-4265 (confirmed_fraud, out_of_region_use)** (Score: 0.5437 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-4265: cardholder C02000 reported unrecognized activity on card C02000-K1. 1 transaction(s) between 2016-10-01 and 2016-10-01 totaling $117.05 were confirmed fraudulent. Card-present use in a b...\"\n\n#### Policy Gated Actions & Next Steps\n- **CREATE_CASE** (`auto` - EXECUTED): Customer explicitly denied transaction. Open formal fraud case. (Governing: *Rule R2*)\n- **BLOCK_CARD** (`L1` - PENDING_HUMAN_APPROVAL): Compromised card replacement required for customer-reported fraud ($117.05 exposure). (Governing: *Rule R2*)",
  "actions_taken": [
    "CREATE_CASE",
    "BLOCK_CARD"
  ],
  "graph_vertices": {
    "Case": {
      "case_id": "MEM-RUN-1",
      "opened_at": "2026-09-21T11:29:04.489718",
      "closed_at": "2026-09-21T11:29:04.541428",
      "status": "RESOLVED",
      "outcome": "confirmed_fraud",
      "pattern": "out_of_region_use",
      "exposure_usd": 117.05,
      "is_benchmark": false,
      "namespace": "case_memory",
      "narrative": "### Investigation Summary for Case MEM-RUN-1\n**Transaction**: `3000332` | **Amount**: `$117.05` | **Trigger**: `risk_score`\n\n**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertainty: `0.02`)\n\n#### Traceable Evidence & Reasoning\n- **Trigger Prior**: Bank Risk Model Score (0.73) (+0.53): Real-time automated transaction scoring model.\n- **Corroborating Signal**: Out-of-Region In-Person POS (+0.20): Physical card used in region 476.0 away from established home 299.0.\n- **Corroborating Signal**: Explicit Customer Denial of Charge (Rule R2) (+0.90): Cardholder explicitly stated they did not authorize this purchase.\n- **Mitigating Signal**: Established Customer History (-0.10): Customer has 1051 historical transactions totaling $97,241.71.\n\n#### Case Memory Precedents Informing Decision\n- **Precedent Case CC-0002 (confirmed_fraud, out_of_region_use)** (Score: 0.711 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-0002: cardholder C06403 reported unrecognized activity on card C06403-K2. 1 transaction(s) between 2016-07-02 and 2016-07-02 totaling $117.05 were confirmed fraudulent. Card-present use in a b...\"\n- **Precedent Case CC-3328 (confirmed_fraud, out_of_region_use)** (Score: 0.5475 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-3328: cardholder C01982 reported unrecognized activity on card C01982-K2. 1 transaction(s) between 2016-09-10 and 2016-09-10 totaling $117.05 were confirmed fraudulent. Card-present use in a b...\"\n- **Precedent Case CC-4265 (confirmed_fraud, out_of_region_use)** (Score: 0.5437 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-4265: cardholder C02000 reported unrecognized activity on card C02000-K1. 1 transaction(s) between 2016-10-01 and 2016-10-01 totaling $117.05 were confirmed fraudulent. Card-present use in a b...\"\n\n#### Policy Gated Actions & Next Steps\n- **CREATE_CASE** (`auto` - EXECUTED): Customer explicitly denied transaction. Open formal fraud case. (Governing: *Rule R2*)\n- **BLOCK_CARD** (`L1` - PENDING_HUMAN_APPROVAL): Compromised card replacement required for customer-reported fraud ($117.05 exposure). (Governing: *Rule R2*)"
    },
    "Evidence": [
      {
        "evidence_id": "MEM-RUN-1-EV-001",
        "evidence_type": "customer_baseline",
        "source": "TigerGraph / Customer",
        "title": "Cardholder Profile for C06403",
        "score": null
      },
      {
        "evidence_id": "MEM-RUN-1-EV-002",
        "evidence_type": "target_transaction",
        "source": "TigerGraph / Transaction",
        "title": "Flagged Transaction 3000332 ($ 117.05)",
        "score": 0.73
      },
      {
        "evidence_id": "MEM-RUN-1-EV-003",
        "evidence_type": "velocity_timeline",
        "source": "TigerGraph / Card History",
        "title": "Rolling 72-Hour Timeline (3 events)",
        "score": null
      },
      {
        "evidence_id": "MEM-RUN-1-EV-004",
        "evidence_type": "pattern_signals",
        "source": "Pattern Engine",
        "title": "Typology Pattern Recognition Checks",
        "score": null
      },
      {
        "evidence_id": "MEM-RUN-1-EV-005",
        "evidence_type": "hardware_rings",
        "source": "Graph Ring Algorithms",
        "title": "Shared Hardware Syndicate Ring Discovery",
        "score": null
      },
      {
        "evidence_id": "MEM-RUN-1-EV-006",
        "evidence_type": "policy_citation",
        "source": "Bank Fraud Policy Store",
        "title": "**Rule R1: Verify Before You Block on a Weak Signal**",
        "score": 0.254
      },
      {
        "evidence_id": "MEM-RUN-1-EV-007",
        "evidence_type": "policy_citation",
        "source": "Bank Fraud Policy Store",
        "title": "Closed Case CC-3328 (confirmed_fraud, out_of_region_use)",
        "score": 0.2031
      },
      {
        "evidence_id": "MEM-RUN-1-EV-008",
        "evidence_type": "case_precedent",
        "source": "TigerGraph Case Memory (Historical)",
        "title": "Precedent Case CC-0002 (confirmed_fraud, out_of_region_use)",
        "score": 0.711
      },
      {
        "evidence_id": "MEM-RUN-1-EV-009",
        "evidence_type": "case_precedent",
        "source": "TigerGraph Case Memory (Historical)",
        "title": "Precedent Case CC-3328 (confirmed_fraud, out_of_region_use)",
        "score": 0.5475
      },
      {
        "evidence_id": "MEM-RUN-1-EV-010",
        "evidence_type": "case_precedent",
        "source": "TigerGraph Case Memory (Historical)",
        "title": "Precedent Case CC-4265 (confirmed_fraud, out_of_region_use)",
        "score": 0.5437
      },
      {
        "evidence_id": "MEM-RUN-1-EV-011",
        "evidence_type": "customer_verification_response",
        "source": "Cardholder SMS/Push Channel",
        "title": "Customer Verification Response: denied_fraud",
        "score": null
      }
    ]
  },
  "graph_edges": {
    "PART_OF_CASE": [
      {
        "from": 3000332,
        "to": "MEM-RUN-1"
      }
    ],
    "INVESTIGATED_CARD": [
      {
        "from": "MEM-RUN-1",
        "to": "C06403-K1"
      }
    ],
    "INVESTIGATED_CUSTOMER": [
      {
        "from": "MEM-RUN-1",
        "to": "C06403"
      }
    ],
    "ATTACHED_EVIDENCE": [
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-001"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-002"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-003"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-004"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-005"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-006"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-007"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-008"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-009"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-010"
      },
      {
        "from": "MEM-RUN-1",
        "to": "MEM-RUN-1-EV-011"
      }
    ],
    "APPLIED_POLICY": [
      {
        "from": "MEM-RUN-1",
        "to": "Rule R2"
      },
      {
        "from": "MEM-RUN-1",
        "to": "Rule R2"
      }
    ]
  },
  "persisted_at": "2026-09-21T11:29:04.541478"
}
```