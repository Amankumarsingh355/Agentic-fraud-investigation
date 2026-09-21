"""
Autonomous Fraud Investigation Agent
Implements the end-to-end stateful investigation loop:
Trigger -> Investigate -> Gather Evidence -> Assess Uncertainty -> Gather More Evidence -> Take Next Actions -> Explain Decision -> Update Case Memory
Strictly enforces policy gating and inspectable confidence logic.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from agent.case import Case
from agent.uncertainty_engine import UncertaintyEngine
from agent.policy_engine import PolicyEngine
from agent.action_executor import ActionExecutor
from graph.subgraph_extractor import SubgraphExtractor
from graph.similar_cases_engine import SimilarCasesEngine
from graph.load_vector_store import VectorRetriever
from graph.graphrag_synthesizer import GraphRAGSynthesizer

class FraudInvestigationAgent:
    def __init__(self):
        print("Initializing FraudInvestigationAgent...")
        self.extractor = SubgraphExtractor()
        self.uncertainty_engine = UncertaintyEngine()
        self.policy_engine = PolicyEngine()
        self.action_executor = ActionExecutor()
        self.similar_engine = SimilarCasesEngine()
        self.vector_retriever = VectorRetriever()
        self.synthesizer = GraphRAGSynthesizer()
        print("FraudInvestigationAgent ready.")

    def run_investigation(
        self,
        trigger_type: str,
        trigger_text: str,
        flagged_txn_id: int,
        case_id: Optional[str] = None,
        simulated_customer_response: Optional[str] = None # None, "confirmed_authorized", "denied_fraud", "unresponsive"
    ) -> Case:
        """
        Executes the complete 8-stage fraud investigation loop end-to-end.
        """
        if not case_id:
            case_id = f"CASE-{flagged_txn_id}"

        # -------------------------------------------------------------
        # STAGE 1: TRIGGER HANDLER
        # -------------------------------------------------------------
        subgraph = self.extractor.extract_subgraph(flagged_txn_id)
        if not subgraph:
            raise ValueError(f"TransactionID {flagged_txn_id} not found in graph database.")
            
        target = subgraph["target_transaction"]
        cust_id = target["customer_id"]
        card_id = target["card_id"]
        risk_score = target.get("risk_score")
        
        case = Case(
            case_id=case_id,
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn_id,
            card_id=card_id,
            customer_id=cust_id,
            risk_score=risk_score
        )
        
        # -------------------------------------------------------------
        # STAGE 2: INVESTIGATE (MULTI-HOP GRAPH TRAVERSAL)
        # -------------------------------------------------------------
        case.set_status("INVESTIGATING", reason="Initiated graph traversal and entity resolution.")
        
        # Record baseline evidence
        case.add_evidence(
            evidence_type="customer_baseline",
            source="TigerGraph / Customer",
            title=f"Cardholder Profile for {cust_id}",
            details=subgraph["customer_profile"]
        )
        
        case.add_evidence(
            evidence_type="target_transaction",
            source="TigerGraph / Transaction",
            title=f"Flagged Transaction {flagged_txn_id} ($ {target['amount']:.2f})",
            details=target,
            score=risk_score
        )
        
        case.add_evidence(
            evidence_type="velocity_timeline",
            source="TigerGraph / Card History",
            title=f"Rolling 72-Hour Timeline ({len(subgraph['card_timeline_72h'])} events)",
            details=subgraph["card_timeline_72h"]
        )
        
        if subgraph.get("identity_device"):
            case.add_evidence(
                evidence_type="hardware_profile",
                source="TigerGraph / Device",
                title=f"Device Fingerprint: {subgraph['identity_device'].get('device_profile')}",
                details=subgraph["identity_device"]
            )

        # -------------------------------------------------------------
        # STAGE 3: GATHER EVIDENCE (PATTERNS, RINGS, POLICIES, MEMORY)
        # -------------------------------------------------------------
        case.set_status("GATHER_EVIDENCE", reason="Extracting pattern typologies, syndicate rings, and precedents.")
        
        patterns = subgraph["pattern_signals"]
        case.add_evidence(
            evidence_type="pattern_signals",
            source="Pattern Engine",
            title="Typology Pattern Recognition Checks",
            details=patterns
        )
        
        rings = subgraph["shared_hardware_ring"]
        case.add_evidence(
            evidence_type="hardware_rings",
            source="Graph Ring Algorithms",
            title="Shared Hardware Syndicate Ring Discovery",
            details=rings
        )
        
        # Record findings
        if patterns["card_testing"]["flagged"]:
            case.add_finding(
                finding_type="CARD_TESTING",
                description=f"Rapid micro-authorizations under $10 detected prior to larger charge.",
                severity="HIGH",
                graph_proof=patterns["card_testing"]
            )
        if patterns["out_of_region"]["flagged"]:
            case.add_finding(
                finding_type="OUT_OF_REGION",
                description=f"In-person POS activity in region {patterns['out_of_region']['current_region']} differing from home region {patterns['out_of_region']['home_region']}.",
                severity="MEDIUM",
                graph_proof=patterns["out_of_region"]
            )
        if rings["has_shared_ring"]:
            case.add_finding(
                finding_type="SYNDICATE_RING",
                description=f"Hardware profile shared across {rings['ring_size']} separate customer accounts: {rings['connected_customers']}.",
                severity="CRITICAL",
                graph_proof=rings
            )

        # Retrieve relevant policies & precedents
        policy_hits = self.vector_retriever.search(f"{trigger_type} {target['amount']} block verify card", top_k=2)
        for ph in policy_hits:
            case.add_evidence(
                evidence_type="policy_citation",
                source="Bank Fraud Policy Store",
                title=ph["title"],
                details=ph["content_snippet"],
                score=ph["score"]
            )
            
        memory_hits = self.similar_engine.find_similar_cases(
            query_text=f"{trigger_text} amount ${target['amount']}",
            target_exposure=target["amount"],
            top_k=2
        )
        for mh in memory_hits:
            case.add_evidence(
                evidence_type="case_precedent",
                source="TigerGraph Case Memory (Historical)",
                title=f"Precedent Case {mh['case_id']} ({mh['outcome']})",
                details=mh["notes_snippet"],
                score=mh["hybrid_score"]
            )

        # -------------------------------------------------------------
        # STAGE 4: ASSESS UNCERTAINTY (INITIAL)
        # -------------------------------------------------------------
        init_assessment = self.uncertainty_engine.assess(
            subgraph=subgraph,
            trigger_type=trigger_type,
            trigger_risk_score=risk_score,
            customer_verification_status="pending"
        )
        case.update_risk_assessment(
            fraud_probability=init_assessment["fraud_probability"],
            uncertainty_score=init_assessment["uncertainty_score"],
            confidence_level=init_assessment["confidence_level"],
            has_sufficient_evidence=init_assessment["has_sufficient_evidence"],
            criteria_breakdown=init_assessment["criteria_breakdown"],
            evidence_gaps=init_assessment["evidence_gaps"]
        )

        # -------------------------------------------------------------
        # STAGE 5: GATHER MORE EVIDENCE IF NEEDED
        # -------------------------------------------------------------
        final_assessment = init_assessment
        cust_status = "pending"
        
        if not init_assessment["has_sufficient_evidence"]:
            case.set_status("EVIDENCE_PENDING", reason="Uncertainty exceeds threshold; initiating controlled evidence gathering.")
            
            # Dispatch autonomous verification request to cardholder
            case.add_audit_event(
                stage="GATHER_MORE_EVIDENCE",
                event_type="DISPATCH_CUSTOMER_VERIFICATION",
                description="Triggered autonomous VERIFY_WITH_CUSTOMER (Rule R1: Verify Before You Block).",
                actor="AGENT_CORE"
            )
            
            # If a simulated customer response is provided, process it
            if simulated_customer_response:
                cust_status = simulated_customer_response
                case.add_evidence(
                    evidence_type="customer_verification_response",
                    source="Cardholder SMS/Push Channel",
                    title=f"Customer Verification Response: {cust_status}",
                    details={"status": cust_status, "response_received_at": datetime.now().isoformat()}
                )
                
                # Re-assess uncertainty with new ground-truth evidence
                final_assessment = self.uncertainty_engine.assess(
                    subgraph=subgraph,
                    trigger_type=trigger_type,
                    trigger_risk_score=risk_score,
                    customer_verification_status=cust_status
                )
                case.update_risk_assessment(
                    fraud_probability=final_assessment["fraud_probability"],
                    uncertainty_score=final_assessment["uncertainty_score"],
                    confidence_level=final_assessment["confidence_level"],
                    has_sufficient_evidence=final_assessment["has_sufficient_evidence"],
                    criteria_breakdown=final_assessment["criteria_breakdown"],
                    evidence_gaps=final_assessment["evidence_gaps"]
                )

        # -------------------------------------------------------------
        # STAGE 6: RECOMMEND & TAKE ACTIONS (POLICY GATING)
        # -------------------------------------------------------------
        case.set_status("RECOMMENDING_ACTIONS", reason="Evaluating policy rules and assigning authority routes.")
        
        recommended_actions = self.policy_engine.evaluate_actions(
            subgraph=subgraph,
            risk_assessment=final_assessment,
            customer_verification_status=cust_status,
            trigger_type=trigger_type
        )
        
        for act in recommended_actions:
            dispatch_res = self.action_executor.dispatch_action(
                action_name=act["action"],
                route=act["route"],
                case_id=case.case_id,
                customer_id=cust_id,
                card_id=card_id,
                txn_id=flagged_txn_id,
                amount=target["amount"],
                reason=act["reason"],
                policy_rule=act["policy_rule"],
                simulate_human_signoff=False # Strictly test policy gating
            )
            case.record_action(
                action_name=act["action"],
                route=act["route"],
                status=dispatch_res["status"],
                reason=act["reason"],
                policy_rule=act["policy_rule"],
                side_effects=dispatch_res["side_effects"]
            )

        # -------------------------------------------------------------
        # STAGE 7: EXPLAIN THE DECISION
        # -------------------------------------------------------------
        case.set_status("EXPLAINING_DECISION", reason="Generating comprehensive policy-grounded rationale.")
        explanation = self._generate_explanation(case, subgraph, final_assessment)
        case.set_explanation(explanation)

        # -------------------------------------------------------------
        # STAGE 8: UPDATE CASE MEMORY
        # -------------------------------------------------------------
        if any(a["status"] == "PENDING_HUMAN_APPROVAL" for a in case.actions):
            case.set_status("RESOLVED", reason="Investigation completed. Pending human authority sign-off on staged actions.")
        elif cust_status == "confirmed_authorized":
            case.set_status("CLOSED", reason="Investigation closed as cleared/no fraud upon cardholder verification.")
        else:
            case.set_status("RESOLVED", reason="Investigation completed and policy actions executed.")
            
        case.add_audit_event(
            stage="UPDATE_CASE_MEMORY",
            event_type="CASE_PERSISTED",
            description=f"Case {case.case_id} state committed to memory (Namespace: case_memory).",
            actor="CASE_MEMORY_MANAGER"
        )
        
        return case

    def _generate_explanation(self, case: Case, subgraph: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """Generates a transparent, auditable natural language explanation."""
        target = subgraph["target_transaction"]
        cust = subgraph["customer_profile"]
        rings = subgraph["shared_hardware_ring"]
        
        lines = []
        lines.append(f"### Investigation Summary for Case {case.case_id}")
        lines.append(f"**Transaction**: `{case.trigger['flagged_txn_id']}` | **Amount**: `${target['amount']:.2f}` | **Trigger**: `{case.trigger['type']}`")
        lines.append("")
        lines.append(f"**Assessed Fraud Probability**: `{assessment['fraud_probability']:.2f}` | **Confidence**: `{assessment['confidence_level']}` (Uncertainty: `{assessment['uncertainty_score']:.2f}`)")
        lines.append("")
        lines.append("#### Traceable Evidence & Reasoning")
        for sig in assessment["criteria_breakdown"]["base_signals"]:
            lines.append(f"- **Trigger Prior**: {sig['signal']} ({sig['delta']:+.2f}): {sig['detail']}")
        for sig in assessment["criteria_breakdown"]["corroborating_signals"]:
            lines.append(f"- **Corroborating Signal**: {sig['signal']} ({sig['delta']:+.2f}): {sig['detail']}")
        for sig in assessment["criteria_breakdown"]["mitigating_signals"]:
            lines.append(f"- **Mitigating Signal**: {sig['signal']} ({sig['delta']:+.2f}): {sig['detail']}")
            
        if assessment["evidence_gaps"]:
            lines.append("")
            lines.append("#### Identified Evidence Gaps")
            for gap in assessment["evidence_gaps"]:
                lines.append(f"- *Gap*: {gap}")
                
        lines.append("")
        lines.append("#### Policy Gated Actions & Next Steps")
        for act in case.actions:
            lines.append(f"- **{act['action_name']}** (`{act['route']}` - {act['status']}): {act['reason']} (Governing: *{act['policy_rule']}*)")
            
        return "\n".join(lines)
