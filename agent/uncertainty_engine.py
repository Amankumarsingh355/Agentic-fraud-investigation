"""
Inspectable Uncertainty & Confidence Reasoning Engine
Evaluates mathematical fraud probability, confidence score, evidence completeness,
and explicit uncertainty level.
Zero conflation between risk and confidence: high risk + low confidence mandates step-up/verification.
"""

from typing import Dict, Any, List, Optional


class UncertaintyEngine:
    def __init__(self):
        # Configurable, policy-aligned weightings
        self.CONFIDENCE_THRESHOLD = 0.75
        self.HIGH_FRAUD_THRESHOLD = 0.70
        self.LOW_FRAUD_THRESHOLD = 0.25

    def assess(
        self,
        subgraph: Dict[str, Any],
        trigger_type: str,
        trigger_risk_score: Optional[float] = None,
        customer_verification_status: str = "pending"  # pending, confirmed_authorized, denied_fraud, unresponsive
    ) -> Dict[str, Any]:
        """
        Decomposes evidence into an inspectable, traceable risk and uncertainty assessment.
        Returns:
            fraud_probability (risk_score): [0.0 - 1.0]
            confidence_score: [0.0 - 1.0]
            evidence_completeness: [0.0 - 1.0]
            uncertainty_score: [0.0 - 1.0]
            uncertainty_level: "LOW" | "MEDIUM" | "HIGH"
            has_sufficient_evidence: bool
            criteria_breakdown: detailed signals and deltas
        """
        target = subgraph["target_transaction"]
        cust = subgraph["customer_profile"]
        timeline = subgraph.get("card_timeline_72h", [])
        device = subgraph.get("identity_device")
        rings = subgraph.get("shared_hardware_ring", {})
        patterns = subgraph.get("pattern_signals", {})

        breakdown = {
            "base_signals": [],
            "corroborating_signals": [],
            "mitigating_signals": [],
            "evidence_gaps": []
        }

        # -------------------------------------------------------------
        # 1. Base Signal Evaluation (Prior)
        # -------------------------------------------------------------
        base_prob = 0.20  # baseline transaction prior in flagged cohort
        if trigger_type == "customer_report":
            base_prob = 0.65
            breakdown["base_signals"].append({
                "signal": "Direct Customer Dispute/Inquiry",
                "delta": +0.45,
                "detail": "Customer explicitly questioned or reported the charge."
            })
        elif trigger_type == "analyst_request":
            base_prob = 0.50
            breakdown["base_signals"].append({
                "signal": "Analyst Flagged Investigation",
                "delta": +0.30,
                "detail": "Case routed by human analyst investigating unusual activity or shared devices."
            })
        elif trigger_risk_score is not None:
            base_prob = float(trigger_risk_score)
            breakdown["base_signals"].append({
                "signal": f"Bank Risk Model Score ({trigger_risk_score:.2f})",
                "delta": round(trigger_risk_score - 0.20, 2),
                "detail": "Real-time automated transaction scoring model."
            })

        prob = base_prob

        # -------------------------------------------------------------
        # 2. Corroborating Graph Evidence
        # -------------------------------------------------------------
        corroboration_points = 0

        # Out-of-region check
        if patterns.get("out_of_region", {}).get("flagged"):
            delta = 0.20
            prob += delta
            corroboration_points += 1
            curr_reg = patterns["out_of_region"].get("current_region")
            home_reg = patterns["out_of_region"].get("home_region")
            breakdown["corroborating_signals"].append({
                "signal": "Out-of-Region In-Person POS",
                "delta": +delta,
                "detail": f"Physical card used in region {curr_reg} away from established home {home_reg}."
            })

        # New Device check
        if device and device.get("is_new"):
            delta = 0.15
            prob += delta
            corroboration_points += 1
            breakdown["corroborating_signals"].append({
                "signal": "New Hardware Device Profile",
                "delta": +delta,
                "detail": f"Online session from unfamiliar hardware signature: {device.get('device_profile')}."
            })

        # Anonymous Proxy check
        if device and "ANONYMOUS" in str(device.get("proxy_status", "")):
            delta = 0.15
            prob += delta
            corroboration_points += 1
            breakdown["corroborating_signals"].append({
                "signal": "Anonymous Proxy / VPN Connection",
                "delta": +delta,
                "detail": f"Identity record reveals proxy type {device.get('proxy_status')}."
            })

        # Card Testing Sequence check
        if patterns.get("card_testing", {}).get("flagged"):
            delta = 0.25
            prob += delta
            corroboration_points += 1
            ct = patterns["card_testing"]
            breakdown["corroborating_signals"].append({
                "signal": "Card Testing Authorization Pattern",
                "delta": +delta,
                "detail": f"{ct.get('micro_count')} micro-auth(s) under $10 followed by {ct.get('large_count')} large auth(s)."
            })

        # Shared Hardware Syndicate Ring check (Rule R6)
        if rings.get("has_shared_ring"):
            ring_size = rings.get("ring_size", 1)
            delta = 0.35 if ring_size > 2 else 0.25
            prob += delta
            corroboration_points += 2
            breakdown["corroborating_signals"].append({
                "signal": f"Syndicate Device Ring ({ring_size} connected accounts)",
                "delta": +delta,
                "detail": f"Hardware profile is shared across {ring_size} separate customer accounts: {rings.get('connected_customers')}."
            })

        # -------------------------------------------------------------
        # 3. Mitigating Counter-Evidence
        # -------------------------------------------------------------
        mitigating_points = 0

        # Long customer tenure (> 50 transactions)
        if cust.get("total_historical_txns", 0) > 50:
            delta = -0.10
            prob += delta
            mitigating_points += 1
            breakdown["mitigating_signals"].append({
                "signal": "Established Customer History",
                "delta": delta,
                "detail": f"Customer has {cust['total_historical_txns']} historical transactions totaling ${cust.get('total_historical_volume', 0):,.2f}."
            })

        # Established home region match for in-person transactions
        if target.get("channel") == "in_person" and not patterns.get("out_of_region", {}).get("flagged"):
            delta = -0.15
            prob += delta
            mitigating_points += 1
            breakdown["mitigating_signals"].append({
                "signal": "Home Region In-Person Activity",
                "delta": delta,
                "detail": f"Transaction took place in established home billing region {target.get('addr1')}."
            })

        # Clamp mathematical probability before interactive verification
        prob = max(0.01, min(0.99, prob))

        # -------------------------------------------------------------
        # 4. Interactive Customer Verification Impact
        # -------------------------------------------------------------
        evidence_gaps = []
        if customer_verification_status == "confirmed_authorized":
            prob = 0.02
            breakdown["mitigating_signals"].append({
                "signal": "Explicit Customer Confirmation (Rule R3)",
                "delta": -0.90,
                "detail": "Cardholder confirmed initiating this transaction."
            })
        elif customer_verification_status == "denied_fraud":
            prob = 0.98
            breakdown["corroborating_signals"].append({
                "signal": "Explicit Customer Denial of Charge (Rule R2)",
                "delta": +0.90,
                "detail": "Cardholder explicitly stated they did not authorize this purchase."
            })
        elif customer_verification_status == "unresponsive":
            prob = min(0.85, prob + 0.15)
            breakdown["corroborating_signals"].append({
                "signal": "Unresponsive Cardholder >24h (Rule R4)",
                "delta": +0.15,
                "detail": "No response to cardholder verification within 24 hours."
            })
        else:
            # Pending customer verification - check for key evidence gaps
            if patterns.get("out_of_region", {}).get("flagged") and not rings.get("has_shared_ring"):
                evidence_gaps.append("Missing confirmation whether out-of-region spend is legitimate travel vs cloned card (Rule R1).")
            if trigger_type == "risk_score" and corroboration_points == 0:
                evidence_gaps.append("Weak uncorroborated single signal: risk score stands alone without graph or device anomalies (Rule R1).")
            if target.get("amount", 0) > 500 and prob < 0.80 and corroboration_points < 2:
                evidence_gaps.append(f"High financial exposure (${target.get('amount'):.2f}) with ambiguous corroboration (Rule R8).")

        breakdown["evidence_gaps"] = evidence_gaps

        # -------------------------------------------------------------
        # 5. Evidence Completeness Calculation
        # -------------------------------------------------------------
        # Checklist:
        # Check 1: Trigger verified (always present)
        # Check 2: Customer baseline profile extracted
        # Check 3: Graph topology & 72h timeline traversed
        # Check 4: Identity/device verified (if online) or POS physical check (if in_person)
        # Check 5: Customer confirmation or corroborating multi-signal link
        checks_completed = 3  # checks 1, 2, 3 always completed
        total_checks = 5
        if device or target.get("channel") == "in_person":
            checks_completed += 1
        if customer_verification_status in ["confirmed_authorized", "denied_fraud"] or rings.get("has_shared_ring") or corroboration_points >= 2:
            checks_completed += 1

        evidence_completeness = round(checks_completed / total_checks, 2)

        # -------------------------------------------------------------
        # 6. Traceable Confidence Score Calculation
        # -------------------------------------------------------------
        base_confidence = 0.40
        if customer_verification_status in ["confirmed_authorized", "denied_fraud"]:
            confidence = 0.98
            uncertainty = 0.02
        elif rings.get("has_shared_ring"):
            confidence = 0.90
            uncertainty = 0.10
        else:
            confidence = base_confidence + (0.15 * corroboration_points) - (0.20 * len(evidence_gaps))
            confidence = max(0.10, min(0.85, confidence))
            uncertainty = round(1.0 - confidence, 4)

        # Determine uncertainty level
        if uncertainty >= 0.50:
            unc_level = "HIGH"
        elif uncertainty >= 0.25:
            unc_level = "MEDIUM"
        else:
            unc_level = "LOW"

        # Determine confidence level
        if confidence >= 0.75:
            conf_level = "HIGH"
        elif confidence >= 0.50:
            conf_level = "MEDIUM"
        else:
            conf_level = "LOW"

        # -------------------------------------------------------------
        # 7. Evidence Sufficiency Determination
        # -------------------------------------------------------------
        has_sufficient_evidence = False
        if customer_verification_status in ["confirmed_authorized", "denied_fraud"]:
            has_sufficient_evidence = True
        elif rings.get("has_shared_ring") and len(rings.get("connected_customers", [])) >= 1:
            has_sufficient_evidence = True
        elif patterns.get("card_testing", {}).get("flagged") and patterns["card_testing"].get("micro_count", 0) >= 2:
            has_sufficient_evidence = True
        elif confidence >= self.CONFIDENCE_THRESHOLD and len(evidence_gaps) == 0 and evidence_completeness >= 0.80:
            has_sufficient_evidence = True

        return {
            "fraud_probability": round(prob, 4),
            "risk_score": round(prob, 4),
            "confidence_score": round(confidence, 4),
            "evidence_completeness": evidence_completeness,
            "uncertainty_score": round(uncertainty, 4),
            "uncertainty_level": unc_level,
            "confidence_level": conf_level,
            "has_sufficient_evidence": has_sufficient_evidence,
            "corroboration_count": corroboration_points,
            "mitigating_count": mitigating_points,
            "evidence_gaps": evidence_gaps,
            "criteria_breakdown": breakdown
        }
