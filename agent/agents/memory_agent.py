"""
Case Memory & Precedents Specialist Agent
"""

from typing import Dict, Any, List
from datetime import datetime
from agent.agents.base_agent import BaseSpecialistAgent, AgentReport, AgentFinding
from graph.similar_cases_engine import SimilarCasesEngine
from graph.load_vector_store import VectorRetriever
from graph.case_memory import CaseMemoryManager
from graph.pattern_registry import PatternRegistry

class CaseMemoryAgent(BaseSpecialistAgent):
    def __init__(self, similar_engine: Any = None, vector_retriever: Any = None):
        super().__init__(
            agent_id="agent_case_memory",
            agent_name="Case Memory Agent",
            specialization="5,565 Historical Graph Precedents & Analyst Decisions",
            avatar="🧠"
        )
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.similar_engine = similar_engine or SimilarCasesEngine(retriever=self.vector_retriever)
        self.case_memory_manager = CaseMemoryManager()
        self.pattern_registry = PatternRegistry()

    def analyze(self, context: Dict[str, Any]) -> AgentReport:
        subgraph = context.get("subgraph") or {}
        target = subgraph.get("target_transaction") or {}
        dev_obj = subgraph.get("identity_device") or {}
        
        trigger_text = context.get("trigger_text", "")
        dominant_pattern = context.get("dominant_pattern", "none")
        cust_id = target.get("customer_id", "C00000")
        exposure = target.get("amount", 0.0)

        findings = []
        key_evidence = []

        # 1. Search prior closed cases
        memory_hits = self.similar_engine.find_similar_cases(
            query_text=f"{trigger_text} {dominant_pattern} amount ${exposure:.2f}",
            target_pattern=dominant_pattern if dominant_pattern != "none" else None,
            target_exposure=exposure,
            target_customer=cust_id,
            top_k=3
        )

        # 2. Check pattern registry for recurring malicious entities
        dev_str = dev_obj.get("device_profile")
        proxy_str = dev_obj.get("proxy_status")
        registry_matches = self.pattern_registry.check_entity(
            device_profile=dev_str,
            proxy_status=proxy_str
        )

        has_recurring = len(registry_matches) > 0
        top_precedent = memory_hits[0] if memory_hits else None
        top_score = top_precedent.get("similarity_score", 0.0) if top_precedent else 0.0

        risk_score = 0.88 if has_recurring else (0.75 if top_score > 0.85 else 0.20)
        confidence = 0.90
        status = "CRITICAL" if has_recurring else ("FLAGGED" if top_score > 0.80 else "PASS")

        if has_recurring:
            for rm in registry_matches:
                findings.append(AgentFinding(
                    finding_type="RECURRING_FRAUD_ENTITY_MATCH",
                    description=f"Entity alert: {rm['risk_signal']} matched previous case {rm['first_case_id']}.",
                    severity="CRITICAL",
                    score=0.95,
                    evidence_proof=rm
                ))
            key_evidence.append({
                "type": "registry_match",
                "label": "Recurring Entity Alert",
                "detail": f"Matched past incident {registry_matches[0]['first_case_id']}"
            })

        if memory_hits:
            for mh in memory_hits[:2]:
                findings.append(AgentFinding(
                    finding_type="HISTORICAL_CASE_PRECEDENT",
                    description=f"Precedent Case {mh['case_id']} ({mh.get('pattern_type', 'general')}) with similarity score {mh.get('similarity_score', 0):.2f}.",
                    severity="HIGH" if mh.get("similarity_score", 0) > 0.85 else "MEDIUM",
                    score=mh.get("similarity_score", 0.5),
                    evidence_proof=mh
                ))
                key_evidence.append({
                    "type": "case_precedent",
                    "label": f"Precedent {mh['case_id']}",
                    "detail": f"{int(mh.get('similarity_score', 0)*100)}% Match • Decision: {mh.get('historical_decision', 'BLOCK_CARD')}"
                })
        else:
            findings.append(AgentFinding(
                finding_type="NO_PRECEDENT_OVERLAP",
                description="No highly correlated previous fraud cases identified in memory bank.",
                severity="INFO",
                score=0.10,
                evidence_proof={}
            ))

        precedent_ids = [m["case_id"] for m in memory_hits]
        summary = (
            f"Case memory retrieved {len(memory_hits)} similar prior cases ({', '.join(precedent_ids[:2])}). "
            f"Recurring entity flag: {has_recurring}."
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
            recommended_action=top_precedent.get("historical_decision") if top_precedent else None,
            telemetry={
                "precedents_scanned": 5565,
                "top_precedent_case_id": top_precedent.get("case_id") if top_precedent else None,
                "recurring_entities_count": len(registry_matches)
            }
        )
