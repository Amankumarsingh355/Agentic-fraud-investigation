# Phase 7 Verification Report: Explainability & Exact Output Format

**Status**: VERIFIED & PASSING
**Date**: September 21, 2026
**Scope**: Validation of the 3-part submission JSON artifact against the exact schema specified in README.md (case, sar, next_best_actions).

---

## Phase 7 Gate Result: PASSED (0 Schema Errors)

### Sample Case Validated: `HHG-001` (Txn `3514030`)
- **Verdict**: `fraud`
- **Status**: `closed_fraud`
- **Fraud Probability**: `0.98`
- **Pattern**: `out_of_region_use`
- **Written to Graph**: `True` (`CASE-3514030`)
- **SAR File Mandated**: `False`
- **Next Best Actions**: `3` initial $\rightarrow$ `2` final

### Generated Submission Artifact (`cases/HHG-001.json`)
```json
{
  "case_id": "HHG-001",
  "case": {
    "status": "closed_fraud",
    "verdict": "fraud",
    "fraud_probability": 0.98,
    "pattern": "out_of_region_use",
    "pattern_description": "",
    "affected_txn_ids": [
      "3514030"
    ],
    "first_suspicious_txn_id": "3514030",
    "connected_card_ids": [],
    "connected_device_profiles": [],
    "exposure_usd": 77.07,
    "evidence": [
      {
        "claim": "Cardholder Profile for C12382",
        "source": "customer",
        "ref": "evidence_request:1",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Flagged Transaction 3514030 ($ 77.07)",
        "source": "graph",
        "ref": "query:target_transaction(txn_id=3514030)",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Rolling 72-Hour Timeline (8 events)",
        "source": "graph",
        "ref": "query:velocity_timeline(txn_id=3514030)",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Typology Pattern Recognition Checks",
        "source": "graph",
        "ref": "query:pattern_signals(txn_id=3514030)",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Shared Hardware Syndicate Ring Discovery",
        "source": "graph",
        "ref": "query:hardware_rings(txn_id=3514030)",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "**Rule R1: Verify Before You Block on a Weak Signal**",
        "source": "document",
        "ref": "document:bank_fraud_policy",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Closed Case CC-1541 (confirmed_fraud, out_of_region_use)",
        "source": "document",
        "ref": "document:bank_fraud_policy",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "[DYNAMIC MEMORY] Precedent Case MEM-RUN-1 (confirmed_fraud, out_of_region_use)",
        "source": "graph",
        "ref": "query:similar_prior_cases",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Precedent Case CC-1541 (confirmed_fraud, out_of_region_use)",
        "source": "graph",
        "ref": "query:similar_prior_cases",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Precedent Case CC-2923 (confirmed_fraud, out_of_region_use)",
        "source": "graph",
        "ref": "query:similar_prior_cases",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      },
      {
        "claim": "Customer Verification Response: denied_fraud: denied_fraud",
        "source": "customer",
        "ref": "evidence_request:1",
        "entity_ids": [
          "3514030",
          "C12382-K1"
        ]
      }
    ],
    "similar_prior_cases": [
      "MEM-RUN-1",
      "CC-1541",
      "CC-2923"
    ],
    "summary": "Investigation of transaction 3514030 ($77.07) on card C12382-K1 concluded with verdict 'fraud'. Assessed fraud probability is 0.98 based on out of region use indicators and bank baseline metrics. Precedent case memory retrieval drew upon prior historical cases MEM-RUN-1, CC-1541. Next best actions were formulated under Bank Fraud Policy v1.0 with appropriate approval authority routes.",
    "written_to_graph": true,
    "graph_case_id": "CASE-3514030"
  },
  "evidence_requests": [
    {
      "type": "customer_validation",
      "asked_after_step": 4,
      "assumed_response": "Customer states they did not make this purchase of $77.07 and still has physical possession of the card."
    }
  ],
  "next_best_actions": {
    "initial": [
      {
        "action": "CREATE_CASE",
        "route": "auto",
        "reason": "Out-of-region in-person spend recorded."
      },
      {
        "action": "VERIFY_WITH_CUSTOMER",
        "route": "auto",
        "reason": "Verify out-of-region POS charge in Region 444.0 with cardholder before taking blocking action."
      },
      {
        "action": "MONITOR_CARD",
        "route": "auto",
        "reason": "Temporarily monitor card while awaiting cardholder verification response."
      }
    ],
    "final": [
      {
        "action": "CREATE_CASE",
        "route": "auto",
        "reason": "Customer explicitly denied transaction. Open formal fraud case."
      },
      {
        "action": "BLOCK_CARD",
        "route": "L1",
        "reason": "Compromised card replacement required for customer-reported fraud ($77.07 exposure)."
      }
    ],
    "what_changed": "Customer denial raised fraud probability from 0.71 to 0.98, confirming the need for permanent card block and fraud case creation."
  },
  "sar": {
    "file": false,
    "reason": "No regulatory SAR required: transaction confirmed legitimate or financial exposure does not meet statutory reporting threshold under BSA/FinCEN guidelines.",
    "narrative": "",
    "subjects": [],
    "total_amount_usd": 0,
    "activity_dates": []
  },
  "stop_reason": "Policy actions formulated and staged for required human approval; case saved to graph memory.",
  "tool_calls": 9,
  "tokens": 11200,
  "latency_s": 0.1
}
```

---

## Graph Memory Record Inspection
```json
{
  "case_id": "HHG-001",
  "outcome": "confirmed_fraud",
  "pattern": "out_of_region_use",
  "exposure_usd": 77.07,
  "customer_id": "C12382",
  "card_id": "C12382-K1",
  "flagged_txn_id": 3514030,
  "is_benchmark": true,
  "namespace": "eval_benchmark",
  "narrative": "### Investigation Summary for Case HHG-001\n**Transaction**: `3514030` | **Amount**: `$77.07` | **Trigger**: `risk_score`\n\n**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertainty: `0.02`)\n\n#### Traceable Evidence & Reasoning\n- **Trigger Prior**: Bank Risk Model Score (0.61) (+0.41): Real-time automated transaction scoring model.\n- **Corroborating Signal**: Out-of-Region In-Person POS (+0.20): Physical card used in region 444.0 away from established home 204.0.\n- **Corroborating Signal**: Explicit Customer Denial of Charge (Rule R2) (+0.90): Cardholder explicitly stated they did not authorize this purchase.\n- **Mitigating Signal**: Established Customer History (-0.10): Customer has 422 historical transactions totaling $48,783.68.\n\n#### Case Memory Precedents Informing Decision\n- **[DYNAMIC MEMORY] Precedent Case MEM-RUN-1 (confirmed_fraud, out_of_region_use)** (Score: 0.55 | Source: *TigerGraph Dynamic Case Memory*):\n  \"### Investigation Summary for Case MEM-RUN-1\n**Transaction**: `3000332` | **Amount**: `$117.05` | **Trigger**: `risk_score`\n\n**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertaint...\"\n- **Precedent Case CC-1541 (confirmed_fraud, out_of_region_use)** (Score: 0.4891 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-1541: cardholder C02250 reported unrecognized activity on card C02250-K2. 1 transaction(s) between 2016-08-01 and 2016-08-01 totaling $77.02 were confirmed fraudulent. Card-present use in a bi...\"\n- **Precedent Case CC-2923 (confirmed_fraud, out_of_region_use)** (Score: 0.4869 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-2923: cardholder C00088 reported unrecognized activity on card C00088-K1. 1 transaction(s) between 2016-08-31 and 2016-08-31 totaling $77.00 were confirmed fraudulent. Card-present use in a bi...\"\n\n#### Policy Gated Actions & Next Steps\n- **CREATE_CASE** (`auto` - EXECUTED): Customer explicitly denied transaction. Open formal fraud case. (Governing: *Rule R2*)\n- **BLOCK_CARD** (`L1` - PENDING_HUMAN_APPROVAL): Compromised card replacement required for customer-reported fraud ($77.07 exposure). (Governing: *Rule R2*)",
  "actions_taken": [
    "CREATE_CASE",
    "BLOCK_CARD"
  ],
  "graph_vertices": {
    "Case": {
      "case_id": "HHG-001",
      "opened_at": "2026-09-21T11:33:11.213031",
      "closed_at": "2026-09-21T11:33:11.256930",
      "status": "RESOLVED",
      "outcome": "confirmed_fraud",
      "pattern": "out_of_region_use",
      "exposure_usd": 77.07,
      "is_benchmark": true,
      "namespace": "eval_benchmark",
      "narrative": "### Investigation Summary for Case HHG-001\n**Transaction**: `3514030` | **Amount**: `$77.07` | **Trigger**: `risk_score`\n\n**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertainty: `0.02`)\n\n#### Traceable Evidence & Reasoning\n- **Trigger Prior**: Bank Risk Model Score (0.61) (+0.41): Real-time automated transaction scoring model.\n- **Corroborating Signal**: Out-of-Region In-Person POS (+0.20): Physical card used in region 444.0 away from established home 204.0.\n- **Corroborating Signal**: Explicit Customer Denial of Charge (Rule R2) (+0.90): Cardholder explicitly stated they did not authorize this purchase.\n- **Mitigating Signal**: Established Customer History (-0.10): Customer has 422 historical transactions totaling $48,783.68.\n\n#### Case Memory Precedents Informing Decision\n- **[DYNAMIC MEMORY] Precedent Case MEM-RUN-1 (confirmed_fraud, out_of_region_use)** (Score: 0.55 | Source: *TigerGraph Dynamic Case Memory*):\n  \"### Investigation Summary for Case MEM-RUN-1\n**Transaction**: `3000332` | **Amount**: `$117.05` | **Trigger**: `risk_score`\n\n**Assessed Fraud Probability**: `0.98` | **Confidence**: `HIGH` (Uncertaint...\"\n- **Precedent Case CC-1541 (confirmed_fraud, out_of_region_use)** (Score: 0.4891 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-1541: cardholder C02250 reported unrecognized activity on card C02250-K2. 1 transaction(s) between 2016-08-01 and 2016-08-01 totaling $77.02 were confirmed fraudulent. Card-present use in a bi...\"\n- **Precedent Case CC-2923 (confirmed_fraud, out_of_region_use)** (Score: 0.4869 | Source: *TigerGraph Case Memory (Historical)*):\n  \"Case CC-2923: cardholder C00088 reported unrecognized activity on card C00088-K1. 1 transaction(s) between 2016-08-31 and 2016-08-31 totaling $77.00 were confirmed fraudulent. Card-present use in a bi...\"\n\n#### Policy Gated Actions & Next Steps\n- **CREATE_CASE** (`auto` - EXECUTED): Customer explicitly denied transaction. Open formal fraud case. (Governing: *Rule R2*)\n- **BLOCK_CARD** (`L1` - PENDING_HUMAN_APPROVAL): Compromised card replacement required for customer-reported fraud ($77.07 exposure). (Governing: *Rule R2*)"
    },
    "Evidence": [
      {
        "evidence_id": "HHG-001-EV-001",
        "evidence_type": "customer_baseline",
        "source": "TigerGraph / Customer",
        "title": "Cardholder Profile for C12382",
        "score": null
      },
      {
        "evidence_id": "HHG-001-EV-002",
        "evidence_type": "target_transaction",
        "source": "TigerGraph / Transaction",
        "title": "Flagged Transaction 3514030 ($ 77.07)",
        "score": 0.61
      },
      {
        "evidence_id": "HHG-001-EV-003",
        "evidence_type": "velocity_timeline",
        "source": "TigerGraph / Card History",
        "title": "Rolling 72-Hour Timeline (8 events)",
        "score": null
      },
      {
        "evidence_id": "HHG-001-EV-004",
        "evidence_type": "pattern_signals",
        "source": "Pattern Engine",
        "title": "Typology Pattern Recognition Checks",
        "score": null
      },
      {
        "evidence_id": "HHG-001-EV-005",
        "evidence_type": "hardware_rings",
        "source": "Graph Ring Algorithms",
        "title": "Shared Hardware Syndicate Ring Discovery",
        "score": null
      },
      {
        "evidence_id": "HHG-001-EV-006",
        "evidence_type": "policy_citation",
        "source": "Bank Fraud Policy Store",
        "title": "**Rule R1: Verify Before You Block on a Weak Signal**",
        "score": 0.2939
      },
      {
        "evidence_id": "HHG-001-EV-007",
        "evidence_type": "policy_citation",
        "source": "Bank Fraud Policy Store",
        "title": "Closed Case CC-1541 (confirmed_fraud, out_of_region_use)",
        "score": 0.091
      },
      {
        "evidence_id": "HHG-001-EV-008",
        "evidence_type": "case_precedent",
        "source": "TigerGraph Dynamic Case Memory",
        "title": "[DYNAMIC MEMORY] Precedent Case MEM-RUN-1 (confirmed_fraud, out_of_region_use)",
        "score": 0.55
      },
      {
        "evidence_id": "HHG-001-EV-009",
        "evidence_type": "case_precedent",
        "source": "TigerGraph Case Memory (Historical)",
        "title": "Precedent Case CC-1541 (confirmed_fraud, out_of_region_use)",
        "score": 0.4891
      },
      {
        "evidence_id": "HHG-001-EV-010",
        "evidence_type": "case_precedent",
        "source": "TigerGraph Case Memory (Historical)",
        "title": "Precedent Case CC-2923 (confirmed_fraud, out_of_region_use)",
        "score": 0.4869
      },
      {
        "evidence_id": "HHG-001-EV-011",
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
        "from": 3514030,
        "to": "HHG-001"
      }
    ],
    "INVESTIGATED_CARD": [
      {
        "from": "HHG-001",
        "to": "C12382-K1"
      }
    ],
    "INVESTIGATED_CUSTOMER": [
      {
        "from": "HHG-001",
        "to": "C12382"
      }
    ],
    "ATTACHED_EVIDENCE": [
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-001"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-002"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-003"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-004"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-005"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-006"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-007"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-008"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-009"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-010"
      },
      {
        "from": "HHG-001",
        "to": "HHG-001-EV-011"
      }
    ],
    "APPLIED_POLICY": [
      {
        "from": "HHG-001",
        "to": "Rule R2"
      },
      {
        "from": "HHG-001",
        "to": "Rule R2"
      }
    ]
  },
  "persisted_at": "2026-09-21T11:33:11.256962"
}
```