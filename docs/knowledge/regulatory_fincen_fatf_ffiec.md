# Regulatory Guidance: FinCEN SAR Standards, FATF & FFIEC Typologies

## 1. FinCEN Suspicious Activity Report (SAR) Narrative Standards

Under 31 U.S.C. 5318(g) and FinCEN regulations, financial institutions must file a Suspicious Activity Report (SAR) when detecting known or suspected violations of federal law, suspicious transactions related to money laundering, or fraudulent activity exceeding prescribed thresholds (\$1,000 for identified suspects, \$5,000 for unidentified suspects, or immediately for systemic abuse).

### 1.1 The Six Mandatory Narrative Questions
The SAR narrative must stand entirely on its own. Regulators, law enforcement, and prosecutors must be able to understand the entire fraudulent scheme without requesting internal work papers. The narrative must succinctly and comprehensively answer:

1. **WHO**: Identify all parties involved. This includes the cardholder/victim (`customer_id`, `card_id`), any identified fraudsters or aliases, associated digital identities (IP addresses, device fingerprints, email handles), and recipient merchants.
2. **WHAT**: Quantify the illicit conduct and financial instrument. Specify transaction IDs, exact dollar values in USD, payment card types, and total exposure.
3. **WHEN**: Detail chronological milestones. State the date and time of the initial suspicious transaction, the duration of the fraud episode, the date the alert fired, and the timestamp of cardholder contact.
4. **WHERE**: Identify the digital and geographic loci. Document the physical billing regions (`addr1`), origin country codes (`addr2`), merchant digital storefronts, and internet protocol / proxy endpoints.
5. **HOW**: Explain the operational mechanics of the compromise. Describe the method of exploitation (e.g. automated card testing, counterfeit card cloning, unauthorized credential harvesting, or proxy routing).
6. **WHY**: Articulate why the activity is suspicious and warrants regulatory intervention. Detail why the conduct deviates from normal profile baselines, how it breaches bank risk policies, and why law enforcement interest is justified.

### 1.2 Structure & Length Requirements
- Length: 6 to 12 coherent, professional, objective sentences.
- Tone: Factual, forensic, neutral. Avoid speculation; state facts confirmed by graph traversal and customer verification.

---

## 2. FATF (Financial Action Task Force) Guidance on Cyber-Enabled Fraud

- **Rapid Fund Displacement**: Fraud syndicates rapidly move illicit funds through multiple linked accounts or intermediary digital payment mechanisms within minutes of initial compromise.
- **Mule Networks & Shared Endpoints**: Syndicates frequently use single physical devices or commercial VPNs/proxies to manage multiple unrelated accounts simultaneously.
- **Threshold Structuring**: Breaking unauthorized transactions into smaller amounts to evade automated velocity thresholds.

---

## 3. FFIEC (Federal Financial Institutions Examination Council) BSA/AML Red Flags

- **Velocity & Temporal Red Flags**:
  - High volume of transactions occurring within an unusually compressed timeframe.
  - Transactions initiated outside normal operational hours or during unusual dormancy periods.
- **Geographic Red Flags**:
  - Sudden geographical transitions without reasonable travel intervals (impossible velocity).
  - Out-of-profile cross-border transactions involving high-risk jurisdiction codes.
- **Identity & Authentication Red Flags**:
  - Multiple cards accessed from identical device footprints or shared proxy nodes.
  - Repeated failed authentication attempts (`match_status` failure) followed by sudden high-value transactions.
