# Phase 5 Verification Report: Agent Core & Investigation Loop

**Status**: VERIFIED & PASSING
**Date**: September 21, 2026
**Scope**: Validation of autonomous 8-stage investigation loop, inspectable uncertainty/confidence logic, controlled evidence gathering, and policy approval gating (auto vs L1 vs L2) across non-benchmark test cases.

---

## Case Record: TEST-01 (Txn: `3000332`)
- **Scenario**: Out-of-region POS spend with customer denial resulting in staged card block.
- **Trigger**: `risk_score` — *"Real-time model scored transaction 3000332 ($117.05, in billing region 476.0) at 0.73. Review and decide."*
- **Final Case Status**: `RESOLVED`
- **Fraud Probability**: `0.98` | **Confidence**: `HIGH`

### Actions Executed & Staged
| Action | Route | Status | Policy Rule | Justification |
| :--- | :--- | :--- | :--- | :--- |
| `CREATE_CASE` | `auto` | **EXECUTED** | Rule R2 | Customer explicitly denied transaction. Open formal fraud case. |
| `BLOCK_CARD` | `L1` | **PENDING_HUMAN_APPROVAL** | Rule R2 | Compromised card replacement required for customer-reported fraud ($117.05 exposure). |

### Decision Rationale
### Investigation Summary for Case TEST-01
**Transaction**: `3000332` | **Amount**: `$117.05` | **Trigger**: `risk_score`

**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertainty: `0.02`)

#### Traceable Evidence & Reasoning
- **Trigger Prior**: Bank Risk Model Score (0.73) (+0.53): Real-time automated transaction scoring model.
- **Corroborating Signal**: Out-of-Region In-Person POS (+0.20): Physical card used in region 476.0 away from established home 299.0.
- **Corroborating Signal**: Explicit Customer Denial of Charge (Rule R2) (+0.90): Cardholder explicitly stated they did not authorize this purchase.
- **Mitigating Signal**: Established Customer History (-0.10): Customer has 1051 historical transactions totaling $97,241.71.

#### Policy Gated Actions & Next Steps
- **CREATE_CASE** (`auto` - EXECUTED): Customer explicitly denied transaction. Open formal fraud case. (Governing: *Rule R2*)
- **BLOCK_CARD** (`L1` - PENDING_HUMAN_APPROVAL): Compromised card replacement required for customer-reported fraud ($117.05 exposure). (Governing: *Rule R2*)

### Audit Trail Summary
Total audit trail events logged: 25.
```json
[
  {
    "index": 1,
    "timestamp": "2026-09-21T11:21:30.232372",
    "stage": "TRIGGER",
    "event_type": "CASE_OPENED",
    "description": "Case TEST-01 initialized via risk_score for Txn 3000332 (Customer C06403, Card C06403-K1).",
    "actor": "SYSTEM_TRIGGER_HANDLER"
  },
  {
    "index": 2,
    "timestamp": "2026-09-21T11:21:30.232380",
    "stage": "LIFECYCLE",
    "event_type": "STATUS_CHANGED",
    "description": "Status transitioned from OPEN to INVESTIGATING. Initiated graph traversal and entity resolution.",
    "actor": "AGENT_CORE"
  },
  {
    "index": 3,
    "timestamp": "2026-09-21T11:21:30.232391",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-001] (customer_baseline): Cardholder Profile for C06403",
    "actor": "EVIDENCE_COLLECTOR"
  },
  {
    "index": 4,
    "timestamp": "2026-09-21T11:21:30.232399",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-002] (target_transaction): Flagged Transaction 3000332 ($ 117.05)",
    "actor": "EVIDENCE_COLLECTOR"
  },
  {
    "index": 5,
    "timestamp": "2026-09-21T11:21:30.232404",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-003] (velocity_timeline): Rolling 72-Hour Timeline (3 events)",
    "actor": "EVIDENCE_COLLECTOR"
  }
]
... [truncated for display]
```

---

## Case Record: TEST-02 (Txn: `3000196`)
- **Scenario**: Customer dispute on online card testing sequence.
- **Trigger**: `customer_report` — *"Customer C12982 message: 'I see an unrecognized online purchase of $30.12 following small test transactions. Please check my card.' Refers to 3000196."*
- **Final Case Status**: `RESOLVED`
- **Fraud Probability**: `0.55` | **Confidence**: `LOW`

### Actions Executed & Staged
| Action | Route | Status | Policy Rule | Justification |
| :--- | :--- | :--- | :--- | :--- |
| `MONITOR_CARD` | `auto` | **EXECUTED** | Section 1 | Low confidence single signal; keep card active under standard heightened monitoring. |

### Decision Rationale
### Investigation Summary for Case TEST-02
**Transaction**: `3000196` | **Amount**: `$30.12` | **Trigger**: `customer_report`

**Assessed Fraud Probability**: `0.55` | **Confidence**: `LOW` (Uncertainty: `0.60`)

#### Traceable Evidence & Reasoning
- **Trigger Prior**: Direct Customer Dispute/Inquiry (+0.45): Customer explicitly questioned or reported the charge.
- **Mitigating Signal**: Established Customer History (-0.10): Customer has 262 historical transactions totaling $14,699.92.

#### Policy Gated Actions & Next Steps
- **MONITOR_CARD** (`auto` - EXECUTED): Low confidence single signal; keep card active under standard heightened monitoring. (Governing: *Section 1*)

### Audit Trail Summary
Total audit trail events logged: 22.
```json
[
  {
    "index": 1,
    "timestamp": "2026-09-21T11:21:30.332514",
    "stage": "TRIGGER",
    "event_type": "CASE_OPENED",
    "description": "Case TEST-02 initialized via customer_report for Txn 3000196 (Customer C12982, Card C12982-K1).",
    "actor": "SYSTEM_TRIGGER_HANDLER"
  },
  {
    "index": 2,
    "timestamp": "2026-09-21T11:21:30.332521",
    "stage": "LIFECYCLE",
    "event_type": "STATUS_CHANGED",
    "description": "Status transitioned from OPEN to INVESTIGATING. Initiated graph traversal and entity resolution.",
    "actor": "AGENT_CORE"
  },
  {
    "index": 3,
    "timestamp": "2026-09-21T11:21:30.332533",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-001] (customer_baseline): Cardholder Profile for C12982",
    "actor": "EVIDENCE_COLLECTOR"
  },
  {
    "index": 4,
    "timestamp": "2026-09-21T11:21:30.332542",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-002] (target_transaction): Flagged Transaction 3000196 ($ 30.12)",
    "actor": "EVIDENCE_COLLECTOR"
  },
  {
    "index": 5,
    "timestamp": "2026-09-21T11:21:30.332548",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-003] (velocity_timeline): Rolling 72-Hour Timeline (1 events)",
    "actor": "EVIDENCE_COLLECTOR"
  }
]
... [truncated for display]
```

---

## Case Record: TEST-03 (Txn: `3001018`)
- **Scenario**: High risk score with customer confirmation resulting in safe case closure (Rule R3).
- **Trigger**: `risk_score` — *"Real-time model scored transaction 3001018 ($49.04) at 0.84. Review and decide."*
- **Final Case Status**: `CLOSED`
- **Fraud Probability**: `0.02` | **Confidence**: `HIGH`

### Actions Executed & Staged
| Action | Route | Status | Policy Rule | Justification |
| :--- | :--- | :--- | :--- | :--- |
| `CLOSE_NO_FRAUD` | `auto` | **EXECUTED** | Rule R3 | Cardholder verified initiating transaction. Close case without fraud. |

### Decision Rationale
### Investigation Summary for Case TEST-03
**Transaction**: `3001018` | **Amount**: `$49.04` | **Trigger**: `risk_score`

**Assessed Fraud Probability**: `0.02` | **Confidence**: `HIGH` (Uncertainty: `0.02`)

#### Traceable Evidence & Reasoning
- **Trigger Prior**: Bank Risk Model Score (0.84) (+0.64): Real-time automated transaction scoring model.
- **Mitigating Signal**: Home Region In-Person Activity (-0.15): Transaction took place in established home billing region 123.0.
- **Mitigating Signal**: Explicit Customer Confirmation (Rule R3) (-0.90): Cardholder confirmed initiating this transaction.

#### Policy Gated Actions & Next Steps
- **CLOSE_NO_FRAUD** (`auto` - EXECUTED): Cardholder verified initiating transaction. Close case without fraud. (Governing: *Rule R3*)

### Audit Trail Summary
Total audit trail events logged: 23.
```json
[
  {
    "index": 1,
    "timestamp": "2026-09-21T11:21:30.411588",
    "stage": "TRIGGER",
    "event_type": "CASE_OPENED",
    "description": "Case TEST-03 initialized via risk_score for Txn 3001018 (Customer C03667, Card C03667-K1).",
    "actor": "SYSTEM_TRIGGER_HANDLER"
  },
  {
    "index": 2,
    "timestamp": "2026-09-21T11:21:30.411596",
    "stage": "LIFECYCLE",
    "event_type": "STATUS_CHANGED",
    "description": "Status transitioned from OPEN to INVESTIGATING. Initiated graph traversal and entity resolution.",
    "actor": "AGENT_CORE"
  },
  {
    "index": 3,
    "timestamp": "2026-09-21T11:21:30.411607",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-001] (customer_baseline): Cardholder Profile for C03667",
    "actor": "EVIDENCE_COLLECTOR"
  },
  {
    "index": 4,
    "timestamp": "2026-09-21T11:21:30.411618",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-002] (target_transaction): Flagged Transaction 3001018 ($ 49.04)",
    "actor": "EVIDENCE_COLLECTOR"
  },
  {
    "index": 5,
    "timestamp": "2026-09-21T11:21:30.411624",
    "stage": "GATHER_EVIDENCE",
    "event_type": "EVIDENCE_ADDED",
    "description": "Added evidence [EV-003] (velocity_timeline): Rolling 72-Hour Timeline (1 events)",
    "actor": "EVIDENCE_COLLECTOR"
  }
]
... [truncated for display]
```

---
