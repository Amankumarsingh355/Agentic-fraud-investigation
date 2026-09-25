"""
Graph Topology Specialist Agent (TigerGraph Multi-Hop Explorer)
"""

from typing import Dict, Any, List
from datetime import datetime
from agent.agents.base_agent import BaseSpecialistAgent, AgentReport, AgentFinding

class GraphTopologyAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_graph_topology",
            agent_name="Graph Topology Agent",
            specialization="Multi-Hop Subgraph & Syndicate Ring Detection",
            avatar="🕸️"
        )

    def analyze(self, context: Dict[str, Any]) -> AgentReport:
        subgraph = context.get("subgraph", {})
        target = subgraph.get("target_transaction", {})
        rings = subgraph.get("shared_hardware_ring", {})
        findings = []
        key_evidence = []
        
        has_ring = rings.get("has_shared_ring", False)
        ring_size = rings.get("ring_size", 0)
        connected_custs = rings.get("connected_customers", [])
        connected_cards = rings.get("connected_cards", [])

        risk_score = 0.10
        confidence = 0.85
        status = "PASS"
        action = None

        if has_ring:
            if ring_size >= 5:
                risk_score = 0.98
                confidence = 0.96
                status = "CRITICAL"
                action = "ESCALATE_TO_L2_SYNDICATE"
                findings.append(AgentFinding(
                    finding_type="LARGE_SYNDICATE_RING",
                    description=f"Hardware profile is shared across {ring_size} distinct customer accounts: {connected_custs}.",
                    severity="CRITICAL",
                    score=0.98,
                    evidence_proof={"ring_size": ring_size, "customers": connected_custs, "cards": connected_cards}
                ))
            else:
                risk_score = 0.75
                confidence = 0.88
                status = "FLAGGED"
                action = "FLAG_FOR_REVIEW"
                findings.append(AgentFinding(
                    finding_type="SHARED_DEVICE_CLUSTER",
                    description=f"Device shared across {ring_size} accounts.",
                    severity="HIGH",
                    score=0.75,
                    evidence_proof={"ring_size": ring_size, "customers": connected_custs}
                ))
            
            key_evidence.append({
                "type": "syndicate_ring",
                "label": f"Hardware Ring Size: {ring_size}",
                "detail": f"{len(connected_cards)} cards attached to device"
            })
        else:
            findings.append(AgentFinding(
                finding_type="ISOLATED_DEVICE",
                description="Device is unique to the cardholder with no external ring connections.",
                severity="INFO",
                score=0.10,
                evidence_proof={"ring_size": 1}
            ))
            key_evidence.append({
                "type": "graph_isolation",
                "label": "Entity Isolation",
                "detail": "Zero cross-account hardware overlaps detected."
            })

        summary = (
            f"Graph analysis identified {ring_size} account(s) clustered around device. "
            f"Syndicate threat level is {status}."
        )

        return AgentReport(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            specialization=self.specialization,
            avatar=self.avatar,
            timestamp=datetime.utcnow().isoformat() + "Z",
            risk_score=risk_score,
            confidence=confidence,
            status=status,
            summary=summary,
            findings=findings,
            key_evidence=key_evidence,
            recommended_action=action,
            telemetry={
                "gsql_queries_run": ["target_transaction", "shared_hardware_ring"],
                "graph_hops_explored": 2,
                "nodes_evaluated": len(connected_custs) + len(connected_cards) + 2
            }
        )
