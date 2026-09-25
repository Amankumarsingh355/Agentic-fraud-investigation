"""
Customer Verification Provider Abstraction (agent/customer_verification.py)
Provides clean, pluggable interfaces for out-of-band customer transaction confirmation:
- MockCustomerVerificationProvider: deterministic evaluation for benchmarks and CI
- DemoCustomerVerificationProvider: interactive analyst simulator for demos
- WebhookCustomerVerificationProvider: production-ready asynchronous webhook/callback handler

Supports proper asynchronous case lifecycle states:
AWAITING_CUSTOMER_VERIFICATION -> Customer Response -> Re-Investigation -> Dynamic Action Evolution
"""

import os
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

class VerificationStatus:
    PENDING = "AWAITING_CUSTOMER_VERIFICATION"
    CONFIRMED_AUTHORIZED = "confirmed_authorized"
    DENIED_FRAUD = "denied_fraud"
    NO_RESPONSE = "no_response"
    TIMEOUT = "timeout"

class CustomerVerificationRequest:
    def __init__(
        self,
        case_id: str,
        customer_id: str,
        transaction_id: int,
        amount_usd: float,
        channel: str = "online",
        provider_name: str = "mock",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.request_id = f"VERIFY-{uuid.uuid4().hex[:8].upper()}"
        self.case_id = case_id
        self.customer_id = customer_id
        self.transaction_id = transaction_id
        self.amount_usd = amount_usd
        self.channel = channel
        self.provider_name = provider_name
        self.status = VerificationStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.responded_at = None
        self.response_value = None
        self.response_notes = ""
        self.metadata = metadata or {}

    def complete(self, response_value: str, notes: str = ""):
        self.response_value = response_value
        self.status = response_value
        self.responded_at = datetime.now().isoformat()
        self.response_notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "case_id": self.case_id,
            "customer_id": self.customer_id,
            "transaction_id": self.transaction_id,
            "amount_usd": self.amount_usd,
            "channel": self.channel,
            "provider_name": self.provider_name,
            "status": self.status,
            "created_at": self.created_at,
            "responded_at": self.responded_at,
            "response_value": self.response_value,
            "response_notes": self.response_notes,
            "metadata": self.metadata
        }

class CustomerVerificationProvider(ABC):
    """Abstract Base Class for all customer verification providers."""

    @abstractmethod
    def request_verification(
        self,
        case_id: str,
        customer_id: str,
        transaction_id: int,
        amount_usd: float,
        channel: str = "online",
        **kwargs
    ) -> CustomerVerificationRequest:
        """Dispatches an out-of-band challenge (SMS, App push, 3DS biometric, etc.)."""
        pass

    @abstractmethod
    def check_verification_status(self, request_id: str) -> Optional[CustomerVerificationRequest]:
        """Polls or retrieves current status of an open challenge."""
        pass

    @abstractmethod
    def submit_customer_response(
        self,
        request_id: str,
        response_value: str,
        notes: str = ""
    ) -> bool:
        """Submits customer feedback into the provider pipeline."""
        pass

class MockCustomerVerificationProvider(CustomerVerificationProvider):
    """
    Mock provider for automated benchmarks and CI test suites.
    Supports pre-configured simulated responses or deterministic case mappings.
    """
    def __init__(self, default_response: str = "denied_fraud"):
        self.default_response = default_response
        self.requests: Dict[str, CustomerVerificationRequest] = {}

    def request_verification(
        self,
        case_id: str,
        customer_id: str,
        transaction_id: int,
        amount_usd: float,
        channel: str = "online",
        simulated_response: Optional[str] = None,
        auto_complete: bool = False,
        **kwargs
    ) -> CustomerVerificationRequest:
        req = CustomerVerificationRequest(
            case_id=case_id,
            customer_id=customer_id,
            transaction_id=transaction_id,
            amount_usd=amount_usd,
            channel=channel,
            provider_name="mock_provider",
            metadata=kwargs
        )
        resp_to_use = simulated_response or self.default_response
        if auto_complete:
            req.complete(resp_to_use, notes="Auto-resolved by benchmark mock provider.")
        self.requests[req.request_id] = req
        return req

    def check_verification_status(self, request_id: str) -> Optional[CustomerVerificationRequest]:
        return self.requests.get(request_id)

    def submit_customer_response(
        self,
        request_id: str,
        response_value: str,
        notes: str = ""
    ) -> bool:
        if request_id in self.requests:
            self.requests[request_id].complete(response_value, notes=notes)
            return True
        return False

class DemoCustomerVerificationProvider(CustomerVerificationProvider):
    """
    Interactive provider for live hackathon demos.
    Leaves requests in AWAITING_CUSTOMER_VERIFICATION until analyst/user submits customer feedback.
    """
    def __init__(self):
        self.requests: Dict[str, CustomerVerificationRequest] = {}

    def request_verification(
        self,
        case_id: str,
        customer_id: str,
        transaction_id: int,
        amount_usd: float,
        channel: str = "online",
        **kwargs
    ) -> CustomerVerificationRequest:
        req = CustomerVerificationRequest(
            case_id=case_id,
            customer_id=customer_id,
            transaction_id=transaction_id,
            amount_usd=amount_usd,
            channel=channel,
            provider_name="demo_interactive",
            metadata=kwargs
        )
        self.requests[req.request_id] = req
        return req

    def check_verification_status(self, request_id: str) -> Optional[CustomerVerificationRequest]:
        return self.requests.get(request_id)

    def submit_customer_response(
        self,
        request_id: str,
        response_value: str,
        notes: str = ""
    ) -> bool:
        if request_id in self.requests:
            self.requests[request_id].complete(response_value, notes=notes)
            return True
        return False

    def get_pending_requests(self) -> List[CustomerVerificationRequest]:
        return [r for r in self.requests.values() if r.status == VerificationStatus.PENDING]

class WebhookCustomerVerificationProvider(CustomerVerificationProvider):
    """
    Webhook-ready asynchronous provider for external integration.
    Dispatches outbound payload to webhook_url, processes incoming callbacks.
    """
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("CUSTOMER_VERIFICATION_WEBHOOK_URL")
        self.requests: Dict[str, CustomerVerificationRequest] = {}

    def request_verification(
        self,
        case_id: str,
        customer_id: str,
        transaction_id: int,
        amount_usd: float,
        channel: str = "online",
        **kwargs
    ) -> CustomerVerificationRequest:
        req = CustomerVerificationRequest(
            case_id=case_id,
            customer_id=customer_id,
            transaction_id=transaction_id,
            amount_usd=amount_usd,
            channel=channel,
            provider_name="webhook_provider",
            metadata=kwargs
        )
        self.requests[req.request_id] = req

        # If webhook URL is configured, dispatch HTTP POST asynchronously
        if self.webhook_url:
            try:
                import urllib.request
                import json
                payload = json.dumps(req.to_dict()).encode("utf-8")
                req_obj = urllib.request.Request(
                    self.webhook_url,
                    data=payload,
                    headers={"Content-Type": "application/json", "X-Event": "verification_requested"}
                )
                urllib.request.urlopen(req_obj, timeout=2.0)
            except Exception as e:
                # Log without blocking
                pass

        return req

    def check_verification_status(self, request_id: str) -> Optional[CustomerVerificationRequest]:
        return self.requests.get(request_id)

    def submit_customer_response(
        self,
        request_id: str,
        response_value: str,
        notes: str = ""
    ) -> bool:
        if request_id in self.requests:
            self.requests[request_id].complete(response_value, notes=notes)
            return True
        return False
