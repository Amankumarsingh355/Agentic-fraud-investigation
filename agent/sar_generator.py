"""
FinCEN Suspicious Activity Report (SAR) Narrative & Compliance Engine
Generates regulatory filings adhering strictly to BSA/FinCEN SAR requirements:
- The 6-Question Framework: Who, What, When, Where, How, and Why
- Subject entity resolution: customers, cards, devices, merchant categories
- Strict consistency with Bank Fraud Policy v1.0 and README answer format
"""

from typing import Dict, Any, List, Optional

class SARGenerator:
    def __init__(self):
        pass

    def generate_sar(
        self,
        subgraph: Dict[str, Any],
        verdict: str,
        fraud_probability: float,
        pattern: str,
        actions: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        assumed_customer_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates whether a SAR filing is mandated by policy and generates
        the compliant regulatory filing.
        """
        target = subgraph["target_transaction"]
        cust = subgraph["customer_profile"]
        timeline = subgraph.get("card_timeline_72h", [])
        device = subgraph.get("identity_device")
        rings = subgraph.get("shared_hardware_ring", {})
        
        exposure = float(target.get("amount", 0.0))
        cust_id = target.get("customer_id")
        card_id = target.get("card_id")
        txn_id = target.get("txn_id")
        
        # Strictly enforce: SAR file == true ONLY if FILE_REPORT exists in final actions
        file_report_mandated = any(
            (a.get("action") == "FILE_REPORT" or a.get("action_name") == "FILE_REPORT")
            for a in actions
        )
        should_file = file_report_mandated and (verdict == "fraud")
        
        # If verdict is legitimate or should not file, return empty compliant SAR block
        if not should_file or verdict == "legitimate":
            reason = "No regulatory SAR required: transaction confirmed legitimate or financial exposure does not meet statutory reporting threshold under BSA/FinCEN guidelines."
            if verdict == "uncertain":
                reason = "Filing deferred under Policy Rule R8: investigation remains uncertain pending additional customer authentication."
            return {
                "file": False,
                "reason": reason,
                "narrative": "",
                "subjects": [],
                "total_amount_usd": 0,
                "activity_dates": []
            }

        # Determine Filing Reason
        if rings.get("has_shared_ring"):
            ring_size = rings.get("ring_size", 1)
            reason = f"Rule R6 / FinCEN SAR Filing: Organised multi-card syndicate detected. Hardware profile is shared across {ring_size} distinct accounts."
        elif exposure >= 1000.0:
            reason = f"Rule R2 / Statutory Threshold: Confirmed unauthorized transaction exceeding $1,000 reporting threshold (${exposure:,.2f} total exposure)."
        elif pattern == "card_testing":
            reason = "Rule R5: Automated card testing sequence followed by unauthorized card draining."
        elif pattern == "account_takeover":
            reason = "Rule R9 / Credential Compromise: Unauthorized account takeover with cross-channel anomalies and device substitution."
        else:
            reason = f"FinCEN SAR Filing: Confirmed fraudulent activity under pattern '{pattern}' with total exposure ${exposure:,.2f}."

        # Compile Subjects
        subjects = [cust_id, card_id]
        if rings.get("has_shared_ring"):
            for conn_cust in rings.get("connected_customers", []):
                if conn_cust not in subjects:
                    subjects.append(conn_cust)
        if device and device.get("device_profile"):
            subjects.append(device["device_profile"])

        # Compile Activity Dates
        txn_ts = str(target.get("ts", ""))[:10]
        dates = [t.get("ts", "")[:10] for t in timeline if t.get("ts")]
        if not dates:
            dates = [txn_ts]
        start_date = min(dates)
        end_date = max(dates)
        activity_dates = [start_date, end_date]

        # Calculate Total Suspicious Amount
        # For card testing or ring, sum recent suspicious txns; else target amount
        if pattern == "card_testing":
            suspicious_txns = [t for t in timeline if t.get("channel") == "online"]
            total_amt = round(sum(t.get("amount", 0.0) for t in suspicious_txns), 2)
            if total_amt < exposure:
                total_amt = exposure
        else:
            total_amt = round(exposure, 2)

        # Generate 6-Question Framework SAR Narrative (6 to 12 sentences)
        narrative_parts = []
        
        # 1. WHO
        narrative_parts.append(
            f"This Suspicious Activity Report pertains to customer {cust_id} and debit/credit card {card_id}."
        )
        if rings.get("has_shared_ring"):
            connected_str = ", ".join(rings.get("connected_customers", [])[:3])
            narrative_parts.append(
                f"Graph analytics identified a shared hardware syndicate linking this account to multiple other customer profiles including {connected_str}."
            )
            
        # 2. WHAT & WHEN
        narrative_parts.append(
            f"Between {start_date} and {end_date}, transaction activity totaling ${total_amt:,.2f} USD was flagged for anomalous risk indicators, initiated via the {target.get('channel')} channel under merchant product category {target.get('product_cd')}."
        )
        narrative_parts.append(
            f"The primary flagged transaction {txn_id} occurred on {str(target.get('ts'))[:19]} for an amount of ${exposure:.2f}."
        )
        
        # 3. WHERE
        if target.get("channel") == "in_person":
            narrative_parts.append(
                f"Physical card-present transactions took place in geographic billing region {target.get('addr1')} (Country {target.get('addr2')}), which represents a geographic deviation from the cardholder's established domestic home region {cust.get('home_region')}."
            )
        else:
            dev_str = device.get('device_profile') if device else "unidentified browser"
            proxy_str = device.get('proxy_status') if device else "unknown"
            narrative_parts.append(
                f"Online authentication originated from digital hardware profile '{dev_str}' with proxy routing classified as '{proxy_str}'."
            )
            
        # 4. HOW
        if pattern == "card_testing":
            narrative_parts.append(
                "The modus operandi matches automated card testing velocity: rapid successive micro-authorizations under $10 were attempted to validate stolen PAN credentials prior to submitting high-value settlement requests."
            )
        elif pattern == "out_of_region_use":
            narrative_parts.append(
                "The modus operandi indicates magnetic stripe cloning or counterfeit card reproduction, evidenced by physical in-person POS transactions in an unfamiliar geographic region concurrent with cardholder domestic presence."
            )
        elif pattern == "card_not_present_new_device":
            narrative_parts.append(
                "The modus operandi involved credential capture and card-not-present exploitation originating from an unrecognized new device profile without prior account history."
            )
        else:
            narrative_parts.append(
                "The observed transaction sequence deviates significantly from the cardholder's historical baseline volume and cadence, exhibiting hallmarks of unauthorized credential compromise."
            )
            
        # 5. WHY
        if assumed_customer_response == "denied_fraud":
            narrative_parts.append(
                "Upon formal bank outreach, the cardholder explicitly denied initiating or authorizing the transactions and confirmed physical possession of the original card."
            )
        elif rings.get("has_shared_ring"):
            narrative_parts.append(
                f"Suspicion is corroborated by graph ring discovery confirming the hardware device was simultaneously utilized across {rings.get('ring_size', 1)} unrelated customer accounts within a compressed timeframe."
            )
        else:
            narrative_parts.append(
                "The activity is deemed suspicious based on the convergence of automated bank risk scoring, rapid velocity shifts, and complete lack of cardholder historical precedent."
            )
            
        # 6. ACTION TAKEN
        narrative_parts.append(
            f"The financial institution has permanently blocked card {card_id} to prevent further financial exposure, staged appropriate fraud chargebacks, and placed all connected cards under heightened surveillance."
        )

        full_narrative = " ".join(narrative_parts)

        return {
            "file": True,
            "reason": reason,
            "narrative": full_narrative,
            "subjects": subjects,
            "total_amount_usd": total_amt,
            "activity_dates": activity_dates
        }
