"""
Decision Engine & Two-Stage Next Best Action Evolution
Computes:
1. Initial next best actions (prior to interactive evidence gathering)
2. Controlled evidence requests with assumed responses
3. Final next best actions (after assumed evidence is incorporated)
4. 'what_changed' explanation tracking action evolution
"""

from typing import Dict, Any, List, Optional, Tuple

class DecisionEngine:
    def __init__(self):
        pass

    def evaluate_decision_evolution(
        self,
        subgraph: Dict[str, Any],
        initial_assessment: Dict[str, Any],
        final_assessment: Dict[str, Any],
        trigger_type: str,
        initial_actions: List[Dict[str, Any]],
        final_actions: List[Dict[str, Any]],
        assumed_customer_response: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Synthesizes the two-stage action progression:
        Returns:
        - evidence_requests: List[Dict]
        - next_best_actions: {"initial": [...], "final": [...], "what_changed": "..."}
        """
        target = subgraph["target_transaction"]
        rings = subgraph.get("shared_hardware_ring", {})
        patterns = subgraph.get("pattern_signals", {})
        exposure = float(target.get("amount", 0.0))
        
        evidence_requests = []
        
        # Check if controlled evidence gathering was necessary
        # Rule R1: Weak signal / single risk score / out-of-region POS without confirmation
        needs_customer_validation = (
            trigger_type == "risk_score" and 
            initial_assessment["fraud_probability"] < 0.70 and 
            not rings.get("has_shared_ring", False)
        ) or (
            patterns.get("out_of_region", {}).get("flagged") and 
            trigger_type != "customer_report"
        )
        
        if needs_customer_validation or assumed_customer_response is not None:
            # Formulate assumed response based on actual case context or assumed parameter
            if assumed_customer_response == "confirmed_authorized":
                resp_text = f"Customer states they authorized this purchase of ${exposure:.2f} while traveling."
            elif assumed_customer_response == "denied_fraud":
                resp_text = f"Customer states they did not make this purchase of ${exposure:.2f} and still has physical possession of the card."
            elif assumed_customer_response == "unresponsive":
                resp_text = "No response received from cardholder within standard 24-hour verification window."
            else:
                # Default assumed response based on risk score / pattern
                if initial_assessment["fraud_probability"] >= 0.60:
                    resp_text = f"Customer denies initiating this ${exposure:.2f} transaction and confirms card was in their possession."
                else:
                    resp_text = f"Customer confirms they authorized this ${exposure:.2f} transaction."

            evidence_requests.append({
                "type": "customer_validation",
                "asked_after_step": 4,
                "assumed_response": resp_text
            })

        # Format initial actions (only action, route, reason)
        clean_initial = [
            {
                "action": a["action"] if "action" in a else a["action_name"],
                "route": a["route"],
                "reason": a["reason"]
            }
            for a in initial_actions
        ]
        
        # Format final actions
        clean_final = [
            {
                "action": a["action"] if "action" in a else a["action_name"],
                "route": a["route"],
                "reason": a["reason"]
            }
            for a in final_actions
        ]
        
        # If no evidence requests were made, final equals initial
        if not evidence_requests:
            clean_final = clean_initial
            ring_size = rings.get("ring_size", 1)
            if rings.get("has_shared_ring") and ring_size > 1:
                what_changed = (
                    f"Graph ring traversal provided decisive structural proof of multi-account syndicate "
                    f"({ring_size} connected accounts); no customer inquiry was required and definitive policy actions were formulated immediately."
                )
            else:
                what_changed = (
                    f"Initial graph evidence and historical precedent match provided sufficient certainty; "
                    f"no additional customer inquiry was required and policy recommendations were maintained."
                )
        else:
            # Compute what_changed explanation
            p_init = initial_assessment["fraud_probability"]
            p_final = final_assessment["fraud_probability"]
            
            if assumed_customer_response == "denied_fraud" or (assumed_customer_response is None and p_final >= 0.70):
                what_changed = (
                    f"Customer denial raised fraud probability from {p_init:.2f} to {p_final:.2f}, "
                    f"confirming the need for permanent card block and fraud case creation."
                )
                if any(a["action"] == "FILE_REPORT" for a in clean_final):
                    what_changed += " Financial exposure and graph ring connections triggered regulatory SAR filing."
            elif assumed_customer_response == "confirmed_authorized" or p_final <= 0.20:
                what_changed = (
                    f"Customer confirmation lowered fraud probability from {p_init:.2f} to {p_final:.2f}, "
                    f"allowing the transaction to clear and closing the case without customer friction."
                )
            elif assumed_customer_response == "unresponsive":
                what_changed = (
                    f"Cardholder failed to reply within 24 hours. Initial monitoring escalated to "
                    f"declining pending authorizations and routing to human analyst under Rule R4."
                )
            else:
                what_changed = (
                    f"Evidence gathering updated assessed fraud probability from {p_init:.2f} to {p_final:.2f}, "
                    f"transitioning actions from preliminary monitoring to definitive case resolution."
                )

        next_best_actions = {
            "initial": clean_initial,
            "final": clean_final,
            "what_changed": what_changed
        }
        
        return evidence_requests, next_best_actions
