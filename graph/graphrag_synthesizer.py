"""
GraphRAG Evidence Synthesis Engine
Combines multi-hop graph subgraphs + semantic policy/typology vector search + case memory
Formats structured, LLM-ready investigative dossiers (never raw JSON dumps)
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))
from graph.subgraph_extractor import SubgraphExtractor
from graph.similar_cases_engine import SimilarCasesEngine
from graph.load_vector_store import VectorRetriever

class GraphRAGSynthesizer:
    def __init__(self):
        print("Initializing GraphRAGSynthesizer...")
        self.extractor = SubgraphExtractor()
        self.similar_engine = SimilarCasesEngine()
        self.vector_retriever = VectorRetriever()
        print("GraphRAGSynthesizer ready.")
        
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
        subgraph = self.extractor.extract_subgraph(transaction_id)
        if not subgraph:
            return f"Error: Transaction {transaction_id} not found in graph."
            
        target = subgraph["target_transaction"]
        cust = subgraph["customer_profile"]
        timeline = subgraph["card_timeline_72h"]
        device = subgraph["identity_device"]
        rings = subgraph["shared_hardware_ring"]
        patterns = subgraph["pattern_signals"]
        
        # 1. Determine most prominent pattern signal
        primary_pattern = "none"
        if patterns["card_testing"]["flagged"]:
            primary_pattern = "card_testing"
        elif patterns["out_of_region"]["flagged"]:
            primary_pattern = "out_of_region_use"
        elif patterns["cnp_new_device"]["flagged"]:
            primary_pattern = "card_not_present_new_device"
        elif patterns["account_takeover"]["flagged"]:
            primary_pattern = "account_takeover"
        elif patterns["card_not_present"]["flagged"]:
            primary_pattern = "card_not_present_fraud"
            
        # 2. Retrieve relevant policy rules
        policy_query = f"{primary_pattern} {trigger_type} approval route verify block card"
        policy_hits = self.vector_retriever.search(policy_query, top_k=2, doc_type="policy_rule")
        
        # 3. Retrieve similar prior cases from memory
        memory_hits = self.similar_engine.find_similar_cases(
            query_text=f"{trigger_text} {primary_pattern} amount ${target['amount']}",
            target_pattern=primary_pattern if primary_pattern != "none" else None,
            target_exposure=target['amount'],
            top_k=2
        )
        
        # 4. Construct Structured LLM-Ready Markdown Dossier
        lines = []
        lines.append(f"# FRAUD INVESTIGATION DOSSIER: {case_id}")
        lines.append(f"**Target Transaction**: `{transaction_id}` | **Trigger Type**: `{trigger_type}`")
        if trigger_text:
            lines.append(f"**Trigger Detail**: \"{trigger_text}\"\n")
            
        lines.append("## SECTION 1: TARGET TRANSACTION & CARDHOLDER BASELINE")
        lines.append(f"- **Customer**: `{cust['customer_id']}` (Tenure: {cust['first_seen'][:10]} to {cust['last_seen'][:10]}, {cust['total_historical_txns']} historical txns, ${cust['total_historical_volume']:,.2f} total volume)")
        lines.append(f"- **Primary Card**: `{target['card_id']}` (Network: `{target['card_network']}`, Type: `{target['card_type']}`)")
        lines.append(f"- **Flagged Spend**: **${target['amount']:.2f} USD** at `{target['ts']}`")
        lines.append(f"- **Channel / Product**: `{target['channel']}` (ProductCD: `{target['product_cd']}`)")
        lines.append(f"- **Bank Model Risk Score**: `{target['risk_score'] if target['risk_score'] is not None else 'N/A'}` (Input signal only, not a verdict)")
        lines.append(f"- **Geographic Billing**: Region `{target['addr1']}` (Country `{target['addr2']}` | Established Home Region: `{cust['home_region']}`)\n")
        
        lines.append("## SECTION 2: GRAPH TRAVERSAL & HARDWARE FOOTPRINT")
        if device:
            lines.append(f"- **Channel**: Online authenticated session")
            lines.append(f"- **Device Profile**: `{device['device_profile']}`")
            lines.append(f"- **Device Status**: `{'NEW to account (id_15=New)' if device['is_new'] else 'RECURRING/FOUND (id_15=Found)'}`")
            lines.append(f"- **Proxy Status**: `{device['proxy_status']}`")
        else:
            lines.append(f"- **Channel**: Physical in-person point of sale (Product code W). Zero digital identity footprint recorded.")
            
        if rings["has_shared_ring"]:
            lines.append(f"- **SYNDICATE ALERT (Rule R6)**: Hardware profile is SHARED across {rings['ring_size']} distinct accounts: {rings['connected_customers']}")
        else:
            lines.append(f"- **Device Linkage**: Device is isolated to this customer profile (0 shared card rings discovered).\n")
            
        lines.append("## SECTION 3: RECENT TRANSACTION VELOCITY (72-HOUR TIMELINE)")
        if len(timeline) <= 1:
            lines.append("- Isolated transaction. No prior transactions on this card in the last 72 hours.")
        else:
            lines.append(f"- Recorded {len(timeline)} transactions on this card within 72 hours:")
            for t in timeline:
                flag_marker = " [TARGET ALERT]" if t['txn_id'] == transaction_id else ""
                lines.append(f"  * Txn `{t['txn_id']}`: ${t['amount']:.2f} ({t['channel']}, Product {t['product_cd']}) at {t['ts']} (delta: +{t['delta_s']:.0f}s, Risk: {t['risk_score']}){flag_marker}")
        lines.append("")
        
        lines.append("## SECTION 4: AUTOMATED GRAPH PATTERN SIGNALS")
        lines.append(f"- **Card Testing Indicator (R5)**: `{'FLAGGED' if patterns['card_testing']['flagged'] else 'NEGATIVE'}` ({patterns['card_testing']['micro_count']} micro-auths under $10, {patterns['card_testing']['large_count']} large auths)")
        lines.append(f"- **Card-Not-Present Burst**: `{'FLAGGED' if patterns['card_not_present']['flagged'] else 'NEGATIVE'}` ({patterns['card_not_present']['online_count']} online txns in window)")
        lines.append(f"- **CNP via New Device**: `{'FLAGGED' if patterns['cnp_new_device']['flagged'] else 'NEGATIVE'}`")
        lines.append(f"- **Out-of-Region Use**: `{'FLAGGED' if patterns['out_of_region']['flagged'] else 'NEGATIVE'}` (Current: {patterns['out_of_region']['current_region']} vs Home: {patterns['out_of_region']['home_region']})")
        lines.append(f"- **Account Takeover**: `{'FLAGGED' if patterns['account_takeover']['flagged'] else 'NEGATIVE'}`\n")
        
        lines.append("## SECTION 5: GOVERNING BANK POLICY RULES")
        for ph in policy_hits:
            lines.append(f"- **{ph['title']}** (Relevance: {ph['score']}):")
            lines.append(f"  {ph['content_snippet'][:200]}...")
        lines.append("")
        
        lines.append("## SECTION 6: HISTORICAL CASE MEMORY PRECEDENTS")
        if memory_hits:
            for mh in memory_hits:
                lines.append(f"- **Case {mh['case_id']}** (Outcome: `{mh['outcome']}`, Pattern: `{mh['pattern']}`, Exposure: ${mh['exposure_usd']:,.2f}, Hybrid Score: {mh['hybrid_score']}):")
                lines.append(f"  \"{mh['notes_snippet'][:220]}...\"")
        else:
            lines.append("- No direct high-similarity closed cases retrieved.")
        lines.append("")
        
        lines.append("## SECTION 7: EVIDENCE GAPS & INVESTIGATIVE GUIDANCE")
        if primary_pattern == "out_of_region_use":
            lines.append("- **Ambiguity**: Out-of-region in-person charge observed. Could represent legitimate travel or counterfeit clone.")
            lines.append("- **Mandatory Policy Rule R1**: If assessed fraud probability < 0.70 on single indicator, recommend `VERIFY_WITH_CUSTOMER` before any card block.")
        elif primary_pattern == "card_testing":
            lines.append("- **Policy Rule R5**: Testing sequence detected. Recommend `DECLINE_TRANSACTION` and `STEP_UP_AUTH`. If high-value purchase cleared, recommend `BLOCK_CARD`.")
        elif rings["has_shared_ring"]:
            lines.append("- **Policy Rule R6**: Shared origin syndicate detected across multiple cardholders. Mandatory `CREATE_CASE`, `FILE_REPORT`, and `MONITOR_CONNECTED_CARDS`.")
        else:
            lines.append("- **Policy Guidance**: Corroborate risk score with customer spending baseline and device trust before taking restrictive actions.")
            
        return "\n".join(lines)

if __name__ == "__main__":
    synthesizer = GraphRAGSynthesizer()
    dossier = synthesizer.synthesize_investigation_dossier(
        transaction_id=3514030,
        case_id="HHG-001",
        trigger_type="risk_score",
        trigger_text="Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide."
    )
    print("\n" + "="*80)
    print("SAMPLE SYNTHESIZED GRAPH-RAG DOSSIER")
    print("="*80)
    print(dossier[:1500] + "\n...[truncated for preview]...")
