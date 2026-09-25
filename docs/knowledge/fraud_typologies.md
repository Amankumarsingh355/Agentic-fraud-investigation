# Fraud Typologies & Detection Indicators Manual

This document details the behavioral indicators, graph structural patterns, and policy mappings for fraud typologies in the card payments domain.

---

## Typology 1: Card Testing (`card_testing`)
- **Mechanism**: Fraudsters acquire compromised payment card credentials and test whether the card is active and valid before committing high-value theft.
- **Structural Indicators**:
  - Sequence of 3 or more micro-authorizations, typically under \$5.00 (e.g., \$0.95, \$1.10, \$2.40).
  - Transactions occur online (`channel = 'online'`, `ProductCD` in `['C', 'R', 'H', 'S']`).
  - Time elapsed between testing transactions is tight, typically under 60 minutes.
  - Followed closely by an attempt or clearance of a significantly larger transaction (often >\$100 or \$250).
- **Graph Traversal Pattern**:
  - Traversal along `Card -> PERFORMED -> Transaction -> NEXT -> Transaction` within 1 hour where amount $< \$5.00$ and count $\ge 3$.
- **Policy Response**:
  - Rule R5: Recommend `DECLINE_TRANSACTION` and `STEP_UP_AUTH`. If high-value spend has cleared, recommend `BLOCK_CARD`.

---

## Typology 2: Card-Not-Present Fraud (`card_not_present_fraud`)
- **Mechanism**: Fraudulent online or telephone purchases conducted using stolen card information without physical possession of the card.
- **Structural Indicators**:
  - Channel is strictly online (`ProductCD` != 'W').
  - Burst velocity: 2 to 4 unauthorized transactions clustered within 24 to 48 hours.
  - Out-of-character spending amounts and merchant product codes that contrast sharply with the cardholder's baseline transaction history.
  - Absence of in-person card-present transactions in the same timeframe.
- **Graph Traversal Pattern**:
  - High degree of divergence from customer's historical 30-day baseline product code distribution and average transaction amount.
- **Policy Response**:
  - Rules R1 to R4: Single transactions are ambiguous; recommend `VERIFY_WITH_CUSTOMER` before blocking. Upon cardholder denial, escalate to `BLOCK_CARD` and `CREATE_CASE`.

---

## Typology 3: Card-Not-Present via New Device (`card_not_present_new_device`)
- **Mechanism**: Card-not-present fraud executed from an unauthenticated hardware endpoint, often accompanied by anonymizing infrastructure.
- **Structural Indicators**:
  - All indicators of Pattern 2 present.
  - Identity signal `id_15` is explicitly marked as `New` for this account profile.
  - Identity signal `id_23` frequently indicates `IP_PROXY:TRANSPARENT`, `IP_PROXY:ANONYMOUS`, or `IP_PROXY:HIDDEN`.
  - Discrepancy between device OS/browser and historical customer sessions.
- **Graph Traversal Pattern**:
  - `Transaction -> USED_DEVICE -> Device` where `is_new == TRUE` and device has 0 prior connections to customer's historical transactions.
- **Policy Response**:
  - Elevates fraud probability significantly above baseline CNP. However, legitimate hardware upgrades require customer verification unless corroborated by other compromised cards.

---

## Typology 4: Out-of-Region Use (`out_of_region_use`)
- **Mechanism**: Physical counterfeit card cloning or stolen physical card used in a remote geographical location while legitimate operations continue locally.
- **Structural Indicators**:
  - Channel is in-person (`channel = 'in_person'`, `ProductCD = 'W'`).
  - Billing region `addr1` is entirely novel and distinct from the customer's home region (`home_region`).
  - Key signature: Concurrent or near-simultaneous physical transactions occurring in the customer's home region (impossible travel velocity).
  - *Distinction*: Multi-day continuous spending in a single novel region without home activity denotes legitimate travel, not card cloning.
- **Graph Traversal Pattern**:
  - `Transaction -> BILLED_IN -> BillingRegion` where region != home region, combined with another recent transaction in home region within impossible physical travel duration.
- **Policy Response**:
  - Rules R2 and R3. Immediate confirmation required; block if customer confirms they are at home and in possession of the card.

---

## Typology 5: Account Takeover (`account_takeover`)
- **Mechanism**: Fraudulent actor gains complete unauthorized control of the cardholder's digital banking profile or credentials, enabling cross-channel exploitation.
- **Structural Indicators**:
  - Mixed-channel activity spanning both online and in-person transactions.
  - Sudden changes in purchaser email domain (`P_emaildomain`) or device profiles.
  - Mismatch flags (`M1` through `M9`) failing simultaneously.
  - Rapid succession of profile inquiries followed by balance exhaustion attempts across multiple cards owned by the customer.
- **Graph Traversal Pattern**:
  - Multi-card velocity across `Customer -> OWNS -> Card -> MADE -> Transaction` originating from a single foreign device profile.
- **Policy Response**:
  - High severity: Recommend `BLOCK_CARD`, `CREATE_CASE`, `FILE_REPORT`. If multiple customer cards are impacted, recommend `BLOCK_ALL_CARDS` under Rule R10.

---

## Typology 6: Undocumented Coordinated Abuse (`undocumented`)
- **Mechanism**: Emerging or organized syndicate schemes not fitting standard typologies, including merchant collusive rings, mule layering, and multi-customer botnets.
- **Structural Indicators**:
  - Cross-customer device convergence: Multiple unrelated customer cards sharing a single `DeviceProfile` within a tight 72-hour window.
  - Rapid sequential authorizations across different accounts targeting identical recipient domains or billing clusters.
- **Graph Traversal Pattern**:
  - 2-hop neighbor expansion: `Card_A -> MADE -> Txn -> USED_DEVICE -> Device <- USED_DEVICE <- Txn <- Card_B` where `Customer_A != Customer_B`.
- **Policy Response**:
  - Rule R9: Mandatory `CREATE_CASE`, `FILE_REPORT`, `ESCALATE_TO_ANALYST`, and `MONITOR_CONNECTED_CARDS` across all implicated accounts. Formulate an explicit description in `pattern_description`.
