"""
Autonomous Fraud Investigation Agent
Implements the end-to-end stateful investigation loop:
Trigger -> Investigate -> Gather Evidence -> Assess Uncertainty -> Gather More Evidence -> Take Next Actions -> Explain Decision -> Update Case Memory
Strictly enforces policy gating, inspectable confidence logic, and dynamic case memory feedback.
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
from graph.case_memory import CaseMemoryManager
from graph.pattern_registry import PatternRegistry

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
        self.case_memory_manager = CaseMemoryManager()
        self.pattern_registry = PatternRegistry()
        print("FraudInvestigationAgent ready with Dynamic Case Memory & Pattern Registry.")

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
        
        device_profile_str = None
        proxy_status_str = None
        if subgraph.get("identity_device"):
            dev_obj = subgraph["identity_device"]
            device_profile_str = dev_obj.get("device_profile")
            proxy_status_str = dev_obj.get("proxy_status")
            case.add_evidence(
                evidence_type="hardware_profile",
                source="TigerGraph / Device",
                title=f"Device Fingerprint: {device_profile_str}",
                details=dev_obj
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
        
        # Check Pattern Registry for recurring entities from prior cases (Phase 6 feedback)
        registry_matches = self.pattern_registry.check_entity(
            device_profile=device_profile_str,
            proxy_status=proxy_status_str
        )
        for rm in registry_matches:
            case.add_finding(
                finding_type="RECURRING_FRAUD_ENTITY",
                description=f"Entity alert: {rm['risk_signal']} (Associated cases: {rm['associated_cases']}).",
                severity="CRITICAL",
                graph_proof=rm
            )
            case.add_evidence(
                evidence_type="recurring_entity_memory",
                source="Pattern Feedback Registry",
                title=f"Recurring Entity Matched Prior Case {rm['first_case_id']}",
                details=rm,
                score=0.95
            )
        
        # Determine dominant pattern
        dominant_pattern = "none"
        if patterns["card_testing"]["flagged"]:
            dominant_pattern = "card_testing"
            case.add_finding(
                finding_type="CARD_TESTING",
                description=f"Rapid micro-authorizations under $10 detected prior to larger charge.",
                severity="HIGH",
                graph_proof=patterns["card_testing"]
            )
        elif patterns["out_of_region"]["flagged"]:
            dominant_pattern = "out_of_region_use"
            case.add_finding(
                finding_type="OUT_OF_REGION",
                description=f"In-person POS activity in region {patterns['out_of_region']['current_region']} differing from home region {patterns['out_of_region']['home_region']}.",
                severity="MEDIUM",
                graph_proof=patterns["out_of_region"]
            )
        elif patterns["cnp_new_device"]["flagged"]:
            dominant_pattern = "card_not_present_new_device"
            case.add_finding(
                finding_type="CNP_NEW_DEVICE",
                description="Card-Not-Present transaction from newly authenticated hardware device.",
                severity="HIGH",
                graph_proof=patterns["cnp_new_device"]
            )
        elif patterns["account_takeover"]["flagged"]:
            dominant_pattern = "account_takeover"
            case.add_finding(
                finding_type="ACCOUNT_TAKEOVER",
                description="Cross-channel device shift and credential variance detected.",
                severity="CRITICAL",
                graph_proof=patterns["account_takeover"]
            )
            
        if rings["has_shared_ring"]:
            case.add_finding(
                finding_type="SYNDICATE_RING",
                description=f"Hardware profile shared across {rings['ring_size']} separate customer accounts: {rings['connected_customers']}.",
                severity="CRITICAL",
                graph_proof=rings
            )

        # Retrieve relevant policies & precedents
        policy_hits = self.vector_retriever.search(f"{trigger_type} {dominant_pattern} {target['amount']} block verify card", top_k=2)
        for ph in policy_hits:
            case.add_evidence(
                evidence_type="policy_citation",
                source="Bank Fraud Policy Store",
                title=ph["title"],
                details=ph["content_snippet"],
                score=ph["score"]
            )
            
        # Hybrid retrieval across static historical memory AND dynamic case memory
        memory_hits = self.similar_engine.find_similar_cases(
            query_text=f"{trigger_text} {dominant_pattern} amount ${target['amount']}",
            target_pattern=dominant_pattern if dominant_pattern != "none" else None,
            target_exposure=target["amount"],
            target_customer=cust_id,
            top_k=3
        )
        for mh in memory_hits:
            src = "TigerGraph Dynamic Case Memory" if mh.get("is_dynamic") else "TigerGraph Case Memory (Historical)"
            prefix = "[DYNAMIC MEMORY] " if mh.get("is_dynamic") else ""
            case.add_evidence(
                evidence_type="case_precedent",
                source=src,
                title=f"{prefix}Precedent Case {mh['case_id']} ({mh['outcome']}, {mh['pattern']})",
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
        
        # If recurring entity matched prior fraud case, boost corroboration
        if registry_matches:
            init_assessment["fraud_probability"] = min(0.98, init_assessment["fraud_probability"] + 0.35)
            init_assessment["has_sufficient_evidence"] = True
            init_assessment["criteria_breakdown"]["corroborating_signals"].append({
                "signal": "Recurring Entity Precedent Match",
                "delta": +0.35,
                "detail": f"Entity was previously confirmed fraudulent in case {registry_matches[0]['first_case_id']}."
            })
            
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
        # STAGE 8: UPDATE CASE MEMORY & PERSIST TO GRAPH
        # -------------------------------------------------------------
        if any(a["status"] == "PENDING_HUMAN_APPROVAL" for a in case.actions):
            case.set_status("RESOLVED", reason="Investigation completed. Pending human authority sign-off on staged actions.")
        elif cust_status == "confirmed_authorized":
            case.set_status("CLOSED", reason="Investigation closed as cleared/no fraud upon cardholder verification.")
        else:
            case.set_status("RESOLVED", reason="Investigation completed and policy actions executed.")
            
        # Persist to Dynamic Graph Memory
        persisted_record = self.case_memory_manager.persist_case(
            case_obj=case,
            subgraph=subgraph,
            is_benchmark=False
        )
        
        case.add_audit_event(
            stage="UPDATE_CASE_MEMORY",
            event_type="CASE_PERSISTED",
            description=f"Case {case.case_id} state and graph edges committed to memory (Namespace: case_memory).",
            actor="CASE_MEMORY_MANAGER"
        )
        
        return case

    def _generate_explanation(self, case: Case, subgraph: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """Generates a transparent, auditable natural language explanation citing precedents."""
        target = subgraph["target_transaction"]
        cust = subgraph["customer_profile"]
        
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
                
        # Cite Prior Precedents from Memory
        precedents = [e for e in case.evidence_list if e.get("type") in ["case_precedent", "recurring_entity_memory"]]
        if precedents:
            lines.append("")
            lines.append("#### Case Memory Precedents Informing Decision")
            for p in precedents:
                lines.append(f"- **{p['title']}** (Score: {p.get('score')} | Source: *{p.get('source')}*):")
                lines.append(f"  \"{str(p.get('details'))[:200]}...\"")
                
        lines.append("")
        lines.append("#### Policy Gated Actions & Next Steps")
        for act in case.actions:
            lines.append(f"- **{act['action_name']}** (`{act['route']}` - {act['status']}): {act['reason']} (Governing: *{act['policy_rule']}*)")
            
        return "\n".join(lines)
