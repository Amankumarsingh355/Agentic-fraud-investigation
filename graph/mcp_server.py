"""
TigerGraph Fraud Investigation MCP Server
Exposes Phase 3 (Graph Algorithms & Pattern Library) and Phase 4 (GraphRAG Layer)
as Model Context Protocol (MCP) tools for autonomous investigation agents.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from mcp.server.mcpserver import MCPServer

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from graph.subgraph_extractor import SubgraphExtractor
from graph.similar_cases_engine import SimilarCasesEngine
from graph.load_vector_store import VectorRetriever
from graph.graphrag_synthesizer import GraphRAGSynthesizer

# Initialize MCP Server instance
server = MCPServer(
    name="tigergraph-fraud-investigation-mcp",
    version="1.0.0"
)

# Shared singletons for fast tool execution
_extractor = None
_similar_engine = None
_vector_retriever = None
_synthesizer = None

def get_services():
    global _extractor, _similar_engine, _vector_retriever, _synthesizer
    if _extractor is None:
        _extractor = SubgraphExtractor()
    if _similar_engine is None:
        _similar_engine = SimilarCasesEngine()
    if _vector_retriever is None:
        _vector_retriever = VectorRetriever()
    if _synthesizer is None:
        _synthesizer = GraphRAGSynthesizer()
    return _extractor, _similar_engine, _vector_retriever, _synthesizer

@server.tool()
def get_transaction_subgraph(transaction_id: int) -> str:
    """
    Extract the multi-hop connected graph subgraph for a transaction.
    Traverses: Customer -> Cards -> Transactions (72h window) -> Device/Identity -> Geographic Region.
    
    Args:
        transaction_id: The integer TransactionID to investigate.
    """
    extractor, _, _, _ = get_services()
    subgraph = extractor.extract_subgraph(transaction_id)
    if not subgraph:
        return json.dumps({"error": f"Transaction {transaction_id} not found."})
    return json.dumps(subgraph, indent=2)

@server.tool()
def detect_fraud_patterns(transaction_id: int) -> str:
    """
    Execute pattern recognition queries for the 5 documented fraud typologies:
    1. Card Testing (micro-authorizations followed by high-value spend)
    2. Card-Not-Present (CNP) burst
    3. CNP on New Hardware Device
    4. Out-of-Region In-Person transaction (card cloning / counterfeit)
    5. Account Takeover (ATO - device swap followed by rapid cross-channel activity)
    
    Args:
        transaction_id: The integer TransactionID to test.
    """
    extractor, _, _, _ = get_services()
    subgraph = extractor.extract_subgraph(transaction_id)
    if not subgraph:
        return json.dumps({"error": f"Transaction {transaction_id} not found."})
    return json.dumps(subgraph["pattern_signals"], indent=2)

@server.tool()
def check_device_rings(transaction_id: int) -> str:
    """
    Check if the hardware signature or IP associated with this transaction is shared
    across multiple distinct customer accounts (Syndicate / Fraud Ring detection).
    
    Args:
        transaction_id: The integer TransactionID to check.
    """
    extractor, _, _, _ = get_services()
    subgraph = extractor.extract_subgraph(transaction_id)
    if not subgraph:
        return json.dumps({"error": f"Transaction {transaction_id} not found."})
    
    ring_info = {
        "transaction_id": transaction_id,
        "device_profile": subgraph["identity_device"].get("device_profile") if subgraph["identity_device"] else None,
        "shared_ring": subgraph["shared_hardware_ring"]
    }
    return json.dumps(ring_info, indent=2)

@server.tool()
def retrieve_similar_cases(
    query_text: str,
    target_pattern: str = "",
    target_exposure: float = 0.0,
    top_k: int = 3
) -> str:
    """
    Search historical closed case memory (5,565 resolved cases from months 1-4)
    using hybrid graph structure + TF-IDF semantic vector similarity.
    Evaluation benchmark cases are strictly isolated and never retrieved.
    
    Args:
        query_text: Natural language description or trigger keywords.
        target_pattern: Typology name (card_testing, out_of_region_use, etc.) or blank.
        target_exposure: Float transaction amount to match similar financial exposure.
        top_k: Number of precedent cases to return (default: 3).
    """
    _, similar_engine, _, _ = get_services()
    pattern_arg = target_pattern if target_pattern and target_pattern != "none" else None
    results = similar_engine.find_similar_cases(
        query_text=query_text,
        target_pattern=pattern_arg,
        target_exposure=target_exposure,
        top_k=top_k
    )
    return json.dumps(results, indent=2)

@server.tool()
def retrieve_policy_guidance(query: str, top_k: int = 3) -> str:
    """
    Semantic vector retrieval across bank fraud policies (R1 to R10),
    approval matrices, and regulatory requirements (FinCEN SAR, FATF, FFIEC).
    
    Args:
        query: Query string describing the situation, actions, or policy question.
        top_k: Number of relevant rules/articles to return (default: 3).
    """
    _, _, vector_retriever, _ = get_services()
    hits = vector_retriever.search(query, top_k=top_k)
    return json.dumps(hits, indent=2)

@server.tool()
def synthesize_case_dossier(
    transaction_id: int,
    case_id: str = "CASE-AUTO",
    trigger_type: str = "risk_score",
    trigger_text: str = ""
) -> str:
    """
    GraphRAG Synthesizer: constructs a comprehensive, structured, LLM-ready markdown
    investigative dossier combining graph traversal, pattern signals, hardware rings,
    relevant policy rules, and historical precedents.
    
    Args:
        transaction_id: Integer TransactionID.
        case_id: Case identifier (e.g., HHG-001).
        trigger_type: Type of trigger (e.g., risk_score, card_testing, out_of_region).
        trigger_text: Original alert/trigger notification text.
    """
    _, _, _, synthesizer = get_services()
    dossier = synthesizer.synthesize_investigation_dossier(
        transaction_id=transaction_id,
        case_id=case_id,
        trigger_type=trigger_type,
        trigger_text=trigger_text
    )
    return dossier

if __name__ == "__main__":
    # If run directly without arguments, print available tools or run stdio server
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        server.run(transport="stdio")
    else:
        print("TigerGraph Fraud Investigation MCP Server")
        print("Tools defined:")
        extractor, similar, vec, syn = get_services()
        print("Service singletons initialized successfully.")
        print("Run with `--stdio` to start the MCP stdio listener.")
