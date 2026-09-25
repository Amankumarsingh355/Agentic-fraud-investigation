"""
Stateful Investigation State Machine & Schema Definition
Core Architecture: 11-Agent Autonomous Fraud Investigation Pipeline
Guarantees typed state transitions, explicit evidence tracking,
auditable history, and clean handoffs across all 11 agents.
"""

import time
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class InvestigationStatus(str, Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"
    EVIDENCE_RECEIVED = "EVIDENCE_RECEIVED"
    REINVESTIGATION = "REINVESTIGATION"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class UncertaintyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ApprovalRoute(str, Enum):
    AUTO = "auto"
    L1 = "L1"
    L2 = "L2"


class AuditEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stage: str
    event_type: str
    description: str
    actor: str = "AGENTIC_SYSTEM"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    claim: str
    source: str  # "graph" | "document" | "customer" | "external"
    ref: str
    entity_ids: List[str] = Field(default_factory=list)
    confidence: float = 1.0


class PolicyCitation(BaseModel):
    rule_id: str  # e.g., "Rule R1", "Rule R6"
    title: str
    relevance_score: float = 0.0
    text_snippet: str = ""
    requires_approval: str = "auto"  # "auto" | "L1" | "L2"


class ActionItem(BaseModel):
    action: str  # One of the 14 Bank Fraud Policy actions
    route: str  # "auto" | "L1" | "L2"
    reason: str  # Must cite policy rule
    policy_rule: Optional[str] = None
    approval_role: Optional[str] = None
    is_autonomous: bool = True
    status: str = "RECOMMENDED"  # RECOMMENDED | AWAITING_APPROVAL | APPROVED | REJECTED | EXECUTED


class EvidenceRequest(BaseModel):
    type: str  # "customer_validation" | "step_up_auth" | "analyst_info" | "device_verification"
    asked_after_step: int = 1
    reason: str = ""
    assumed_response: Optional[str] = None
    actual_response: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SARRecord(BaseModel):
    file: bool = False
    reason: str = ""
    narrative: str = ""
    subjects: List[str] = Field(default_factory=list)
    total_amount_usd: float = 0.0
    activity_dates: List[str] = Field(default_factory=list)


class InvestigationState(BaseModel):
    """
    Central mutable state object for an investigation.
    Maintains complete data integrity, prevents hidden state,
    and isolates domain responsibilities between agents.
    """
    case_id: str
    status: InvestigationStatus = InvestigationStatus.NEW
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Trigger & Transaction Parameters
    flagged_txn_id: int
    user_id: str
    customer_id: str
    card_id: str
    amount: float = 0.0
    channel: str = "online"
    trigger_type: str = "risk_score"
    trigger_text: str = ""
    initial_risk_score: Optional[float] = None

    # Graph Evidence
    subgraph: Dict[str, Any] = Field(default_factory=dict)
    hardware_ring: Dict[str, Any] = Field(default_factory=dict)
    connected_customers: List[str] = Field(default_factory=list)
    connected_cards: List[str] = Field(default_factory=list)
    connected_devices: List[str] = Field(default_factory=list)
    affected_txn_ids: List[str] = Field(default_factory=list)
    timeline_72h: List[Dict[str, Any]] = Field(default_factory=list)

    # Typology & Pattern
    fraud_pattern: str = "none"  # card_testing, cnp, out_of_region, ato, undocumented, none
    pattern_description: str = ""

    # Mathematical Uncertainty & Risk Metrics
    risk_score: float = 0.0  # Assessed probability of fraud [0.0 - 1.0]
    confidence_score: float = 0.50  # Evidence strength [0.0 - 1.0]
    evidence_completeness: float = 0.50  # Completeness ratio [0.0 - 1.0]
    uncertainty_score: float = 0.50  # 1.0 - confidence_score
    uncertainty_level: UncertaintyLevel = UncertaintyLevel.MEDIUM
    is_evidence_sufficient: bool = False
    evidence_gaps: List[str] = Field(default_factory=list)
    corroboration_count: int = 0
    mitigating_count: int = 0

    # Structured GraphRAG Evidence
    evidence_list: List[EvidenceItem] = Field(default_factory=list)
    policy_citations: List[PolicyCitation] = Field(default_factory=list)
    historical_cases: List[Dict[str, Any]] = Field(default_factory=list)

    # Additional Evidence Loop
    evidence_requests: List[EvidenceRequest] = Field(default_factory=list)
    evidence_responses: List[Dict[str, Any]] = Field(default_factory=list)

    # Two-Stage Next-Best-Action Evolution
    initial_actions: List[ActionItem] = Field(default_factory=list)
    final_actions: List[ActionItem] = Field(default_factory=list)
    what_changed: str = "nothing"
    final_action_taken: str = "MONITOR_CARD"

    # Human Approval
    human_approval_required: bool = False
    approval_route: str = "auto"
    approval_status: str = "NONE"  # NONE | AWAITING_APPROVAL | APPROVED | REJECTED | ESCALATED
    approval_record: Optional[Dict[str, Any]] = None

    # Regulatory SAR
    sar: SARRecord = Field(default_factory=SARRecord)

    # Final Synthesis & Audit Trail
    verdict: str = "uncertain"  # "fraud" | "legitimate" | "uncertain"
    exposure_usd: float = 0.0
    summary: str = ""
    audit_rationale: str = ""
    stop_reason: str = ""
    tool_calls: int = 0
    tokens: int = 0
    latency_s: float = 0.0
    written_to_graph: bool = False
    graph_case_id: str = ""

    # Chronological Audit Ledger
    audit_events: List[AuditEvent] = Field(default_factory=list)

    def add_audit_event(self, stage: str, event_type: str, description: str, actor: str = "AGENTIC_SYSTEM", metadata: Dict[str, Any] = None):
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            stage=stage,
            event_type=event_type,
            description=description,
            actor=actor,
            metadata=metadata or {}
        )
        self.audit_events.append(event)
        self.updated_at = event.timestamp

    def transition_status(self, new_status: InvestigationStatus, reason: str, actor: str = "AGENTIC_SYSTEM"):
        prev = self.status
        self.status = new_status
        self.add_audit_event(
            stage="LIFECYCLE_TRANSITION",
            event_type="STATUS_CHANGED",
            description=f"Status changed from {prev.value} to {new_status.value}: {reason}",
            actor=actor,
            metadata={"previous_status": prev.value, "new_status": new_status.value}
        )

    def add_evidence(self, claim: str, source: str, ref: str, entity_ids: List[str] = None, confidence: float = 1.0):
        e = EvidenceItem(
            claim=claim,
            source=source,
            ref=ref,
            entity_ids=entity_ids or [],
            confidence=confidence
        )
        self.evidence_list.append(e)

    def record_evidence_request(self, req_type: str, asked_after_step: int, reason: str, assumed_response: Optional[str] = None):
        req = EvidenceRequest(
            type=req_type,
            asked_after_step=asked_after_step,
            reason=reason,
            assumed_response=assumed_response
        )
        self.evidence_requests.append(req)
        self.transition_status(
            InvestigationStatus.EVIDENCE_REQUESTED,
            f"Requested {req_type}: {reason}"
        )

    def apply_evidence_response(self, response_text: str, source: str = "cardholder"):
        self.evidence_responses.append({
            "response": response_text,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        if self.evidence_requests:
            self.evidence_requests[-1].actual_response = response_text
        self.transition_status(
            InvestigationStatus.EVIDENCE_RECEIVED,
            f"Received response from {source}: {response_text}"
        )
