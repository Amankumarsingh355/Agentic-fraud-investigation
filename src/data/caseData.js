export const goldStandardPayload = {
  "case_id": "TG-CASE-2026-8819",
  "overall_fraud_score": 0.94,
  "fraud_type_detected": "Circular Payment Fraud Ring",
  "investigation_status": "RESOLVED",
  "key_evidence": [
    "Shared Device_99",
    "3-Hop Transfer Path",
    "High-Value $15k Outflow",
    "Precedent Match #HHG-001 (94% Sim)"
  ],
  "tigergraph_ring_findings": {
    "shared_nodes": "Device_99 (IP: 192.168.1.23)",
    "hops_traversed": "3-hop path between User_101 -> Device_99 -> User_882 -> Wallet_X7",
    "graph_risk_level": "CRITICAL"
  },
  "agent_contributions": {
    "agent_1_ingestion": "Received High-Risk Alert (Score 0.61)",
    "agent_2_tigergraph": "Uncovered shared device and circular transfer edges via gsql query",
    "agent_3_pattern": "Classified structure as Circular Payment Fraud Ring",
    "agent_8_policy": "Auto-freeze approved under Policy Rule R6 (Syndicate / Shared Device)",
    "agent_9_stopping": "Early termination triggered at Step 4 due to high evidence density"
  },
  "final_action": "Freeze Account",
  "human_approval_required": false,
  "audit_rationale": "High-confidence fraud ring detected using TigerGraph multi-hop analysis. Shared device with known fraudster and circular funds movement justify immediate automated freeze under Policy Rule R6."
};
