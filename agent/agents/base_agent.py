"""
Base Agent Definition for Specialized Fraud Investigation Squad
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentFinding:
    finding_type: str
    description: str
    severity: str # INFO, LOW, MEDIUM, HIGH, CRITICAL
    score: float # 0.0 to 1.0
    evidence_proof: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentReport:
    agent_id: str
    agent_name: str
    specialization: str
    avatar: str
    timestamp: str
    risk_score: float # 0.0 to 1.0
    confidence: float # 0.0 to 1.0
    status: str # "PASS", "FLAGGED", "CRITICAL", "INCONCLUSIVE"
    summary: str
    findings: List[AgentFinding] = field(default_factory=list)
    key_evidence: List[Dict[str, Any]] = field(default_factory=list)
    recommended_action: Optional[str] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "specialization": self.specialization,
            "avatar": self.avatar,
            "timestamp": self.timestamp,
            "risk_score": round(self.risk_score, 3),
            "confidence": round(self.confidence, 3),
            "status": self.status,
            "summary": self.summary,
            "findings": [
                {
                    "finding_type": f.finding_type,
                    "description": f.description,
                    "severity": f.severity,
                    "score": round(f.score, 3),
                    "evidence_proof": f.evidence_proof
                }
                for f in self.findings
            ],
            "key_evidence": self.key_evidence,
            "recommended_action": self.recommended_action,
            "telemetry": self.telemetry
        }

class BaseSpecialistAgent(ABC):
    def __init__(self, agent_id: str, agent_name: str, specialization: str, avatar: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.specialization = specialization
        self.avatar = avatar

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> AgentReport:
        """
        Takes investigation context (subgraph, transaction, customer profile, etc.)
        and returns a standardized AgentReport.
        """
        pass
