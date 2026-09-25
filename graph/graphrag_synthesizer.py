"""
GraphRAG Evidence Synthesis Engine
Combines multi-hop graph subgraphs + semantic policy/typology vector search + case memory
Formats structured, LLM-ready investigative dossiers and machine-readable context objects.
Zero fabricated evidence, strictly grounded in dataset and official policy documents.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))
from graph.subgraph_extractor import SubgraphExtractor
from graph.similar_cases_engine import SimilarCasesEngine
from graph.load_vector_store import VectorRetriever


class GraphRAGSynthesizer:
    def __init__(self, extractor=None, similar_engine=None, vector_retriever=None):
        self.extractor = extractor or SubgraphExtractor()
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.similar_engine = similar_engine or SimilarCasesEngine(retriever=self.vector_retriever)

    def synthesize_graphrag_context(
        self,
        transaction_id: int,
        case_id: str = "CASE-AUTO",
        trigger_type: str = "risk_score",
        trigger_text: str = ""
    ) -> Dict[str, Any]:
        """
        Builds a unified, comprehensive GraphRAG context object combining:
        - graph_evidence: multi-hop subgraphs, shared hardware rings, 72h timeline
        - document_evidence: FinCEN/FATF/FFIEC regulatory guidance
        - policy_evidence: exact retrieved rules (R1 to R10)
        - typology_evidence: pattern classification signals
        - historical_case_evidence: top matching closed cases
        - transaction_evidence: target parameters and baseline
        - risk_signals: base, corroborating, and mitigating signals
        - missing_evidence: explicit evidence gaps
        """
        subgraph = self.extractor.extract_subgraph(transaction_id)
        if not subgraph:
            return {"error": f"Transaction {transaction_id} not found in graph."}

        target = subgraph["target_transaction"]
        cust = subgraph["customer_profile"]
        timeline = subgraph.get("card_timeline_72h", [])
        device = subgraph.get("identity_device")
        rings = subgraph.get("shared_hardware_ring", {})
        patterns = subgraph.get("pattern_signals", {})

        # 1. Determine primary pattern
        primary_pattern = "none"
        if patterns.get("card_testing", {}).get("flagged"):
            primary_pattern = "card_testing"
        elif patterns.get("out_of_region", {}).get("flagged"):
            primary_pattern = "out_of_region_use"
        elif patterns.get("cnp_new_device", {}).get("flagged"):
            primary_pattern = "card_not_present_new_device"
        elif patterns.get("account_takeover", {}).get("flagged"):
            primary_pattern = "account_takeover"
        elif patterns.get("card_not_present", {}).get("flagged"):
            primary_pattern = "card_not_present_fraud"

        # 2. Retrieve relevant policy rules (Rules R1 - R10)
        policy_query = f"{primary_pattern} {trigger_type} approval route verify block card customer confirm deny"
        policy_hits = self.vector_retriever.search(policy_query, top_k=3, doc_type="policy_rule")

        # 3. Retrieve regulatory standards (FinCEN, FATF, FFIEC)
        reg_hits = self.vector_retriever.search(f"{primary_pattern} SAR filing narrative red flags", top_k=2, doc_type="regulatory_guidance")

        # 4. Retrieve fraud typologies documentation
        typology_hits = self.vector_retriever.search(f"{primary_pattern} detection indicators", top_k=1, doc_type="fraud_typology")

        # 5. Retrieve similar prior cases from memory
        memory_hits = self.similar_engine.find_similar_cases(
            query_text=f"{trigger_text} {primary_pattern} amount ${target['amount']}",
            target_pattern=primary_pattern if primary_pattern != "none" else None,
            target_exposure=target["amount"],
            target_customer=str(cust.get("customer_id", "")),
            top_k=3
        )

        # 6. Decompose Risk Signals
        base_signals = []
        if trigger_type == "customer_report":
            base_signals.append({"signal": "Customer Direct Report", "weight": 0.45, "detail": trigger_text})
        elif trigger_type == "analyst_request":
            base_signals.append({"signal": "Analyst Flagged Investigation", "weight": 0.30, "detail": trigger_text})
        elif target.get("risk_score") is not None:
            base_signals.append({"signal": f"Model Risk Score ({target['risk_score']:.2f})", "weight": round(target['risk_score'] - 0.20, 2), "detail": "Bank real-time ML detector"})

        corroborating = []
        if rings.get("has_shared_ring"):
            corroborating.append({
                "signal": f"Shared Syndicate Hardware Ring ({rings.get('ring_size', 1)} accounts)",
                "detail": f"Hardware profile shared across accounts: {rings.get('connected_customers')}"
            })
        if device and device.get("is_new"):
            corroborating.append({"signal": "Unfamiliar Hardware Profile (id_15=New)", "detail": device.get("device_profile")})
        if device and "ANONYMOUS" in str(device.get("proxy_status", "")):
            corroborating.append({"signal": "Anonymous Proxy / VPN Detected", "detail": device.get("proxy_status")})
        if patterns.get("card_testing", {}).get("flagged"):
            corroborating.append({"signal": "Card Testing Authorization Sequence (R5)", "detail": f"{patterns['card_testing'].get('micro_count')} micro auths"})
        if patterns.get("out_of_region", {}).get("flagged"):
            corroborating.append({"signal": f"Out-of-Region POS (Region {target.get('addr1')} vs Home {cust.get('home_region')})", "detail": "In-person physical swipe"})

        mitigating = []
        if cust.get("total_historical_txns", 0) > 50:
            mitigating.append({"signal": f"Established Account History ({cust.get('total_historical_txns')} txns)", "detail": f"Volume ${cust.get('total_historical_volume', 0):,.2f}"})
        if target.get("channel") == "in_person" and not patterns.get("out_of_region", {}).get("flagged"):
            mitigating.append({"signal": "Home Billing Region Alignment", "detail": f"Region {target.get('addr1')} matches home profile"})

        missing_evidence = []
        if patterns.get("out_of_region", {}).get("flagged") and not rings.get("has_shared_ring"):
            missing_evidence.append("Verification whether out-of-region POS charge is legitimate travel vs card cloning (Rule R1)")
        if trigger_type == "risk_score" and len(corroborating) == 0:
            missing_evidence.append("Corroborating graph or identity signals for standalone risk score (Rule R1)")
        if target.get("amount", 0) > 500 and len(corroborating) < 2:
            missing_evidence.append("Customer confirmation or second factor authentication for high value charge (Rule R8)")

        return {
            "case_id": case_id,
            "transaction_id": transaction_id,
            "trigger_type": trigger_type,
            "trigger_text": trigger_text,
            "graph_evidence": {
                "target_transaction": target,
                "customer_profile": cust,
                "identity_device": device,
                "shared_hardware_ring": rings,
                "card_timeline_72h": timeline,
                "hops_summary": f"Multi-hop graph neighborhood for customer {cust.get('customer_id')} across card {target.get('card_id')}"
            },
            "document_evidence": reg_hits,
            "policy_evidence": policy_hits,
            "typology_evidence": typology_hits,
            "historical_case_evidence": memory_hits,
            "transaction_evidence": {
                "amount_usd": target.get("amount", 0.0),
                "channel": target.get("channel", "online"),
                "product_cd": target.get("product_cd"),
                "billing_region": target.get("addr1"),
                "billing_country": target.get("addr2"),
                "ts": target.get("ts"),
                "initial_model_score": target.get("risk_score")
            },
            "risk_signals": {
                "primary_pattern": primary_pattern,
                "base_signals": base_signals,
                "corroborating_signals": corroborating,
                "mitigating_signals": mitigating
            },
            "missing_evidence": missing_evidence
        }

    def synthesize_investigation_dossier(
        self,
        transaction_id: int,
        case_id: str = "CASE-AUTO",
        trigger_type: str = "risk_score",
        trigger_text: str = ""
    ) -> str:
        """
        Synthesizes a structured, highly grounded markdown investigative dossier for LLM consumption.
        """
        ctx = self.synthesize_graphrag_context(
            transaction_id=transaction_id,
            case_id=case_id,
            trigger_type=trigger_type,
            trigger_text=trigger_text
        )
        if "error" in ctx:
            return ctx["error"]

        target = ctx["graph_evidence"]["target_transaction"]
        cust = ctx["graph_evidence"]["customer_profile"]
        timeline = ctx["graph_evidence"]["card_timeline_72h"]
        device = ctx["graph_evidence"]["identity_device"]
        rings = ctx["graph_evidence"]["shared_hardware_ring"]
        primary_pattern = ctx["risk_signals"]["primary_pattern"]

        lines = []
        lines.append(f"# FRAUD INVESTIGATION DOSSIER: {case_id}")
        lines.append(f"**Target Transaction**: `{transaction_id}` | **Trigger Type**: `{trigger_type}`")
        if trigger_text:
            lines.append(f"**Trigger Detail**: \"{trigger_text}\"\n")

        lines.append("## SECTION 1: TARGET TRANSACTION & CARDHOLDER BASELINE")
        lines.append(f"- **Customer**: `{cust.get('customer_id')}` (Tenure: {str(cust.get('first_seen', ''))[:10]} to {str(cust.get('last_seen', ''))[:10]}, {cust.get('total_historical_txns', 0)} historical txns, ${cust.get('total_historical_volume', 0.0):,.2f} total volume)")
        lines.append(f"- **Primary Card**: `{target.get('card_id')}` (Network: `{target.get('card_network')}`, Type: `{target.get('card_type')}`)")
        lines.append(f"- **Flagged Spend**: **${target.get('amount', 0.0):.2f} USD** at `{target.get('ts')}`")
        lines.append(f"- **Channel / Product**: `{target.get('channel')}` (ProductCD: `{target.get('product_cd')}`)")
        lines.append(f"- **Bank Model Risk Score**: `{target.get('risk_score') if target.get('risk_score') is not None else 'N/A'}` (Input signal only, not a verdict)")
        lines.append(f"- **Geographic Billing**: Region `{target.get('addr1')}` (Country `{target.get('addr2')}` | Established Home Region: `{cust.get('home_region')}`)\n")

        lines.append("## SECTION 2: GRAPH TRAVERSAL & HARDWARE FOOTPRINT")
        if device:
            lines.append(f"- **Channel**: Online authenticated session")
            lines.append(f"- **Device Profile**: `{device.get('device_profile')}`")
            lines.append(f"- **Device Status**: `{'NEW to account (id_15=New)' if device.get('is_new') else 'RECURRING/FOUND (id_15=Found)'}`")
            lines.append(f"- **Proxy Status**: `{device.get('proxy_status')}`")
        else:
            lines.append(f"- **Channel**: Physical in-person point of sale (Product code W). Zero digital identity footprint recorded.")

        if rings.get("has_shared_ring"):
            lines.append(f"- **SYNDICATE ALERT (Rule R6)**: Hardware profile is SHARED across {rings.get('ring_size')} distinct accounts: {rings.get('connected_customers')}")
        else:
            lines.append(f"- **Device Linkage**: Device is isolated to this customer profile (0 shared card rings discovered).\n")

        lines.append("## SECTION 3: RECENT TRANSACTION VELOCITY (72-HOUR TIMELINE)")
        if len(timeline) <= 1:
            lines.append("- Isolated transaction. No prior transactions on this card in the last 72 hours.")
        else:
            lines.append(f"- Recorded {len(timeline)} transactions on this card within 72 hours:")
            for t in timeline:
                flag_marker = " [TARGET ALERT]" if t.get('txn_id') == transaction_id else ""
                lines.append(f"  * Txn `{t.get('txn_id')}`: ${t.get('amount', 0.0):.2f} ({t.get('channel')}, Product {t.get('product_cd')}) at {t.get('ts')} (delta: +{t.get('delta_s', 0):.0f}s, Risk: {t.get('risk_score')}){flag_marker}")
        lines.append("")

        lines.append("## SECTION 4: AUTOMATED GRAPH PATTERN SIGNALS")
        lines.append(f"- **Detected Pattern**: `{primary_pattern}`")
        for sig in ctx["risk_signals"]["corroborating_signals"]:
            lines.append(f"- **Corroborating Signal**: {sig['signal']} — {sig['detail']}")
        for sig in ctx["risk_signals"]["mitigating_signals"]:
            lines.append(f"- **Mitigating Signal**: {sig['signal']} — {sig['detail']}")
        lines.append("")

        lines.append("## SECTION 5: GOVERNING BANK POLICY RULES (Bank Fraud Policy v1.0)")
        for ph in ctx["policy_evidence"]:
            lines.append(f"- **{ph['title']}** (Relevance: {ph['score']}):")
            lines.append(f"  {ph['content_snippet'][:200]}...")
        lines.append("")

        lines.append("## SECTION 6: HISTORICAL CASE MEMORY PRECEDENTS")
        if ctx["historical_case_evidence"]:
            for mh in ctx["historical_case_evidence"]:
                lines.append(f"- **Case {mh['case_id']}** (Outcome: `{mh['outcome']}`, Pattern: `{mh['pattern']}`, Exposure: ${mh['exposure_usd']:,.2f}, Hybrid Score: {mh.get('hybrid_score', mh.get('similarity_score', 0))}):")
                lines.append(f"  \"{mh['notes_snippet'][:220]}...\"")
        else:
            lines.append("- No direct high-similarity closed cases retrieved.")
        lines.append("")

        lines.append("## SECTION 7: EVIDENCE GAPS & INVESTIGATIVE GUIDANCE")
        if ctx["missing_evidence"]:
            for gap in ctx["missing_evidence"]:
                lines.append(f"- **Evidence Gap**: {gap}")
        else:
            lines.append("- Sufficient corroborated graph and behavioral evidence established.")

        return "\n".join(lines)


if __name__ == "__main__":
    synthesizer = GraphRAGSynthesizer()
    ctx = synthesizer.synthesize_graphrag_context(
        transaction_id=3514030,
        case_id="HHG-001",
        trigger_type="risk_score",
        trigger_text="Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide."
    )
    print("\n--- SYNTHESIZED GRAPHRAG CONTEXT KEYS ---")
    print(list(ctx.keys()))
    print(f"Policy hits: {len(ctx['policy_evidence'])}")
    print(f"Document hits: {len(ctx['document_evidence'])}")
    print(f"Memory hits: {len(ctx['historical_case_evidence'])}")
    print(f"Missing evidence: {ctx['missing_evidence']}")
