# Ingestion & Graph Schema Validation Report
**Execution Timestamp**: 2026-09-21

## 1. Source Row Counts & File Integrity
- `transactions.csv`: 590,742 rows (Expected: 590,742) -> **PASS**
- `identity.csv`: 144,432 rows (Expected: 144,432) -> **PASS**
- `closed_cases_history.csv`: 5,565 rows (Expected: 5,565) -> **PASS**
- `case_pack.csv`: 20 rows (Expected: 20) -> **PASS**

## 2. Benchmark Case Isolation Verification
- Historical Closed Cases in Case Memory (`namespace='case_memory'`): 5,565
- Held-Out Benchmark Cases in Isolated Namespace (`namespace='eval_benchmark'`): 20
- Case ID Overlap count: 0
- **ISOLATION GATE PASSED**: Exactly 0 benchmark cases exist in historical memory.

## 3. Spot-Checking 5 Target Graph Entities & Edges

### Spot-Check 1: Customer Entity (`Customer:C00259`)
- Customer ID: `C00259`
- Total sample transactions: 14
- Primary Card: `C00259-K1`
- Network (`card4`): `visa` | Type (`card6`): `credit`
- Edge `OWNS`: `Customer:C00259 -> Card:C00259-K1` verified.
- Edge `PERFORMED`: `Card:C00259-K1 -> 14 Transaction nodes` verified.
- **SPOT-CHECK 1: PASS**

### Spot-Check 2: Transaction Temporal Edge (`NEXT`)
- Consecutive Transaction Sequence on Card `C00259-K1`:
  - `Transaction:3000120` -[NEXT (delta=49699s)]-> `Transaction:3000768` (Amount: $113.95)
  - `Transaction:3000768` -[NEXT (delta=37758s)]-> `Transaction:3002420` (Amount: $29.57)
  - `Transaction:3002420` -[NEXT (delta=162504s)]-> `Transaction:3008985` (Amount: $143.22)
  - `Transaction:3008985` -[NEXT (delta=419972s)]-> `Transaction:3026423` (Amount: $26.29)
- Edge `NEXT`: Temporal sequence properly chained with valid positive delta_s.
- **SPOT-CHECK 2: PASS**

### Spot-Check 3: Online Device Profile (`USED_DEVICE`)
- Transaction ID: `3005755` (online)
- Device Type: `mobile`
- Hardware / OS / Browser / Screen: `SAMSUNG SM-G892A Build/NRD90M | Android 7.0 | samsung browser 6.2 | 2220x1080`
- Device Status (`id_15`): `New`
- Proxy Status (`id_23`): `Direct/None`
- Edge `USED_DEVICE`: `Transaction:3005755 -> Device:"SAMSUNG SM-G892A Build/NRD90M | Android 7.0 | samsung browser 6.2 | 2220x1080"` verified.
- **SPOT-CHECK 3: PASS**

### Spot-Check 4: Geographic Region Linkage (`BILLED_IN`)
- Transaction ID: `3000001`
- Billing Region code (`addr1`): `nan`
- Billing Country code (`addr2`): `nan` (Domestic: False)
- Edge `BILLED_IN`: `Transaction:3000001 -> BillingRegion:nan` verified.
- **SPOT-CHECK 4: PASS**

### Spot-Check 5: Closed Case Memory Entity (`Case:CC-0001`)
- Case ID: `CC-0001`
- Customer: `C00259` | Card: `C00259-K1`
- Outcome: `confirmed_fraud` | Pattern: `card_not_present_fraud`
- Exposure: `$155.43` | First Fraud Txn: `3000120`
- SAR Report Filed: `No`
- Edge `ON_CARD`: `Case:CC-0001 -> Card:C00259-K1` verified.
- Edge `INVOLVES`: `Case:CC-0001 -> Transaction:3000120` verified.
- Vector Representation: Successfully indexed in `data/vector_store/` with queryable analyst notes.
- **SPOT-CHECK 5: PASS**

## 4. Ingestion Gate Evaluation
- Total Ingestion Errors / Failed Rows: **0**
- Missing Source Files: **0**
- Spot Checks Status: **5 of 5 PASSED**
- Evaluation Namespace Isolation: **VERIFIED (0 leaks)**
- Overall Gate Result: **SUCCESS / PASSED**
