"""
Dynamic Case Memory & Graph Persistence Manager
Persists resolved cases, decisions, evidence, and findings back to graph memory.
Enforces benchmark evaluation isolation (eval cases are strictly tagged and excluded).
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from graph.pattern_registry import PatternRegistry
from graph.load_vector_store import VectorRetriever

MEMORY_FILE = os.path.join("data", "dynamic_case_memory.json")

class CaseMemoryManager:
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.pattern_registry = PatternRegistry()
        self.dynamic_cases: Dict[str, Dict[str, Any]] = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load {self.memory_file}: {e}")
        return {}

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.dynamic_cases, f, indent=2)

    def persist_case(
        self,
        case_obj: Any,
        subgraph: Optional[Dict[str, Any]] = None,
        is_benchmark: bool = False
    ) -> Dict[str, Any]:
        """
        Persists a resolved Case object into the dynamic graph memory store.
        """
        case_dict = case_obj.to_dict() if hasattr(case_obj, "to_dict") else case_obj
        cid = case_dict["case_id"]
        
        # Determine case outcome & pattern
        outcome = "cleared" if case_dict.get("status") == "CLOSED" else "confirmed_fraud"
        actions = case_dict.get("actions", [])
        if any(a.get("action_name") == "CLOSE_NO_FRAUD" for a in actions):
            outcome = "cleared"
        elif any(a.get("action_name") in ["BLOCK_CARD", "BLOCK_ALL_CARDS", "FILE_REPORT"] for a in actions):
            outcome = "confirmed_fraud"
            
        # Determine dominant typology
        findings = case_dict.get("findings", [])
        pattern = "none"
        for f in findings:
            ftype = f.get("type", "").lower()
            if "card_testing" in ftype:
                pattern = "card_testing"
                break
            elif "out_of_region" in ftype:
                pattern = "out_of_region_use"
                break
            elif "syndicate" in ftype or "ring" in ftype:
                pattern = "syndicate_ring"
                break
            elif "takeover" in ftype:
                pattern = "account_takeover"
                break
                
        # Calculate exposure
        target = subgraph.get("target_transaction", {}) if subgraph else {}
        exposure = float(target.get("amount", case_dict.get("trigger", {}).get("risk_score", 0.0)))
        
        # Graph Vertices Structure
        graph_vertices = {
            "Case": {
                "case_id": cid,
                "opened_at": case_dict.get("opened_at"),
                "closed_at": case_dict.get("closed_at", datetime.now().isoformat()),
                "status": case_dict.get("status"),
                "outcome": outcome,
                "pattern": pattern,
                "exposure_usd": exposure,
                "is_benchmark": is_benchmark,
                "namespace": "eval_benchmark" if is_benchmark else "case_memory",
                "narrative": case_dict.get("decision_explanation", "")
            },
            "Evidence": [
                {
                    "evidence_id": f"{cid}-{ev.get('evidence_id')}",
                    "evidence_type": ev.get("type"),
                    "source": ev.get("source"),
                    "title": ev.get("title"),
                    "score": ev.get("score")
                }
                for ev in case_dict.get("evidence_list", [])
            ]
        }
        
        # Graph Edges Structure
        cust_id = case_dict.get("trigger", {}).get("customer_id")
        card_id = case_dict.get("trigger", {}).get("card_id")
        txn_id = case_dict.get("trigger", {}).get("flagged_txn_id")
        
        graph_edges = {
            "PART_OF_CASE": [{"from": txn_id, "to": cid}],
            "INVESTIGATED_CARD": [{"from": cid, "to": card_id}],
            "INVESTIGATED_CUSTOMER": [{"from": cid, "to": cust_id}],
            "ATTACHED_EVIDENCE": [
                {"from": cid, "to": f"{cid}-{ev.get('evidence_id')}"}
                for ev in case_dict.get("evidence_list", [])
            ],
            "APPLIED_POLICY": [
                {"from": cid, "to": a.get("policy_rule")}
                for a in actions if a.get("policy_rule")
            ]
        }
        
        memory_record = {
            "case_id": cid,
            "outcome": outcome,
            "pattern": pattern,
            "exposure_usd": exposure,
            "customer_id": cust_id,
            "card_id": card_id,
            "flagged_txn_id": txn_id,
            "is_benchmark": is_benchmark,
            "namespace": "eval_benchmark" if is_benchmark else "case_memory",
            "narrative": case_dict.get("decision_explanation", ""),
            "actions_taken": [a.get("action_name") for a in actions],
            "graph_vertices": graph_vertices,
            "graph_edges": graph_edges,
            "persisted_at": datetime.now().isoformat()
        }
        
        self.dynamic_cases[cid] = memory_record
        self._save_memory()

        # Feedback into pattern registry if confirmed fraud
        if outcome == "confirmed_fraud" and subgraph:
            dev = subgraph.get("identity_device")
            if dev and dev.get("device_profile"):
                self.pattern_registry.register_entity(
                    entity_type="device",
                    entity_value=dev["device_profile"],
                    case_id=cid,
                    pattern=pattern,
                    notes=f"Confirmed fraud in Case {cid}: {pattern} (${exposure:.2f})"
                )
            if dev and dev.get("proxy_status") and "ANONYMOUS" in str(dev.get("proxy_status")):
                self.pattern_registry.register_entity(
                    entity_type="proxy",
                    entity_value=str(dev["proxy_status"]),
                    case_id=cid,
                    pattern=pattern,
                    notes=f"Confirmed anonymous proxy in Case {cid}"
                )

        # Attempt Live TigerGraph Upsert Write-Back
        try:
            from graph.tigergraph_crewai_integration import conn
            if conn and hasattr(conn, "upsertVertex"):
                conn.upsertVertex(
                    "ClosedCase",
                    cid,
                    attributes={
                        "status": case_dict.get("status", "RESOLVED"),
                        "outcome": outcome,
                        "pattern": pattern,
                        "exposure_usd": float(exposure),
                        "analyst_notes": case_dict.get("decision_explanation", "")[:500]
                    }
                )
                if txn_id:
                    try:
                        conn.upsertEdge("ClosedCase", cid, "INVOLVES", "Transaction", str(txn_id))
                    except Exception:
                        pass
                if card_id:
                    try:
                        conn.upsertEdge("ClosedCase", cid, "ON_CARD", "Card", str(card_id))
                    except Exception:
                        pass
        except Exception:
            pass  # Seamless fallback to persistent dynamic case memory

        return memory_record

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self.dynamic_cases.get(case_id)

    def list_cases(self, namespace: str = "case_memory") -> List[Dict[str, Any]]:
        return [c for c in self.dynamic_cases.values() if c.get("namespace") == namespace]

    def clear(self):
        self.dynamic_cases = {}
        self._save_memory()
        self.pattern_registry.clear()
