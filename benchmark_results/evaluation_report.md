# Benchmark Evaluation Report — TigerGraph 11-Agent Fraud Investigation System

- **Evaluated At**: 2026-09-24T13:52:22.880247+00:00
- **Total Cases**: 20 / 20 (100%)
- **Schema Compliance**: 20/20 (100.0%)
- **Fraud Verdicts**: 17 (85.0%)
- **Legitimate Clearances**: 3 (15.0%)
- **FinCEN SAR Filings**: 6 filings ($3,367.13 USD exposure)
- **Average Latency**: 0.18 seconds
- **Average Graph Tool Invocations**: 9.0

## Detailed Case Breakdown

| Case ID | Status | Verdict | Pattern | Exposure | SAR | Latency | Actions |
|---|---|---|---|---|---|---|---|
| HHG-001 | `closed_fraud` | `fraud` | `out_of_region_use` | $77.07 | False | 0.81s | CREATE_CASE, BLOCK_CARD |
| HHG-002 | `closed_fraud` | `fraud` | `card_not_present_fraud` | $292.36 | False | 0.15s | CREATE_CASE, BLOCK_CARD |
| HHG-003 | `closed_fraud` | `fraud` | `out_of_region_use` | $49.00 | False | 0.33s | CREATE_CASE, BLOCK_CARD |
| HHG-004 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $128.33 | False | 0.16s | CREATE_CASE, BLOCK_CARD |
| HHG-005 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $100.07 | True | 0.13s | CREATE_CASE, BLOCK_CARD |
| HHG-006 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $482.12 | True | 0.12s | CREATE_CASE, BLOCK_CARD |
| HHG-007 | `closed_fraud` | `fraud` | `card_not_present_fraud` | $111.92 | False | 0.14s | CREATE_CASE, BLOCK_CARD |
| HHG-008 | `closed_fraud` | `fraud` | `card_testing` | $55.68 | False | 0.12s | CREATE_CASE, BLOCK_CARD |
| HHG-009 | `closed_fraud` | `fraud` | `card_not_present_fraud` | $30.02 | False | 0.1s | CREATE_CASE, BLOCK_CARD |
| HHG-010 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $1,000.03 | True | 0.12s | CREATE_CASE, BLOCK_CARD |
| HHG-011 | `closed_fraud` | `fraud` | `card_testing` | $131.30 | False | 0.15s | CREATE_CASE, BLOCK_CARD |
| HHG-012 | `closed_legitimate` | `legitimate` | `none` | $0.00 | False | 0.12s | CLOSE_NO_FRAUD |
| HHG-013 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $35.66 | False | 0.14s | CREATE_CASE, BLOCK_CARD |
| HHG-014 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $74.96 | True | 0.11s | CREATE_CASE, FILE_REPORT |
| HHG-015 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $599.94 | True | 0.13s | CREATE_CASE, BLOCK_CARD |
| HHG-016 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $59.67 | False | 0.14s | CREATE_CASE, BLOCK_CARD |
| HHG-017 | `closed_legitimate` | `legitimate` | `none` | $0.00 | False | 0.16s | CLOSE_NO_FRAUD |
| HHG-018 | `closed_fraud` | `fraud` | `out_of_region_use` | $39.08 | False | 0.15s | CREATE_CASE, BLOCK_CARD |
| HHG-019 | `closed_fraud` | `fraud` | `card_not_present_new_device` | $99.92 | True | 0.15s | CREATE_CASE, BLOCK_CARD |
| HHG-020 | `closed_legitimate` | `legitimate` | `none` | $0.00 | False | 0.13s | CLOSE_NO_FRAUD |
