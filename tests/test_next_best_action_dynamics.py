"""
Dynamic Next-Best-Action Test Suite (tests/test_next_best_action_dynamics.py)
TigerGraph Hacker House Goa 2026 — Agentic Fraud Investigation System

Validates that next-best-action recommendations are truly dynamic, context-aware,
and strictly conformant to Bank Fraud Policy v1.0 Rules R1-R10 across 5 rigorous scenarios:

  - Scenario A: Customer Confirms Authorized -> Action de-escalates to CLOSE_NO_FRAUD (auto).
  - Scenario B: Customer Denies Fraud -> Action escalates to BLOCK_CARD (L1) and CREATE_CASE (auto).
  - Scenario C: Insufficient Evidence -> Non-destructive restraint (VERIFY_WITH_CUSTOMER [R1], STEP_UP_AUTH).
  - Scenario D: Hardware Ring Corroboration -> Syndicate ring detection triggers MONITOR_CONNECTED_CARDS and FILE_REPORT (L2).
  - Scenario E: Policy Threshold Gating -> Strict mathematical enforcement of auto, L1 ($<=2500), and L2 (>2500, SAR).
"""

import os
import sys
import unittest
from typing import Dict, Any

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.policy_engine import PolicyEngine
from agent.uncertainty_engine import UncertaintyEngine
from agent.decision_engine import DecisionEngine
from graph.subgraph_extractor import SubgraphExtractor


class TestNextBestActionDynamics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy_engine = PolicyEngine()
        cls.uncertainty_engine = UncertaintyEngine()
        cls.decision_engine = DecisionEngine()
        cls.extractor = SubgraphExtractor()

    def _get_mock_subgraph(self, amount: float = 77.07, ring_size: int = 1, is_ring: bool = False) -> Dict[str, Any]:
        """Constructs synthetic but realistic subgraph topology."""
        return {
            "target_transaction": {
                "txn_id": 3514030,
                "customer_id": 101,
                "card_id": "101-K1",
                "amount": amount,
                "channel": "W",
                "risk_score": 0.61,
                "addr1": 444.0
            },
            "customer_profile": {
                "customer_id": 101,
                "home_region": 204.0,
                "total_txns": 12,
                "total_volume": 1240.50
            },
            "card_timeline_72h": [
                {"txn_id": 3514028, "amount": 12.50, "delta_s": 3600},
                {"txn_id": 3514030, "amount": amount, "delta_s": 120}
            ],
            "identity_device": {
                "device_profile": "Windows 10 | Chrome 120.0 | 1920x1080",
                "proxy_status": "residential"
            },
            "shared_hardware_ring": {
                "has_shared_ring": is_ring,
                "ring_size": ring_size,
                "connected_customers": [202, 303, 404] if is_ring else []
            },
            "pattern_signals": {
                "card_testing": {"flagged": False},
                "out_of_region": {"flagged": True, "current_region": 444.0, "home_region": 204.0},
                "cnp_new_device": {"flagged": False},
                "account_takeover": {"flagged": False}
            }
        }

    # -------------------------------------------------------------------------
    # SCENARIO A: Customer Confirmation De-escalation
    # -------------------------------------------------------------------------
    def test_scenario_a_customer_confirmation_deescalation(self):
        """Cardholder confirms transaction was authorized: actions must de-escalate to CLOSE_NO_FRAUD."""
        subgraph = self._get_mock_subgraph(amount=125.00)
        
        # Assess uncertainty with customer authorization
        assessment = self.uncertainty_engine.assess(
            subgraph=subgraph,
            trigger_type="risk_score",
            trigger_risk_score=0.65,
            customer_verification_status="confirmed_authorized"
        )
        
        # Risk probability must collapse
        self.assertLessEqual(assessment["fraud_probability"], 0.15)
        self.assertEqual(assessment["uncertainty_level"], "LOW")
        
        actions = self.policy_engine.evaluate_actions(
            subgraph=subgraph,
            risk_assessment=assessment,
            customer_verification_status="confirmed_authorized",
            trigger_type="risk_score"
        )
        action_names = [a["action"] for a in actions]
        
        # Must recommend CLOSE_NO_FRAUD under Rule R3
        self.assertIn("CLOSE_NO_FRAUD", action_names)
        self.assertNotIn("BLOCK_CARD", action_names)
        self.assertNotIn("FILE_REPORT", action_names)
        
        # Must route autonomously
        close_act = next(a for a in actions if a["action"] == "CLOSE_NO_FRAUD")
        self.assertEqual(close_act["route"], "auto")
        self.assertEqual(close_act["policy_rule"], "Rule R3")

    # -------------------------------------------------------------------------
    # SCENARIO B: Customer Denial Escalation
    # -------------------------------------------------------------------------
    def test_scenario_b_customer_denial_escalation(self):
        """Cardholder denies transaction: actions must escalate to BLOCK_CARD and CREATE_CASE."""
        subgraph = self._get_mock_subgraph(amount=482.12)
        
        assessment = self.uncertainty_engine.assess(
            subgraph=subgraph,
            trigger_type="customer_report",
            trigger_risk_score=0.75,
            customer_verification_status="denied_fraud"
        )
        
        self.assertGreaterEqual(assessment["fraud_probability"], 0.85)
        self.assertTrue(assessment["has_sufficient_evidence"])
        
        actions = self.policy_engine.evaluate_actions(
            subgraph=subgraph,
            risk_assessment=assessment,
            customer_verification_status="denied_fraud",
            trigger_type="customer_report"
        )
        action_names = [a["action"] for a in actions]
        
        # Must block card and create case
        self.assertIn("BLOCK_CARD", action_names)
        self.assertIn("CREATE_CASE", action_names)
        
        # Destructive card block requires L1 authorization under Rule R2
        block_act = next(a for a in actions if a["action"] == "BLOCK_CARD")
        self.assertEqual(block_act["route"], "L1")
        self.assertEqual(block_act["policy_rule"], "Rule R2")

    # -------------------------------------------------------------------------
    # SCENARIO C: Insufficient Evidence Handling
    # -------------------------------------------------------------------------
    def test_scenario_c_insufficient_evidence_restraint(self):
        """Uncorroborated single alert with evidence gaps: must NOT block card; must request verification."""
        # Uncorroborated alert, no device match, pending customer response
        subgraph = self._get_mock_subgraph(amount=85.00)
        subgraph["pattern_signals"]["out_of_region"]["flagged"] = False
        
        assessment = self.uncertainty_engine.assess(
            subgraph=subgraph,
            trigger_type="risk_score",
            trigger_risk_score=0.62,
            customer_verification_status="pending"
        )
        
        self.assertFalse(assessment["has_sufficient_evidence"])
        self.assertIn(assessment["uncertainty_level"], ["HIGH", "MEDIUM"])
        self.assertTrue(len(assessment["evidence_gaps"]) > 0)
        
        actions = self.policy_engine.evaluate_actions(
            subgraph=subgraph,
            risk_assessment=assessment,
            customer_verification_status="pending",
            trigger_type="risk_score"
        )
        action_names = [a["action"] for a in actions]
        
        # Under Rule R1, premature blocking is strictly forbidden
        self.assertNotIn("BLOCK_CARD", action_names)
        self.assertIn("VERIFY_WITH_CUSTOMER", action_names)
        self.assertIn("MONITOR_CARD", action_names)

    # -------------------------------------------------------------------------
    # SCENARIO D: Hardware Ring Corroboration
    # -------------------------------------------------------------------------
    def test_scenario_d_hardware_ring_corroboration(self):
        """Syndicate ring across >= 3 accounts: must trigger MONITOR_CONNECTED_CARDS and FILE_REPORT (L2)."""
        subgraph = self._get_mock_subgraph(amount=100.07, ring_size=4, is_ring=True)
        
        assessment = self.uncertainty_engine.assess(
            subgraph=subgraph,
            trigger_type="risk_score",
            trigger_risk_score=0.88,
            customer_verification_status="pending"
        )
        
        actions = self.policy_engine.evaluate_actions(
            subgraph=subgraph,
            risk_assessment=assessment,
            customer_verification_status="pending",
            trigger_type="risk_score"
        )
        action_names = [a["action"] for a in actions]
        
        # Rule R6 mandates connected card surveillance and regulatory filing
        self.assertIn("MONITOR_CONNECTED_CARDS", action_names)
        self.assertIn("FILE_REPORT", action_names)
        
        report_act = next(a for a in actions if a["action"] == "FILE_REPORT")
        self.assertEqual(report_act["route"], "L2")
        self.assertEqual(report_act["policy_rule"], "Rule R6")

    # -------------------------------------------------------------------------
    # SCENARIO E: Policy Route Gating Thresholds
    # -------------------------------------------------------------------------
    def test_scenario_e_policy_route_gating_thresholds(self):
        """Validates exact approval routing: auto, L1 ($<=2500), and L2 (>2500, SAR)."""
        # 1. Autonomous actions
        route, role = self.policy_engine.determine_action_route("MONITOR_CARD", exposure_usd=500.0)
        self.assertEqual(route, "auto")
        
        route, role = self.policy_engine.determine_action_route("CREATE_CASE", exposure_usd=50000.0)
        self.assertEqual(route, "auto")
        
        route, role = self.policy_engine.determine_action_route("VERIFY_WITH_CUSTOMER", exposure_usd=1000.0)
        self.assertEqual(route, "auto")

        # 2. L1 Tier: Block Card <= $2,500
        route, role = self.policy_engine.determine_action_route("BLOCK_CARD", exposure_usd=2499.0)
        self.assertEqual(route, "L1")
        self.assertEqual(role, "Team Lead Sign-off")

        # 3. L2 Tier: Block Card > $2,500
        route, role = self.policy_engine.determine_action_route("BLOCK_CARD", exposure_usd=2500.01)
        self.assertEqual(route, "L2")
        self.assertEqual(role, "Fraud Manager Sign-off")

        # 4. L2 Tier: Regulatory SAR File Report (always L2 regardless of amount)
        route, role = self.policy_engine.determine_action_route("FILE_REPORT", exposure_usd=74.96)
        self.assertEqual(route, "L2")
        self.assertEqual(role, "Fraud Manager Sign-off")


if __name__ == "__main__":
    unittest.main()
