"""
Case Data Model & Audit Trail Object
Represents an end-to-end fraud investigation case including:
- Case status lifecycle
- Evidence list (multi-hop graph, hardware, velocity, policies, precedents)
- Key analytical findings
- Inspectable risk & uncertainty assessment
- Recommended and executed actions with policy approval gating
- Immutable audit trail
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class Case:
    def __init__(
        self,
        case_id: str,
        trigger_type: str,
        trigger_text: str,
        flagged_txn_id: int,
        card_id: str,
        customer_id: str,
        risk_score: Optional[float] = None,
        opened_at: Optional[str] = None
    ):
        self.case_id = case_id
        self.opened_at = opened_at or datetime.now().isoformat()
        self.closed_at = None
        self.status = "OPEN"  # OPEN, INVESTIGATING, EVIDENCE_PENDING, RESOLVED, CLOSED
        
        self.trigger = {
            "type": trigger_type,
            "text": trigger_text,
            "flagged_txn_id": flagged_txn_id,
            "card_id": card_id,
            "customer_id": customer_id,
            "risk_score": risk_score,
            "timestamp": self.opened_at
        }
        
        self.evidence_list: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, Any]] = []
        self.risk_assessment: Dict[str, Any] = {
            "fraud_probability": 0.0,
            "uncertainty_score": 1.0,
            "confidence_level": "LOW",
            "has_sufficient_evidence": False,
            "criteria_breakdown": {},
            "evidence_gaps": []
        }
        self.actions: List[Dict[str, Any]] = []
        self.audit_trail: List[Dict[str, Any]] = []
        self.decision_explanation: str = ""
        self.case_notes: List[str] = []
        
        # Record creation in audit trail
        self.add_audit_event(
            stage="TRIGGER",
            event_type="CASE_OPENED",
            description=f"Case {case_id} initialized via {trigger_type} for Txn {flagged_txn_id} (Customer {customer_id}, Card {card_id}).",
            actor="SYSTEM_TRIGGER_HANDLER"
        )

    def set_status(self, new_status: str, reason: str = ""):
        old_status = self.status
        self.status = new_status
        if new_status in ["RESOLVED", "CLOSED"] and not self.closed_at:
            self.closed_at = datetime.now().isoformat()
        self.add_audit_event(
            stage="LIFECYCLE",
            event_type="STATUS_CHANGED",
            description=f"Status transitioned from {old_status} to {new_status}. {reason}".strip(),
            actor="AGENT_CORE"
        )

    def add_evidence(self, evidence_type: str, source: str, title: str, details: Any, score: Optional[float] = None):
        ev_id = f"EV-{len(self.evidence_list) + 1:03d}"
        evidence_item = {
            "evidence_id": ev_id,
            "type": evidence_type, # graph_subgraph, hardware_profile, velocity_timeline, pattern_flag, policy_citation, case_precedent
            "source": source,
            "title": title,
            "details": details,
            "score": score,
            "recorded_at": datetime.now().isoformat()
        }
        self.evidence_list.append(evidence_item)
        self.add_audit_event(
            stage="GATHER_EVIDENCE",
            event_type="EVIDENCE_ADDED",
            description=f"Added evidence [{ev_id}] ({evidence_type}): {title}",
            actor="EVIDENCE_COLLECTOR"
        )
        return ev_id

    def add_finding(self, finding_type: str, description: str, severity: str = "INFO", graph_proof: Optional[Dict[str, Any]] = None):
        finding = {
            "finding_id": f"FND-{len(self.findings) + 1:02d}",
            "type": finding_type,
            "description": description,
            "severity": severity, # INFO, LOW, MEDIUM, HIGH, CRITICAL
            "graph_proof": graph_proof or {},
            "timestamp": datetime.now().isoformat()
        }
        self.findings.append(finding)
        self.add_audit_event(
            stage="INVESTIGATE",
            event_type="FINDING_RECORDED",
            description=f"Recorded {severity} finding: {description}",
            actor="ANALYTICAL_ENGINE"
        )

    def update_risk_assessment(
        self,
        fraud_probability: float,
        uncertainty_score: float,
        confidence_level: str,
        has_sufficient_evidence: bool,
        criteria_breakdown: Dict[str, Any],
        evidence_gaps: List[str]
    ):
        self.risk_assessment = {
            "fraud_probability": round(fraud_probability, 4),
            "uncertainty_score": round(uncertainty_score, 4),
            "confidence_level": confidence_level, # LOW, MEDIUM, HIGH
            "has_sufficient_evidence": has_sufficient_evidence,
            "criteria_breakdown": criteria_breakdown,
            "evidence_gaps": evidence_gaps,
            "updated_at": datetime.now().isoformat()
        }
        self.add_audit_event(
            stage="ASSESS_UNCERTAINTY",
            event_type="RISK_ASSESSMENT_UPDATED",
            description=(
                f"Assessed Fraud Probability={fraud_probability:.2f}, "
                f"Confidence={confidence_level} (Uncertainty={uncertainty_score:.2f}). "
                f"Sufficient Evidence to Act={has_sufficient_evidence}."
            ),
            actor="UNCERTAINTY_ENGINE"
        )

    def record_action(
        self,
        action_name: str,
        route: str, # auto, L1, L2
        status: str, # EXECUTED, STAGED_FOR_APPROVAL, REJECTED
        reason: str,
        policy_rule: str,
        side_effects: Dict[str, Any]
    ):
        action_id = f"ACT-{len(self.actions) + 1:02d}"
        action_record = {
            "action_id": action_id,
            "action_name": action_name,
            "route": route,
            "status": status,
            "reason": reason,
            "policy_rule": policy_rule,
            "side_effects": side_effects,
            "timestamp": datetime.now().isoformat()
        }
        self.actions.append(action_record)
        self.add_audit_event(
            stage="EXECUTE_ACTIONS",
            event_type="ACTION_RECORDED",
            description=f"Action {action_name} [{status}] via route '{route}'. Rule: {policy_rule}. Reason: {reason}",
            actor="POLICY_ROUTER"
        )
        return action_id

    def add_audit_event(self, stage: str, event_type: str, description: str, actor: str = "AGENT"):
        event = {
            "index": len(self.audit_trail) + 1,
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "event_type": event_type,
            "description": description,
            "actor": actor
        }
        self.audit_trail.append(event)

    def set_explanation(self, explanation_text: str):
        self.decision_explanation = explanation_text
        self.add_audit_event(
            stage="EXPLAIN_DECISION",
            event_type="EXPLANATION_GENERATED",
            description="Generated full audit-compliant rationale for case adjudication.",
            actor="EXPLANATION_ENGINE"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at,
            "status": self.status,
            "trigger": self.trigger,
            "risk_assessment": self.risk_assessment,
            "findings": self.findings,
            "actions": self.actions,
            "evidence_summary": [
                {
                    "evidence_id": e["evidence_id"],
                    "type": e["type"],
                    "title": e["title"],
                    "score": e.get("score")
                }
                for e in self.evidence_list
            ],
            "evidence_list": self.evidence_list,
            "decision_explanation": self.decision_explanation,
            "audit_trail": self.audit_trail
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)
