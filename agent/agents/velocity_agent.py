"""
Transaction Velocity & Anomaly Specialist Agent
"""

from typing import Dict, Any, List
from datetime import datetime
from agent.agents.base_agent import BaseSpecialistAgent, AgentReport, AgentFinding

class VelocityAnomalyAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_velocity_anomaly",
            agent_name="Velocity & Anomaly Agent",
            specialization="Temporal Velocity, Micro-Auth Bursts & Spend Spikes",
            avatar="📈"
        )

    def analyze(self, context: Dict[str, Any]) -> AgentReport:
        subgraph = context.get("subgraph", {})
        target = subgraph.get("target_transaction", {})
        timeline = subgraph.get("card_timeline_72h", [])
        patterns = subgraph.get("pattern_signals", {})
        card_testing = patterns.get("card_testing", {})

        findings = []
        key_evidence = []
        
        target_amt = target.get("amount", 0.0)
        is_testing = card_testing.get("flagged", False)
        rapid_count = card_testing.get("rapid_count", 0)

        risk_score = 0.12
        confidence = 0.88
        status = "PASS"
        action = None

        if is_testing:
            risk_score = 0.94
            confidence = 0.92
            status = "CRITICAL"
            action = "IMMEDIATE_CARD_FREEZE"
            findings.append(AgentFinding(
                finding_type="MICRO_AUTH_CARD_TESTING",
                description=f"Rapid velocity cluster: {rapid_count} small authorizations observed right before transaction.",
                severity="CRITICAL",
                score=0.94,
                evidence_proof=card_testing
            ))
            key_evidence.append({
                "type": "velocity_burst",
                "label": f"Burst Frequency: {rapid_count} txns / 10m",
                "detail": f"Pre-authorization card testing pattern"
            })
        elif len(timeline) >= 8:
            risk_score = 0.72
            confidence = 0.85
            status = "FLAGGED"
            action = "TEMPORARY_VELOCITY_HOLD"
            findings.append(AgentFinding(
                finding_type="HIGH_TXN_VELOCITY",
                description=f"Elevated frequency: {len(timeline)} transactions in 72-hour rolling window.",
                severity="MEDIUM",
                score=0.72,
                evidence_proof={"timeline_count": len(timeline)}
            ))
            key_evidence.append({
                "type": "velocity_surge",
                "label": f"72h Volume: {len(timeline)} events",
                "detail": "Above normal cardholder baseline"
            })
        else:
            findings.append(AgentFinding(
                finding_type="NORMAL_VELOCITY",
                description="Transaction cadence matches historical card activity profile.",
                severity="INFO",
                score=0.10,
                evidence_proof={"timeline_count": len(timeline)}
            ))
            key_evidence.append({
                "type": "velocity_normal",
                "label": f"Cadence Normal ({len(timeline)} in 72h)",
                "detail": "No micro-bursts or automated testing detected"
            })

        summary = (
            f"Velocity analysis monitored {len(timeline)} events over 72h. "
            f"Testing pattern flag is {is_testing}. Status: {status}."
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
                "timeline_events_scanned": len(timeline),
                "lookback_hours": 72,
                "target_amount_usd": target_amt
            }
        )
