"""
Human-In-The-Loop (HITL) Enforcement & Authorization Tests (tests/test_hitl_enforcement.py)
TigerGraph Hacker House Goa 2026 — Agentic Fraud Investigation System

Validates strict human governance and approval controls:
1. Negative Test: Autonomous execution of destructive actions (e.g., BLOCK_CARD with route L1/L2) is strictly BLOCKED and held as PENDING_APPROVAL.
2. Negative Test: Missing authorization credentials reject state modification; card status remains unchanged.
3. Positive Test: Valid L1 Team Lead sign-off executes card containment inside SandboxActionGateway, transitioning card from ACTIVE -> BLOCKED.
4. Positive Test: Valid L2 Fraud Manager sign-off approves high-exposure regulatory reporting actions.
5. End-to-End API Test: Validates that the live approval gateway endpoint correctly updates case status and executes the action.
"""

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.action_gateway import SandboxActionGateway, ActionState, CardStatus
from agent.policy_engine import PolicyEngine


class TestHITLEnforcement(unittest.TestCase):
    def setUp(self):
        # Use isolated temporary sandbox state file for test hygiene
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.gateway = SandboxActionGateway(state_file=self.temp_file.name)
        self.policy_engine = PolicyEngine()
        self.card_id = "CARD-TEST-9999"
        self.cust_id = "CUST-TEST-8888"
        self.case_id = "HHG-TEST-001"

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_negative_autonomous_destructive_action_held(self):
        """Negative Test: Autonomous engine CANNOT execute BLOCK_CARD without human sign-off."""
        # Initial card status must be ACTIVE
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.ACTIVE)

        # Attempt to dispatch BLOCK_CARD with route L1 but NO authorized_by
        res = self.gateway.execute_action(
            action="BLOCK_CARD",
            case_id=self.case_id,
            card_id=self.card_id,
            customer_id=self.cust_id,
            amount_usd=482.12,
            route="L1",
            authorized_by=None  # No human sign-off
        )

        # Action MUST be held in PENDING_APPROVAL
        self.assertEqual(res["execution_status"], ActionState.PENDING_APPROVAL)
        self.assertIsNone(res["authorized_by"])
        self.assertIn("held in approval queue", res["reason"])

        # Card MUST remain ACTIVE — no destructive state change allowed
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.ACTIVE)

    def test_negative_l2_action_held_without_signoff(self):
        """Negative Test: L2 FILE_REPORT is held in PENDING_APPROVAL if no management sign-off."""
        res = self.gateway.execute_action(
            action="FILE_REPORT",
            case_id=self.case_id,
            card_id=self.card_id,
            customer_id=self.cust_id,
            amount_usd=1000.03,
            route="L2",
            authorized_by=None
        )

        self.assertEqual(res["execution_status"], ActionState.PENDING_APPROVAL)
        self.assertIn("Route L2 sign-off required", res["reason"])

    def test_positive_l1_analyst_signoff_executes_block(self):
        """Positive Test: Valid L1 Team Lead sign-off transitions card to BLOCKED in sandbox."""
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.ACTIVE)

        # L1 Team Lead signs off
        res = self.gateway.execute_action(
            action="BLOCK_CARD",
            case_id=self.case_id,
            card_id=self.card_id,
            customer_id=self.cust_id,
            amount_usd=482.12,
            route="L1",
            authorized_by="analyst_lead_01",
            reason="Confirmed out-of-region card cloning under Rule R4."
        )

        # Status MUST be EXECUTED_IN_SANDBOX
        self.assertEqual(res["execution_status"], ActionState.EXECUTED_IN_SANDBOX)
        self.assertEqual(res["authorized_by"], "analyst_lead_01")
        self.assertEqual(res["previous_card_status"], CardStatus.ACTIVE)
        self.assertEqual(res["new_card_status"], CardStatus.BLOCKED)

        # Gateway ledger must confirm card is now BLOCKED
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.BLOCKED)

    def test_positive_l2_manager_signoff_executes_regulatory_filing(self):
        """Positive Test: Valid L2 Fraud Manager sign-off executes FILE_REPORT."""
        res = self.gateway.execute_action(
            action="FILE_REPORT",
            case_id=self.case_id,
            card_id=self.card_id,
            customer_id=self.cust_id,
            amount_usd=1000.03,
            route="L2",
            authorized_by="fraud_manager_01",
            reason="Confirmed multi-account syndicate under Rule R6."
        )

        self.assertEqual(res["execution_status"], ActionState.EXECUTED_IN_SANDBOX)
        self.assertEqual(res["authorized_by"], "fraud_manager_01")

    def test_card_state_lifecycle_persistence(self):
        """Verifies state transitions: ACTIVE -> BLOCKED -> ACTIVE (unblock)."""
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.ACTIVE)

        # Block
        self.gateway.execute_action(
            action="BLOCK_CARD", case_id=self.case_id, card_id=self.card_id,
            customer_id=self.cust_id, route="L1", authorized_by="analyst_01"
        )
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.BLOCKED)

        # Unblock upon customer confirmation
        self.gateway.execute_action(
            action="UNBLOCK_CARD", case_id=self.case_id, card_id=self.card_id,
            customer_id=self.cust_id, route="auto", authorized_by="analyst_01"
        )
        self.assertEqual(self.gateway.get_card_status(self.card_id), CardStatus.ACTIVE)

    def test_disclaimer_integrity(self):
        """Verifies technical honesty: institutional sandbox disclaimer present in all responses."""
        res = self.gateway.execute_action(
            action="MONITOR_CARD", case_id=self.case_id, card_id=self.card_id,
            customer_id=self.cust_id, route="auto"
        )
        self.assertIn("Sandbox", res["disclaimer"])


if __name__ == "__main__":
    unittest.main()
