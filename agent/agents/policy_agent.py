"""
Policy & Regulatory Compliance Specialist Agent (Bank Policy & FinCEN SAR)
"""

from typing import Dict, Any, List
from datetime import datetime
from agent.agents.base_agent import BaseSpecialistAgent, AgentReport, AgentFinding
from agent.policy_engine import PolicyEngine
from agent.sar_generator import SARGenerator

class PolicyComplianceAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_policy_compliance",
            agent_name="Policy & Compliance Agent",
            specialization="Institutional Policy (Rules R1-R6) & FinCEN BSA/AML SAR",
            avatar="📜"
        )
        self.policy_engine = PolicyEngine()
        self.sar_generator = SARGenerator()

    def analyze(self, context: Dict[str, Any]) -> AgentReport:
        case = context.get("case")
        subgraph = context.get("subgraph", {})
        target = subgraph.get("target_transaction", {})
        rings = subgraph.get("shared_hardware_ring", {})
        
        findings = []
        key_evidence = []
        
        exposure = target.get("amount", 0.0)
        has_syndicate = rings.get("has_shared_ring", False) and rings.get("ring_size", 0) >= 5

        # Evaluate policy rules using institutional policy engine
        cust_status = context.get("customer_response") or "pending"
        actions = self.policy_engine.evaluate_actions(
            subgraph=subgraph,
            risk_assessment={"fraud_probability": 0.95 if cust_status == "denied_fraud" else 0.65},
            customer_verification_status=cust_status,
            trigger_type=context.get("trigger_type", "risk_score")
        )

        top_action = actions[0] if actions else {"action": "VERIFY_WITH_CUSTOMER", "policy_rule": "Rule R1", "route": "auto", "reason": "Default safety check"}
        triggered_rule = top_action.get("policy_rule", "Rule R1")
        rule_desc = top_action.get("reason", "Standard policy evaluation")
        mandated_route = top_action.get("route", "L1")

        # Evaluate SAR statutory requirements under Bank Fraud Policy v1.0 Section 4 ($1,000 threshold or syndicate)
        pattern = context.get("pattern", "")
        sar_required = exposure >= 1000.0 or has_syndicate or (context.get("verdict") == "fraud" and (exposure >= 1000.0 or rings.get("has_shared_ring", False) or pattern in ["syndicate_ring", "account_takeover"]))
        
        risk_score = 0.85 if sar_required else (0.60 if mandated_route != "auto" else 0.15)
        confidence = 0.95
        status = "CRITICAL" if sar_required else ("FLAGGED" if mandated_route != "auto" else "PASS")

        findings.append(AgentFinding(
            finding_type="POLICY_RULE_GROUNDING",
            description=f"Triggered Institutional Directive: Rule {triggered_rule} ({rule_desc}). Approval route: {mandated_route}.",
            severity="HIGH" if mandated_route != "auto" else "INFO",
            score=risk_score,
            evidence_proof=top_action
        ))

        key_evidence.append({
            "type": "institutional_rule",
            "label": f"Policy Rule {triggered_rule}",
            "detail": f"Routing: {mandated_route.upper()} Approval Required"
        })

        if sar_required:
            findings.append(AgentFinding(
                finding_type="FINCEN_SAR_MANDATE",
                description=f"Statutory filing triggered under BSA/AML 31 CFR 1020.320. Exposure: ${exposure:.2f} USD.",
                severity="CRITICAL",
                score=0.95,
                evidence_proof={"statutory_threshold_usd": 10000.0, "total_exposure": exposure}
            ))
            key_evidence.append({
                "type": "fincen_compliance",
                "label": "FinCEN SAR Filing: MANDATORY",
                "detail": "6-Question Narrative required for regulatory record"
            })
        else:
            findings.append(AgentFinding(
                finding_type="FINCEN_SAR_EXEMPT",
                description="Statutory monetary thresholds ($10,000 / $5,000 syndicate) not breached. Filing exempt.",
                severity="INFO",
                score=0.10,
                evidence_proof={"total_exposure": exposure}
            ))
            key_evidence.append({
                "type": "fincen_compliance",
                "label": "FinCEN SAR: EXEMPT",
                "detail": "Below statutory filing thresholds"
            })

        summary = (
            f"Policy grounding matched Rule {triggered_rule}. "
            f"Regulatory SAR filing is {'MANDATED' if sar_required else 'EXEMPT'}."
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
            recommended_action=f"ROUTE_TO_{mandated_route.upper()}",
            telemetry={
                "triggered_policy_rule": triggered_rule,
                "fincen_sar_mandated": sar_required,
                "approval_clearance": mandated_route
            }
        )
