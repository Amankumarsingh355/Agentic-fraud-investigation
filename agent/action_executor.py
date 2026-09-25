"""
Action Execution & Policy Gating Layer
Executes realistic mocked side effects for autonomous actions while strictly gating
and holding L1/L2 actions pending required human authority sign-off.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class ActionExecutor:
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []

    def dispatch_action(
        self,
        action_name: str,
        route: str,
        case_id: str,
        customer_id: str,
        card_id: str,
        txn_id: int,
        amount: float,
        reason: str,
        policy_rule: str,
        simulate_human_signoff: bool = False
    ) -> Dict[str, Any]:
        """
        Dispatches an action through the policy gate.
        If route == 'auto': autonomously executes mock side-effects.
        If route in ['L1', 'L2']: holds action in PENDING_HUMAN_APPROVAL unless explicit sign-off is provided.
        """
        execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now().isoformat()
        
        # Check Policy Gating
        if route != "auto" and not simulate_human_signoff:
            # Action requires human sign-off - agent MUST NOT autonomously execute!
            record = {
                "execution_id": execution_id,
                "action": action_name,
                "route": route,
                "status": "PENDING_HUMAN_APPROVAL",
                "execution_time": now_iso,
                "reason": reason,
                "policy_rule": policy_rule,
                "human_signoff_required": True,
                "approval_token": f"TOKEN-{uuid.uuid4().hex[:6].upper()}",
                "side_effects": {
                    "execution_blocked": True,
                    "message": f"Action {action_name} requires {route} human authorization. Staged in approval queue.",
                    "queue": "TEAM_LEAD_QUEUE" if route == "L1" else "FRAUD_MANAGER_QUEUE"
                }
            }
            self.execution_history.append(record)
            return record

        # Autonomous or Approved Execution
        side_effects = self._generate_mock_side_effects(
            action_name=action_name,
            case_id=case_id,
            customer_id=customer_id,
            card_id=card_id,
            txn_id=txn_id,
            amount=amount
        )
        
        record = {
            "execution_id": execution_id,
            "action": action_name,
            "route": route,
            "status": "EXECUTED",
            "execution_time": now_iso,
            "reason": reason,
            "policy_rule": policy_rule,
            "human_signoff_required": (route != "auto"),
            "side_effects": side_effects
        }
        self.execution_history.append(record)
        return record

    def _generate_mock_side_effects(
        self,
        action_name: str,
        case_id: str,
        customer_id: str,
        card_id: str,
        txn_id: int,
        amount: float
    ) -> Dict[str, Any]:
        """Generates realistic mock side-effects for financial & compliance actions."""
        now_iso = datetime.now().isoformat()
        
        if action_name == "VERIFY_WITH_CUSTOMER":
            return {
                "channel": "SMS_PUSH_DISPATCHER",
                "recipient_customer": customer_id,
                "message": f"Security Alert: Did you authorize charge of ${amount:.2f} at {now_iso[:19]}? Reply YES or NO.",
                "dispatch_id": f"SMS-{uuid.uuid4().hex[:6].upper()}",
                "status": "DELIVERED",
                "awaiting_cardholder_reply": True
            }
            
        elif action_name == "STEP_UP_AUTH":
            return {
                "security_protocol": "3D_SECURE_2.2",
                "challenge_method": "BIOMETRIC_PUSH_OTP",
                "card_id": card_id,
                "challenge_token": f"MFA-{uuid.uuid4().hex[:8].upper()}",
                "status": "CHALLENGE_PENDING"
            }
            
        elif action_name == "ESCALATE_TO_ANALYST":
            return {
                "workflow_system": "TIGERGRAPH_FRAUD_OPS",
                "ticket_id": f"TKT-{uuid.uuid4().hex[:6].upper()}",
                "case_id": case_id,
                "queue": "L1_ANALYST_ADJUDICATION",
                "priority": "HIGH",
                "status": "ROUTED"
            }
            
        elif action_name == "MONITOR_CARD":
            return {
                "card_id": card_id,
                "monitoring_profile": "HEIGHTENED_VELOCITY_72H",
                "threshold_adjustment": 0.80,
                "active_until": "72_hours_rolling"
            }
            
        elif action_name == "MONITOR_CONNECTED_CARDS":
            return {
                "syndicate_protection": True,
                "target_card": card_id,
                "action": "SURVEILLANCE_DEPLOYED_ACROSS_SHARED_DEVICE_RING"
            }
            
        elif action_name == "WARN_CUSTOMER":
            return {
                "channel": "SECURE_PORTAL_INBOX",
                "customer_id": customer_id,
                "notice_type": "ACCOUNT_USAGE_ADVISORY",
                "status": "POSTED"
            }
            
        elif action_name == "CREATE_CASE":
            return {
                "database": "TigerGraph",
                "graph_vertex": "Case",
                "vertex_id": case_id,
                "namespace": "case_memory",
                "persisted": True
            }
            
        elif action_name == "CLOSE_NO_FRAUD":
            return {
                "case_id": case_id,
                "status": "CLOSED",
                "resolution": "CLEARED_LEGITIMATE",
                "customer_friction": "NONE"
            }
            
        elif action_name == "ALLOW_TRANSACTION":
            return {
                "txn_id": txn_id,
                "core_banking_status": "APPROVED",
                "clearing_status": "CLEARED"
            }
            
        elif action_name == "DECLINE_TRANSACTION":
            return {
                "txn_id": txn_id,
                "authorization_response": "DECLINED",
                "response_code": "05_DO_NOT_HONOR",
                "merchant_notified": True
            }
            
        elif action_name == "BLOCK_CARD":
            return {
                "card_id": card_id,
                "card_status": "PERMANENTLY_BLOCKED",
                "reissue_workflow": "AUTOMATIC_REPLACEMENT_TRIGGERED",
                "atm_pos_access": "REVOKED"
            }
            
        elif action_name == "BLOCK_ALL_CARDS":
            return {
                "customer_id": customer_id,
                "all_cards_status": "SUSPENDED",
                "digital_banking": "RESTRICTED",
                "incident_type": "FULL_CREDENTIAL_COMPROMISE"
            }
            
        elif action_name == "FILE_REPORT":
            return {
                "regulatory_body": "FinCEN",
                "filing_type": "Suspicious Activity Report (SAR)",
                "docket_number": f"SAR-2016-{uuid.uuid4().hex[:6].upper()}",
                "filing_status": "TRANSMITTED_BSA_EFILE",
                "retention_period": "5_YEARS"
            }
            
        return {"action": action_name, "executed": True}
