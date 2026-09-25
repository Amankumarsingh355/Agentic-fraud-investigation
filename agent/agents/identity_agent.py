"""
Identity & Device Fingerprint Specialist Agent
"""

from typing import Dict, Any, List
from datetime import datetime
from agent.agents.base_agent import BaseSpecialistAgent, AgentReport, AgentFinding

class IdentityDeviceAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_identity_device",
            agent_name="Identity & Device Agent",
            specialization="Hardware Fingerprinting, Geo-Location & Proxy Detection",
            avatar="🛡️"
        )

    def analyze(self, context: Dict[str, Any]) -> AgentReport:
        subgraph = context.get("subgraph", {})
        dev_obj = subgraph.get("identity_device") or {}
        patterns = subgraph.get("pattern_signals") or {}
        out_of_region = patterns.get("out_of_region", {})
        cnp_new_device = patterns.get("cnp_new_device", {})
        ato = patterns.get("account_takeover", {})

        findings = []
        key_evidence = []

        dev_profile = dev_obj.get("device_profile", "unknown")
        proxy_status = dev_obj.get("proxy_status", "clean")
        
        is_oor = out_of_region.get("flagged", False)
        is_cnp = cnp_new_device.get("flagged", False)
        is_ato = ato.get("flagged", False)

        risk_score = 0.08
        confidence = 0.86
        status = "PASS"
        action = None

        if is_ato:
            risk_score = 0.96
            confidence = 0.94
            status = "CRITICAL"
            action = "LOCK_CREDENTIALS_AND_ALERT"
            findings.append(AgentFinding(
                finding_type="ACCOUNT_TAKEOVER_DEVICE_SHIFT",
                description="Cross-channel credential variance and sudden device substitution detected.",
                severity="CRITICAL",
                score=0.96,
                evidence_proof=ato
            ))
            key_evidence.append({
                "type": "ato_alert",
                "label": "Account Takeover Signature",
                "detail": f"Unrecognized hardware: {dev_profile}"
            })
        elif is_oor:
            cur_reg = out_of_region.get("current_region")
            home_reg = out_of_region.get("home_region")
            risk_score = 0.78
            confidence = 0.90
            status = "FLAGGED"
            action = "VERIFY_CARDHOLDER_TRAVEL"
            findings.append(AgentFinding(
                finding_type="GEOGRAPHIC_MISMATCH",
                description=f"In-person swipe in Region {cur_reg} vs Cardholder Home Region {home_reg}.",
                severity="HIGH",
                score=0.78,
                evidence_proof=out_of_region
            ))
            key_evidence.append({
                "type": "geo_variance",
                "label": f"Region {cur_reg} vs {home_reg}",
                "detail": "Cross-boundary physical terminal transaction"
            })
        elif is_cnp:
            risk_score = 0.70
            confidence = 0.84
            status = "FLAGGED"
            action = "STEP_UP_CHALLENGE"
            findings.append(AgentFinding(
                finding_type="NEW_DEVICE_CNP",
                description="Card-Not-Present transaction initiated from a previously unseen hardware profile.",
                severity="MEDIUM",
                score=0.70,
                evidence_proof=cnp_new_device
            ))
            key_evidence.append({
                "type": "new_device",
                "label": "Unseen Browser/Device",
                "detail": dev_profile
            })
        else:
            findings.append(AgentFinding(
                finding_type="VERIFIED_IDENTITY",
                description="Transaction origin consistent with known cardholder device and home territory.",
                severity="INFO",
                score=0.08,
                evidence_proof={"proxy_status": proxy_status}
            ))
            key_evidence.append({
                "type": "identity_pass",
                "label": "Device & Geo Matched",
                "detail": f"Clean proxy ({proxy_status}), home region verified"
            })

        summary = (
            f"Identity evaluation: Device profile '{dev_profile}', Proxy '{proxy_status}'. "
            f"Geo mismatch: {is_oor}. Status: {status}."
        )

        return AgentReport(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            specialization=self.specialization,
            avatar=self.avatar,
            timestamp=datetime.utcnow().isoformat() + "Z",
            risk_score=risk_score,
            confidence=confidence,
            status=status,
            summary=summary,
            findings=findings,
            key_evidence=key_evidence,
            recommended_action=action,
            telemetry={
                "device_fingerprint": dev_profile,
                "proxy_status": proxy_status,
                "geo_mismatch_detected": is_oor
            }
        )
