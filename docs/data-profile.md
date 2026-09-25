# Data Profile: HHGOA_IEEE Fraud Investigation Dataset

This document provides a thorough, statistical, and structural profile of all data assets in the HHGOA_IEEE dataset, covering distributions, data types, cardinality, missingness, entity relationships, and operational context.

---

## 1. Dataset Overview

| File | Rows | Columns | Disk Size | Primary Key / Joins | Core Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `transactions.csv` | 590,742 | 397 | ~675 MB | `TransactionID` | Complete card transaction stream over 6 months (July–Dec 2016) |
| `identity.csv` | 144,432 | 41 | ~26.7 MB | `TransactionID` (1:1 with online txns) | Device and network identity signals for online transactions |
| `closed_cases_history.csv` | 5,565 | 15 | ~2.7 MB | `case_id` | Historical investigations (July–Oct 2016), serving as Case Memory |
| `case_pack.csv` | 20 | 8 | ~3.5 KB | `case_id` | Benchmark evaluation cases (Nov–Dec 2016) |
| `README.md` | 473 lines | - | ~38.6 KB | - | Problem brief, rules, policy, typologies, answer format |

---

## 2. Transactions Profile (`transactions.csv`)

### 2.1 Dimensions & Temporal Range
- **Total Records**: 590,742 transactions
- **Total Attributes**: 397 columns (393 original Vesta + `customer_id`, `ts`, `channel`, `risk_score`)
- **Temporal Window**: `2016-07-02 00:02:21` to `2016-12-31 23:58:54` (183 calendar days)

### 2.2 Financial Amounts (`TransactionAmt`)
- **Min**: \$0.27
- **25th Percentile**: \$43.32
- **Median**: \$68.86
- **Mean**: \$135.08
- **75th Percentile**: \$125.00
- **Max**: \$31,937.38
- *Operational Insight*: Distinct micro-transactions ($0.27 to $5.00) correlate heavily with card testing sequences.

### 2.3 Channel & Product Code Distribution
| ProductCD | Channel | Record Count | Percentage | Device Record in `identity.csv`? |
| :--- | :--- | :--- | :--- | :--- |
| `W` | `in_person` | 439,670 | 74.43% | No (Card-present POS/ATM) |
| `C` | `online` | 68,721 | 11.63% | Yes |
| `R` | `online` | 37,699 | 6.38% | Yes |
| `H` | `online` | 33,024 | 5.59% | Yes |
| `S` | `online` | 11,628 | 1.97% | Yes |
| **Total** | - | **590,742** | **100.0%** | **144,432 online records** |

### 2.4 Customer & Card Cardinality
- **Distinct Customers (`customer_id`)**: 13,553
- **Mean Transactions per Customer**: 43.58 (Range: 1 to 14,932 txns)
- **Payment Networks (`card4`)**:
  - `visa`: 384,887 (65.15%)
  - `mastercard`: 189,298 (32.04%)
  - `american express`: 8,328 (1.41%)
  - `discover`: 6,652 (1.13%)
  - `Missing (NaN)`: 1,577 (0.27%)
- **Card Types (`card6`)**:
  - `debit`: 440,091 (74.50%)
  - `credit`: 149,035 (25.23%)
  - `debit or credit`: 30 (0.01%)
  - `charge card`: 15 (<0.01%)
  - `Missing (NaN)`: 1,571 (0.27%)

### 2.5 Geography & Billing Regions
- **Billing Regions (`addr1`)**: 332 unique regional codes. Top regions account for 60%+ of volume.
- **Countries (`addr2`)**: 74 unique country codes.
  - Domestic (`addr2 = 87`): 520,643 transactions (88.13%).
  - Foreign / Out-of-country: 70,099 transactions (11.87%).

### 2.6 Digital Footprints (Email Domains)
- **Purchaser Domains (`P_emaildomain`)**: 59 unique domains (94,480 nulls). Top: `gmail.com` (228k), `yahoo.com` (100k), `anonymous.com` (51k), `hotmail.com` (45k).
- **Recipient Domains (`R_emaildomain`)**: 60 unique domains (453,289 nulls). Top: `gmail.com` (57k), `hotmail.com` (23k), `anonymous.com` (20k).

### 2.7 Bank Risk Score Distribution (`risk_score`)
- **Min**: 0.01
- **10th Percentile**: 0.02
- **25th Percentile**: 0.05
- **50th Percentile (Median)**: 0.12
- **75th Percentile**: 0.22
- **90th Percentile**: 0.38
- **95th Percentile**: 0.58
- **99th Percentile**: 0.83
- **Max**: 0.99
- *Key Policy Caveat*: The risk score is an input signal, never a ground truth verdict. Transactions with risk scores >0.85 frequently turn out legitimate, whereas low scores (<0.10) can harbor subtle account takeovers.

---

## 3. Identity Profile (`identity.csv`)

### 3.1 Overview
- **Total Records**: 144,432 (joined on `TransactionID` with online transactions).
- **Total Attributes**: 41 columns (`id_01` to `id_38`, `DeviceType`, `DeviceInfo`).

### 3.2 Device Types & Hardware
- **DeviceType**:
  - `desktop`: 85,204 (58.99%)
  - `mobile`: 55,801 (38.63%)
  - `Missing`: 3,427 (2.37%)
- **Top DeviceInfo Vendors/OS**:
  - `Windows`: 47,741
  - `iOS Device`: 19,805
  - `MacOS`: 12,579
  - `Trident/7.0`: 7,446
  - `SM-G*` / Android handsets: ~15,000+

### 3.3 Device Trust & Network Signals
- **Device Status (`id_15`)**:
  - `Found` (Known, recurring device): 67,773 (46.92%)
  - `New` (First time observed for account): 61,754 (42.76%)
  - `Unknown`: 11,653 (8.07%)
  - `Missing`: 3,252 (2.25%)
- **Proxy Status (`id_23`)**:
  - `Missing (Direct/Standard)`: 139,144 (96.34%)
  - `IP_PROXY:TRANSPARENT`: 3,492 (2.42%)
  - `IP_PROXY:ANONYMOUS`: 1,185 (0.82%)
  - `IP_PROXY:HIDDEN`: 611 (0.42%)
  - *High Risk Indicator*: An anonymous or hidden proxy combined with `id_15 = 'New'` strongly elevates fraud probability.

### 3.4 Composite DeviceProfile
By compounding `DeviceInfo | OS (id_30) | Browser (id_31) | Screen (id_33)`:
- Total unique profiles: **9,706 distinct DeviceProfiles**.
- Shared profiles across multiple cards provide direct graph evidence for fraud rings and card-testing syndicates.

---

## 4. Closed Cases Profile (`closed_cases_history.csv`)

### 4.1 Volume & Time Window
- **Total Records**: 5,565 closed investigations.
- **Period**: July 2016 through October 2016.
- **Unique Customers Involved**: 1,892.

### 4.2 Investigation Outcomes & Typologies
| Pattern | Outcome | Case Count | Mean Exposure ($) | Report Filed (`FILE_REPORT`) |
| :--- | :--- | :--- | :--- | :--- |
| `card_not_present_fraud` | `confirmed_fraud` | 1,404 | \$356.12 | 142 |
| `account_takeover` | `confirmed_fraud` | 1,205 | \$482.30 | 118 |
| `card_not_present_new_device` | `confirmed_fraud` | 1,076 | \$391.84 | 88 |
| `out_of_region_use` | `confirmed_fraud` | 955 | \$289.45 | 41 |
| `none` (Cleared / False Alarm) | `cleared` | 900 | \$0.00 | 0 |
| `card_testing` | `confirmed_fraud` | 16 | \$214.50 | 5 |
| `undocumented` | `confirmed_fraud` | 9 | \$1,489.10 | 3 |
| **Total** | - | **5,565** | **\$372.40** | **397 (7.13%)** |

### 4.3 Financial Exposure Breakdown
- **Minimum**: \$0.00 (all 900 cleared cases)
- **25th Percentile**: \$34.52
- **Median**: \$117.09
- **Mean**: \$372.40
- **75th Percentile**: \$323.82
- **Maximum**: \$35,031.56

### 4.4 Actions Taken Frequency
- `CREATE_CASE`: 4,665 (All confirmed fraud cases)
- `BLOCK_CARD`: 4,665 (All confirmed fraud cases)
- `VERIFY_WITH_CUSTOMER`: 900 (Preceded all cleared cases)
- `CLOSE_NO_FRAUD`: 900 (All cleared cases)
- `FILE_REPORT`: 397 (Cases meeting regulatory thresholds: exposure > $1,000, syndicated rings, or undocumented abuse)

---

## 5. Benchmark Case Pack Profile (`case_pack.csv`)

### 5.1 Volume & Breakdown
- **Total Cases**: 20 (held-out benchmark).
- **Time Window**: November 11, 2016 through December 29, 2016.
- **Triggers**:
  - `risk_score`: 11 cases (Scores ranging from 0.52 to 0.90)
  - `customer_report`: 8 cases (Amounts disputed from $30.02 to $482.12)
  - `analyst_request`: 1 case (HHG-014: shared device investigation)

### 5.2 Case Registry
| Case ID | Opened Timestamp | Trigger Type | Flagged Txn | Card ID | Customer ID | Initial Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HHG-001` | 2016-12-05 01:55:28 | `risk_score` | 3514030 | C12382-K1 | C12382 | 0.61 |
| `HHG-002` | 2016-11-22 23:27:07 | `risk_score` | 3478782 | C11891-K1 | C11891 | 0.79 |
| `HHG-003` | 2016-12-10 15:01:21 | `customer_report` | 3530164 | C08623-K2 | C08623 | - |
| `HHG-004` | 2016-12-29 07:53:54 | `customer_report` | 3583227 | C08106-K1 | C08106 | - |
| `HHG-005` | 2016-12-08 03:38:37 | `risk_score` | 3523199 | C02923-K1 | C02923 | 0.54 |
| `HHG-006` | 2016-11-22 02:30:00 | `customer_report` | 3476682 | C07297-K1 | C07297 | - |
| `HHG-007` | 2016-12-05 03:46:14 | `risk_score` | 3514948 | C09933-K2 | C09933 | 0.87 |
| `HHG-008` | 2016-12-20 03:08:56 | `customer_report` | 3558054 | C13171-K2 | C13171 | - |
| `HHG-009` | 2016-12-28 17:10:53 | `customer_report` | 3581141 | C08299-K1 | C08299 | - |
| `HHG-010` | 2016-12-02 18:18:27 | `risk_score` | 3506725 | C10434-K1 | C10434 | 0.90 |
| `HHG-011` | 2016-12-29 06:27:44 | `customer_report` | 3583368 | C11923-K2 | C11923 | - |
| `HHG-012` | 2016-12-18 05:00:31 | `risk_score` | 3553342 | C05876-K2 | C05876 | 0.55 |
| `HHG-013` | 2016-12-09 05:39:29 | `risk_score` | 3526826 | C07671-K2 | C07671 | 0.76 |
| `HHG-014` | 2016-11-22 20:11:00 | `analyst_request` | 3478561 | C13487-K1 | C13487 | - |
| `HHG-015` | 2016-11-17 19:03:36 | `risk_score` | 3464869 | C03042-K1 | C03042 | 0.77 |
| `HHG-016` | 2016-12-12 01:39:08 | `customer_report` | 3534820 | C09988-K1 | C09988 | - |
| `HHG-017` | 2016-11-12 00:46:24 | `risk_score` | 3450629 | C04570-K1 | C04570 | 0.57 |
| `HHG-018` | 2016-11-27 14:41:26 | `customer_report` | 3491361 | C02354-K2 | C02354 | - |
| `HHG-019` | 2016-12-01 22:28:53 | `risk_score` | 3503878 | C07987-K2 | C07987 | 0.90 |
| `HHG-020` | 2016-12-03 12:04:26 | `risk_score` | 3509359 | C12265-K2 | C12265 | 0.52 |

---

## 6. Profile of Knowledge Documents

### 6.1 Bank Fraud Policy Document (v1.0)
- **14 Prescribed Actions**:
  - Passive / Non-impact: `ALLOW_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `GENERATE_REPORT`, `CREATE_CASE`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`
  - Active verification: `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`
  - Restrictive / Blocking: `DECLINE_TRANSACTION`, `BLOCK_CARD`, `BLOCK_ALL_CARDS`, `FILE_REPORT`
- **Approval Routes**:
  - `auto`: Autonomous execution by agent.
  - `L1` (Team Lead): Single authorizations declined, card blocks when loss $\le \$2,500$.
  - `L2` (Fraud Manager): Card blocks when loss $>\$2,500$, all total account blocks (`BLOCK_ALL_CARDS`), and all regulatory filings (`FILE_REPORT`).

### 6.2 The Five Fraud Patterns Summary
1. `card_testing`: $\ge 3$ micro auths (<$5) online within 60 mins $\rightarrow$ followed by large transaction.
2. `card_not_present_fraud`: Velocity spike of 2-4 transactions within 48 hours with abnormal product codes.
3. `card_not_present_new_device`: Same as above + `id_15 = 'New'` and/or proxy flags in `identity.csv`.
4. `out_of_region_use`: Card-present `in_person` transactions in novel `addr1` concurrent with home region spend.
5. `account_takeover`: Disjoint channels, anomalous devices, mismatched metadata (`M1-M9`).

### 6.3 Regulatory References Profile
- **FinCEN SAR Guidance**: Requires standalone 6–12 sentence narrative capturing:
  - **Who**: Cardholder, compromise suspect, merchant, device.
  - **What**: Exact unauthorized transactions and loss totals.
  - **When**: Start and end timestamps.
  - **Where**: Billing regions, digital IP/proxy, channels.
  - **How**: Typology mechanics (testing, CNP compromise, credential reuse).
  - **Why**: Justification for suspicion and policy breach.
- **FATF Typologies**: Cyber-enabled fraud, money mule accounts, rapid fund displacement.
- **FFIEC Red Flags**: Abrupt geographic jumps, velocity bursts, anomalous authorization failures.
