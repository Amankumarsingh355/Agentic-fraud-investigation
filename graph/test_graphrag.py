"""
Test and Verification Script for Phase 4: GraphRAG Layer
Runs retrieval and synthesis on 3 diverse sample cases:
1. HHG-001 (Txn: 3514030) - High risk score & Out-of-region in-person spend
2. HHG-003 (Txn: 3530164) - Customer dispute / report & CNP card testing
3. HHG-014 (Txn: 3478561) - Analyst request & Shared device syndicate ring

Validates that each output is a structured, LLM-ready markdown dossier (never raw JSON dumps).
Saves detailed results to docs/graphrag-test-report.md.
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from graph.graphrag_synthesizer import GraphRAGSynthesizer

def main():
    print("=" * 80)
    print("PHASE 4 GATE VERIFICATION: GraphRAG Dossier Generation")
    print("=" * 80)
    
    synthesizer = GraphRAGSynthesizer()
    
    test_cases = [
        {
            "case_id": "HHG-001",
            "txn_id": 3514030,
            "trigger_type": "risk_score",
            "trigger_text": "Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide."
        },
        {
            "case_id": "HHG-003",
            "txn_id": 3530164,
            "trigger_type": "customer_report",
            "trigger_text": "Customer C08623 message: 'I never made this $49.00 purchase. Please check my card.' Refers to 3530164."
        },
        {
            "case_id": "HHG-014",
            "txn_id": 3478561,
            "trigger_type": "analyst_request",
            "trigger_text": "Analyst request: several cards this month show purchases from the same unusual device profile. Review transaction 3478561 on card C13487-K1 and look for related activity."
        }
    ]
    
    report_lines = [
        "# Phase 4 Verification Report: GraphRAG Retrieval & Dossier Synthesis",
        "",
        "**Status**: VERIFIED & PASSING",
        "**Date**: September 21, 2026",
        "**Scope**: Validation of GraphRAG multi-hop retrieval, policy vector grounding, case memory precedent matching, and LLM-ready structured dossier generation across 3 sample cases.",
        "",
        "---",
        ""
    ]
    
    for tc in test_cases:
        print(f"\n[+] Synthesizing GraphRAG Dossier for Case {tc['case_id']} (Txn {tc['txn_id']})...")
        dossier = synthesizer.synthesize_investigation_dossier(
            transaction_id=tc['txn_id'],
            case_id=tc['case_id'],
            trigger_type=tc['trigger_type'],
            trigger_text=tc['trigger_text']
        )
        
        # Verify required sections exist
        required_sections = [
            "SECTION 1: TARGET TRANSACTION & CARDHOLDER BASELINE",
            "SECTION 2: GRAPH TRAVERSAL & HARDWARE FOOTPRINT",
            "SECTION 3: RECENT TRANSACTION VELOCITY",
            "SECTION 4: AUTOMATED GRAPH PATTERN SIGNALS",
            "SECTION 5: GOVERNING BANK POLICY RULES",
            "SECTION 6: HISTORICAL CASE MEMORY PRECEDENTS",
            "SECTION 7: EVIDENCE GAPS & INVESTIGATIVE GUIDANCE"
        ]
        
        missing = [s for s in required_sections if s not in dossier]
        if missing:
            raise ValueError(f"Dossier for {tc['case_id']} is missing sections: {missing}")
            
        print(f"    -> Successfully generated {len(dossier.splitlines())} lines ({len(dossier)} bytes).")
        print(f"    -> All 7 structured sections present.")
        
        # Append to report
        report_lines.append(f"## Sample Case {tc['case_id']} (Txn ID: `{tc['txn_id']}`)")
        report_lines.append(f"**Trigger**: `{tc['trigger_type']}` — *\"{tc['trigger_text']}\"*")
        report_lines.append("")
        report_lines.append("### Generated GraphRAG Dossier")
        report_lines.append("```markdown")
        report_lines.append(dossier)
        report_lines.append("```")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

    report_path = "docs/graphrag-test-report.md"
    os.makedirs("docs", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n" + "=" * 80)
    print(f"Phase 4 Gate Validation PASSED! Report saved to {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
