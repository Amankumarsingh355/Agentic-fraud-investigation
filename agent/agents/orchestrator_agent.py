"""
Chief Fraud Orchestrator Agent (Multi-Agent Swarm Supervisor)
Coordinates:
1. Graph Topology Agent (🕸️)
2. Velocity & Anomaly Agent (📈)
3. Identity & Device Agent (🛡️)
4. Policy & Compliance Agent (📜)
5. Case Memory Agent (🧠)
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from agent.agents.base_agent import AgentReport
from agent.agents.graph_agent import GraphTopologyAgent
from agent.agents.velocity_agent import VelocityAnomalyAgent
from agent.agents.identity_agent import IdentityDeviceAgent
from agent.agents.policy_agent import PolicyComplianceAgent
from agent.agents.memory_agent import CaseMemoryAgent

from agent.agent import FraudInvestigationAgent
from graph.subgraph_extractor import SubgraphExtractor

_global_core_agent = None

def get_shared_core_agent():
    global _global_core_agent
    if _global_core_agent is None:
        _global_core_agent = FraudInvestigationAgent()
    return _global_core_agent

class ChiefOrchestratorAgent:
    def __init__(self, core_agent: Optional[FraudInvestigationAgent] = None):
        print("[ChiefOrchestrator] Initializing Multi-Agent Fraud Squad...")
        self.core_agent = core_agent or get_shared_core_agent()
        self.extractor = self.core_agent.extractor
        
        # Instantiate the 5 specialized agents
        self.graph_agent = GraphTopologyAgent()
        self.velocity_agent = VelocityAnomalyAgent()
        self.identity_agent = IdentityDeviceAgent()
        self.policy_agent = PolicyComplianceAgent()
        self.memory_agent = CaseMemoryAgent(
            similar_engine=self.core_agent.similar_engine,
            vector_retriever=self.core_agent.vector_retriever
        )
        print("[ChiefOrchestrator] Multi-Agent Fraud Squad fully operational.")

    def run_squad_investigation(
        self,
        flagged_txn_id: int,
        trigger_type: str = "risk_score",
        trigger_text: Optional[str] = None,
        case_id: Optional[str] = None,
        customer_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches investigation to each specialized agent, gathers their individual reports,
        and generates the unified consensus dossier.
        """
        start_time = time.time()
        
        if not case_id:
            case_id = f"CASE-{flagged_txn_id}"
            
        if not trigger_text:
            trigger_text = f"Automated trigger for transaction #{flagged_txn_id}."

        # 1. Extract raw 2-hop TigerGraph subgraph
        subgraph = self.extractor.extract_subgraph(flagged_txn_id)
        if not subgraph:
            raise ValueError(f"Transaction ID {flagged_txn_id} not found in graph database.")

        patterns = subgraph.get("pattern_signals", {})
        dominant_pattern = "none"
        if patterns.get("card_testing", {}).get("flagged"):
            dominant_pattern = "card_testing"
        elif patterns.get("out_of_region", {}).get("flagged"):
            dominant_pattern = "out_of_region_use"
        elif patterns.get("cnp_new_device", {}).get("flagged"):
            dominant_pattern = "card_not_present_new_device"
        elif patterns.get("account_takeover", {}).get("flagged"):
            dominant_pattern = "account_takeover"

        # Prepare context for the squad
        context = {
            "case_id": case_id,
            "flagged_txn_id": flagged_txn_id,
            "trigger_type": trigger_type,
            "trigger_text": trigger_text,
            "customer_response": customer_response,
            "dominant_pattern": dominant_pattern,
            "subgraph": subgraph
        }

        # 2. Run all individual specialist agents
        agent_reports: Dict[str, Dict[str, Any]] = {}
        
        rep_graph = self.graph_agent.analyze(context)
        rep_vel = self.velocity_agent.analyze(context)
        rep_id = self.identity_agent.analyze(context)
        rep_mem = self.memory_agent.analyze(context)
        
        context["uncertainty_level"] = "low" if customer_response else "high"
        rep_pol = self.policy_agent.analyze(context)

        agent_reports["graph_topology"] = rep_graph.to_dict()
        agent_reports["velocity_anomaly"] = rep_vel.to_dict()
        agent_reports["identity_device"] = rep_id.to_dict()
        agent_reports["policy_compliance"] = rep_pol.to_dict()
        agent_reports["case_memory"] = rep_mem.to_dict()

        # 3. Compute Squad Consensus Score
        weights = {
            "graph_topology": 0.25,
            "velocity_anomaly": 0.20,
            "identity_device": 0.25,
            "policy_compliance": 0.15,
            "case_memory": 0.15
        }
        
        weighted_risk = (
            rep_graph.risk_score * weights["graph_topology"] +
            rep_vel.risk_score * weights["velocity_anomaly"] +
            rep_id.risk_score * weights["identity_device"] +
            rep_pol.risk_score * weights["policy_compliance"] +
            rep_mem.risk_score * weights["case_memory"]
        )

        avg_confidence = (
            rep_graph.confidence + rep_vel.confidence + rep_id.confidence + rep_pol.confidence + rep_mem.confidence
        ) / 5.0

        # Run full submission generation to guarantee 100% compliance
        case_obj, submission_dict = self.core_agent.run_investigation(
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn_id,
            case_id=case_id,
            simulated_customer_response=customer_response
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "success": True,
            "case_id": case_id,
            "flagged_txn_id": flagged_txn_id,
            "dominant_pattern": dominant_pattern,
            "elapsed_ms": elapsed_ms,
            "squad_consensus": {
                "weighted_risk_score": round(weighted_risk, 3),
                "team_confidence": round(avg_confidence, 3),
                "verdict": submission_dict["case"]["verdict"],
                "active_agents_count": 5,
                "squad_status": "ANALYSIS_COMPLETE"
            },
            "agents": agent_reports,
            "submission": submission_dict,
            "case": submission_dict["case"],
            "next_best_actions": submission_dict["next_best_actions"],
            "sar": submission_dict["sar"]
        }
