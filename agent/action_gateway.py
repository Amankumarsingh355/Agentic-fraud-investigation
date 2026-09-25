"""
Institutional Sandbox Action Gateway (agent/action_gateway.py)
Provides realistic, technically honest simulation of card and banking action execution:
- Clearly disclaims: "Simulated execution inside Sandbox Banking Gateway (not real production banking)."
- Manages persisted state transitions: card.status (ACTIVE -> BLOCKED | MONITORED | RESTRICTED)
- Action lifecycle states: RECOMMENDED -> PENDING_APPROVAL -> APPROVED -> EXECUTED_IN_SANDBOX -> FAILED
- Tracks timeline events and audit records
"""

import os
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class ActionState:
    RECOMMENDED = "RECOMMENDED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTED_IN_SANDBOX = "EXECUTED_IN_SANDBOX"
    FAILED = "FAILED"
    REJECTED = "REJECTED"

class CardStatus:
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    MONITORED = "MONITORED"
    RESTRICTED = "RESTRICTED"

class ActionGateway(ABC):
    """Abstract Base Class for action dispatch and banking gateway interaction."""

    @abstractmethod
    def execute_action(
        self,
        action: str,
        case_id: str,
        card_id: str,
        customer_id: str,
        amount_usd: float = 0.0,
        authorized_by: Optional[str] = None,
        route: str = "auto",
        reason: str = ""
    ) -> Dict[str, Any]:
        """Executes action in the gateway target."""
        pass

    @abstractmethod
    def get_card_status(self, card_id: str) -> str:
        """Retrieves card state from gateway ledger."""
        pass

    @abstractmethod
    def get_action_history(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves dispatch audit logs."""
        pass

class MockActionGateway(ActionGateway):
    """Deterministic mock gateway for unit tests and benchmarks."""
    def __init__(self):
        self.card_states: Dict[str, str] = {}
        self.history: List[Dict[str, Any]] = []

    def execute_action(
        self,
        action: str,
        case_id: str,
        card_id: str,
        customer_id: str,
        amount_usd: float = 0.0,
        authorized_by: Optional[str] = None,
        route: str = "auto",
        reason: str = ""
    ) -> Dict[str, Any]:
        prev_status = self.get_card_status(card_id)
        new_status = prev_status

        if action in ["BLOCK_CARD", "BLOCK_ALL_CARDS"]:
            new_status = CardStatus.BLOCKED
        elif action == "UNBLOCK_CARD":
            new_status = CardStatus.ACTIVE
        elif action == "MONITOR_CARD":
            new_status = CardStatus.MONITORED
        elif action == "STEP_UP_AUTH":
            new_status = CardStatus.RESTRICTED

        self.card_states[card_id] = new_status
        record = {
            "gateway_execution_id": f"GW-{uuid.uuid4().hex[:8].upper()}",
            "gateway_type": "MOCK",
            "action": action,
            "case_id": case_id,
            "card_id": card_id,
            "customer_id": customer_id,
            "previous_card_status": prev_status,
            "new_card_status": new_status,
            "execution_status": ActionState.EXECUTED_IN_SANDBOX,
            "route": route,
            "authorized_by": authorized_by or "MOCK_AUTOMATION",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "Simulated in MockActionGateway"
        }
        self.history.append(record)
        return record

    def get_card_status(self, card_id: str) -> str:
        return self.card_states.get(card_id, CardStatus.ACTIVE)

    def get_action_history(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if case_id:
            return [h for h in self.history if h["case_id"] == case_id]
        return self.history

class SandboxActionGateway(ActionGateway):
    """
    Institutional Sandbox Action Gateway.
    Persists realistic card state transitions to data/sandbox_state.json and audit ledger.
    Enforces route-based human authorization checks.
    """
    def __init__(self, state_file: Optional[str] = None):
        self.state_file = state_file or os.path.join(PROJECT_ROOT, "data", "sandbox_state.json")
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.card_states = data.get("card_states", {})
                    self.history = data.get("history", [])
                    return
            except Exception:
                pass
        self.card_states = {}
        self.history = []

    def _save_state(self):
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "updated_at": datetime.now().isoformat(),
                    "gateway": "SandboxActionGateway_v2.6",
                    "disclaimer": "Institutional Sandbox Simulation - Not connected to live clearing / payment rails.",
                    "card_states": self.card_states,
                    "history": self.history[-100:] # retain last 100
                }, f, indent=2)
        except Exception:
            pass

    def execute_action(
        self,
        action: str,
        case_id: str,
        card_id: str,
        customer_id: str,
        amount_usd: float = 0.0,
        authorized_by: Optional[str] = None,
        route: str = "auto",
        reason: str = ""
    ) -> Dict[str, Any]:
        # 1. Authorization check
        if route in ["L1", "L2"] and not authorized_by:
            # Human approval not provided
            record = {
                "gateway_execution_id": f"GW-{uuid.uuid4().hex[:8].upper()}",
                "gateway_type": "SANDBOX",
                "action": action,
                "case_id": case_id,
                "card_id": card_id,
                "customer_id": customer_id,
                "execution_status": ActionState.PENDING_APPROVAL,
                "route": route,
                "authorized_by": None,
                "reason": f"Action {action} held in approval queue. Route {route} sign-off required.",
                "timestamp": datetime.now().isoformat(),
                "disclaimer": "Simulated in Institutional Sandbox Gateway"
            }
            self.history.append(record)
            self._save_state()
            return record

        # 2. Compute Card State Transition
        prev_status = self.get_card_status(card_id)
        new_status = prev_status

        if action in ["BLOCK_CARD", "BLOCK_ALL_CARDS"]:
            new_status = CardStatus.BLOCKED
        elif action == "UNBLOCK_CARD":
            new_status = CardStatus.ACTIVE
        elif action == "MONITOR_CARD":
            new_status = CardStatus.MONITORED
        elif action == "STEP_UP_AUTH":
            new_status = CardStatus.RESTRICTED
        elif action == "DECLINE_TRANSACTION":
            # Transaction declined, card status maintained or monitored
            new_status = prev_status if prev_status != CardStatus.ACTIVE else CardStatus.MONITORED

        self.card_states[card_id] = new_status

        # 3. Emit Sandbox Execution Record
        record = {
            "gateway_execution_id": f"GW-{uuid.uuid4().hex[:8].upper()}",
            "gateway_type": "SANDBOX",
            "action": action,
            "case_id": case_id,
            "card_id": card_id,
            "customer_id": customer_id,
            "previous_card_status": prev_status,
            "new_card_status": new_status,
            "execution_status": ActionState.EXECUTED_IN_SANDBOX,
            "route": route,
            "authorized_by": authorized_by or "SYSTEM_AUTONOMOUS_POLICY",
            "reason": reason or f"Executed in Institutional Sandbox Gateway under Policy Route {route}",
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "Simulated in Institutional Sandbox Banking Gateway"
        }

        self.history.append(record)
        self._save_state()
        return record

    def get_card_status(self, card_id: str) -> str:
        return self.card_states.get(card_id, CardStatus.ACTIVE)

    def get_action_history(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if case_id:
            return [h for h in self.history if h["case_id"] == case_id]
        return self.history

# Default global instance
_default_sandbox_gateway = None

def get_action_gateway() -> ActionGateway:
    global _default_sandbox_gateway
    if _default_sandbox_gateway is None:
        _default_sandbox_gateway = SandboxActionGateway()
    return _default_sandbox_gateway
