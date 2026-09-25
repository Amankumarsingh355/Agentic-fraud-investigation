"""
Bank Fraud Policy & Approval Authority Engine
Strictly enforces Bank Fraud Policy v1.0, Operational Rules (R1 - R10),
and Permission Matrix (auto, L1, L2).
Zero fabricated rules. Strictly grounded in repository policy documentation.
"""

from typing import Dict, Any, List, Optional, Tuple


class PolicyEngine:
    def __init__(self):
        # Section 2 Canonical Action Permission Matrix
        self.AUTO_ACTIONS = {
            "ALLOW_TRANSACTION",
            "MONITOR_CARD",
            "MONITOR_CONNECTED_CARDS",
            "WARN_CUSTOMER",
            "VERIFY_WITH_CUSTOMER",
            "STEP_UP_AUTH",
            "GENERATE_REPORT",
            "CREATE_CASE",
            "ESCALATE_TO_ANALYST",
            "CLOSE_NO_FRAUD"
        }

    def determine_action_route(self, action_name: str, exposure_usd: float) -> Tuple[str, str]:
        """
        Returns (route, role_description):
        - route: 'auto', 'L1', or 'L2'
        - role_description: 'Autonomous Agent', 'Team Lead Sign-off', or 'Fraud Manager Sign-off'
        """
        if action_name in self.AUTO_ACTIONS:
            return "auto", "Autonomous Agent"

        if action_name == "DECLINE_TRANSACTION":
            return "L1", "Team Lead Sign-off"

        if action_name == "BLOCK_CARD":
            if exposure_usd <= 2500.0:
                return "L1", "Team Lead Sign-off"
            else:
                return "L2", "Fraud Manager Sign-off"

        if action_name in ["BLOCK_ALL_CARDS", "FILE_REPORT"]:
            return "L2", "Fraud Manager Sign-off"

        # Default fail-safe: require highest management approval
        return "L2", "Fraud Manager Sign-off (Unclassified Action)"

    def evaluate_actions(
        self,
        subgraph: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        customer_verification_status: str = "pending",
        trigger_type: str = "risk_score",
        is_recurring_dispute: bool = False,
        is_undocumented_pattern: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Determines the policy-compliant sequence of actions and assigns approval routes.
        Follows Bank Fraud Policy v1.0 Rules R1 to R10.
        """
        target = subgraph["target_transaction"]
        rings = subgraph.get("shared_hardware_ring", {})
        patterns = subgraph.get("pattern_signals", {})
        exposure = target.get("amount", 0.0)
        prob = risk_assessment.get("fraud_probability", 0.0)
        has_sufficient_evidence = risk_assessment.get("has_sufficient_evidence", False)
        gaps = risk_assessment.get("evidence_gaps", [])

        actions = []

        def add_act(name: str, rule: str, reason: str):
            route, role = self.determine_action_route(name, exposure)
            # Avoid duplicate action recommendations
            if not any(a["action"] == name for a in actions):
                actions.append({
                    "action": name,
                    "route": route,
                    "approval_role": role,
                    "policy_rule": rule,
                    "reason": reason,
                    "is_autonomous": (route == "auto")
                })

        # --- RULE EVALUATION HIERARCHY ---

        # Rule R7: Disputed But Legitimate Recurring Activity
        if is_recurring_dispute:
            add_act("CREATE_CASE", "Rule R7", "Disputed charge matches historical recurring pattern.")
            add_act("VERIFY_WITH_CUSTOMER", "Rule R7", "Verify recurring subscription with customer.")
            add_act("WARN_CUSTOMER", "Rule R7", "Provide recurring charge advisory to customer; do not block.")
            return actions

        # 1. Customer Verification Cases (Rules R2, R3, R4)
        if customer_verification_status == "confirmed_authorized":
            # Rule R3: Customer Confirms the Transaction
            add_act("CLOSE_NO_FRAUD", "Rule R3", "Cardholder verified initiating transaction. Close case without fraud.")
            return actions

        if customer_verification_status == "denied_fraud":
            # Rule R2: Customer Denies the Transaction
            add_act("CREATE_CASE", "Rule R2", "Customer explicitly denied transaction. Open formal fraud case.")
            add_act("BLOCK_CARD", "Rule R2", f"Compromised card replacement required for customer-reported fraud (${exposure:.2f} exposure).")
            if exposure > 1000.0 or rings.get("has_shared_ring"):
                add_act("FILE_REPORT", "Rule R2 / Section 4", f"Mandatory FinCEN SAR filing: unauthorized charge exceeds $1,000 threshold or links to shared ring.")
            return actions

        if customer_verification_status == "unresponsive":
            # Rule R4: Unresponsive Cardholder (>24h)
            add_act("CREATE_CASE", "Rule R4", "Customer unresponsive after 24h verification window.")
            add_act("MONITOR_CARD", "Rule R4", "Place card under heightened monitoring.")
            add_act("DECLINE_TRANSACTION", "Rule R4", "Decline authorization pending customer re-engagement.")
            if exposure > 500.0:
                add_act("ESCALATE_TO_ANALYST", "Rule R4", f"High exposure (${exposure:.2f}) on unresponsive account requires manual review.")
            return actions

        # Rule R9: Undocumented Coordinated Patterns
        if is_undocumented_pattern:
            add_act("CREATE_CASE", "Rule R9", "Undocumented coordinated pattern detected across accounts.")
            add_act("FILE_REPORT", "Rule R9", "Mandatory SAR for coordinated novel abuse pattern.")
            add_act("ESCALATE_TO_ANALYST", "Rule R9", "Escalate undocumented pattern to fraud analyst.")
            return actions

        # 2. Shared Origin & Syndicate Rings (Rule R6)
        if rings.get("has_shared_ring"):
            ring_size = rings.get("ring_size", 1)
            add_act("CREATE_CASE", "Rule R6", f"Syndicate fraud ring detected: hardware profile shared across {ring_size} distinct accounts.")
            add_act("FILE_REPORT", "Rule R6", f"Mandatory SAR filing for organized cross-account syndicate ({ring_size} connected customers).")
            add_act("MONITOR_CONNECTED_CARDS", "Rule R6", f"Heighten monitoring on all {len(rings.get('connected_customers', []))} peer cards sharing this hardware.")
            if prob >= 0.70:
                add_act("BLOCK_CARD", "Rule R6", "Block compromised target card identified in confirmed syndicate.")
            return actions

        # 3. Card Testing Sequences (Rule R5)
        if patterns.get("card_testing", {}).get("flagged"):
            add_act("CREATE_CASE", "Rule R5", "Card testing velocity signature identified.")
            add_act("DECLINE_TRANSACTION", "Rule R5", "Decline suspected automated testing sequence authorization.")
            add_act("STEP_UP_AUTH", "Rule R5", "Require multi-factor challenge on subsequent online checkout attempts.")
            if exposure > 100.0:
                add_act("BLOCK_CARD", "Rule R5", f"High value purchase (${exposure:.2f}) cleared after micro-authorizations; initiate block.")
            return actions

        # 4. Out-of-Region In-Person Activity (Rule R1: Verify Before You Block)
        if patterns.get("out_of_region", {}).get("flagged"):
            add_act("CREATE_CASE", "Rule R1 / Section 4", "Out-of-region in-person spend recorded.")
            if prob < 0.70 or not has_sufficient_evidence:
                add_act("VERIFY_WITH_CUSTOMER", "Rule R1", f"Verify out-of-region POS charge in Region {patterns['out_of_region'].get('current_region')} with cardholder before taking blocking action.")
                add_act("MONITOR_CARD", "Rule R1", "Temporarily monitor card while awaiting cardholder verification response.")
            else:
                add_act("DECLINE_TRANSACTION", "Rule R1", "Decline suspicious out-of-region authorization.")
                add_act("BLOCK_CARD", "Rule R1", "Block card on corroborated multi-signal out-of-region compromise.")
            return actions

        # 5. Weak Signal & High Uncertainty (Rule R1, Rule R8)
        if not has_sufficient_evidence or prob < 0.50:
            if trigger_type == "risk_score" and prob < 0.70:
                add_act("VERIFY_WITH_CUSTOMER", "Rule R1", "Verify transaction with cardholder due to uncorroborated single risk score.")
                add_act("MONITOR_CARD", "Rule R1", "Monitor card for 72h window.")
            elif exposure > 500.0:
                add_act("ESCALATE_TO_ANALYST", "Rule R8", f"Uncertain verdict on high financial exposure (${exposure:.2f}).")
            else:
                add_act("MONITOR_CARD", "Section 1", "Low confidence single signal; keep card active under standard heightened monitoring.")
            return actions

        # 6. High Confidence Fraud Default
        if prob >= 0.70:
            add_act("CREATE_CASE", "Section 1", "High confidence fraud probability detected.")
            add_act("DECLINE_TRANSACTION", "Section 1", "Decline fraudulent authorization.")
            add_act("BLOCK_CARD", "Section 1", f"Block compromised card (${exposure:.2f} exposure).")
            if exposure > 1000.0:
                add_act("FILE_REPORT", "Section 4", "Mandatory regulatory SAR: loss exposure exceeds $1,000.")
        else:
            add_act("ALLOW_TRANSACTION", "Section 1", "Transaction permitted without customer friction.")
            add_act("MONITOR_CARD", "Section 1", "Card retained in active monitoring.")

        return actions
