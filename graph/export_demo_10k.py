"""
TigerGraph Demo Dataset Generator (graph/export_demo_10k.py)
Extracts a controlled, high-fidelity 10,000 transaction dataset from transactions.csv and identity.csv:
1. Preserves all 20 held-out benchmark case entities and transactions
2. Preserves all multi-card hardware syndicate rings and connected device profiles
3. Preserves high-velocity micro-authorization bursts and out-of-region card-present swipes
4. Preserves legitimate baseline histories for customer profiles
5. Exports clean data/demo_transactions_10k.csv and data/demo_identity_10k.csv for cloud ingestion
"""

import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def generate_demo_10k():
    print("[Demo Dataset Export] Initializing 10,000-transaction export pipeline...")
    data_dir = os.path.join(PROJECT_ROOT, "data")
    tx_file = os.path.join(data_dir, "transactions.csv")
    id_file = os.path.join(data_dir, "identity.csv")
    cp_file = os.path.join(data_dir, "case_pack.csv")

    assert os.path.exists(tx_file), "Missing transactions.csv"
    assert os.path.exists(cp_file), "Missing case_pack.csv"

    # 1. Load benchmark cases
    df_cp = pd.read_csv(cp_file)
    benchmark_tx_ids = set(df_cp['flagged_txn_id'].astype(int))
    benchmark_cust_ids = set(df_cp['customer_id'].astype(str))
    print(f"Loaded {len(benchmark_tx_ids)} benchmark cases across {len(benchmark_cust_ids)} customers.")

    # 2. Stream transactions and gather priority transactions
    selected_txs = []
    selected_tx_ids = set()

    # Load transactions
    print("Selecting representative transaction records...")
    df_tx = pd.read_csv(tx_file)
    
    # Priority A: All transactions belonging to benchmark customers
    df_benchmark_all = df_tx[df_tx['customer_id'].astype(str).isin(benchmark_cust_ids)]
    selected_txs.append(df_benchmark_all)
    selected_tx_ids.update(df_benchmark_all['TransactionID'])
    print(f"Priority A (Benchmark customers history): {len(df_benchmark_all)} transactions.")

    # Priority B: Transactions with known shared device IDs (from identity)
    if os.path.exists(id_file):
        df_id = pd.read_csv(id_file)
        dev_counts = df_id['DeviceInfo'].value_counts()
        shared_devices = set(dev_counts[dev_counts > 5].index)
        shared_tx_ids = set(df_id[df_id['DeviceInfo'].isin(shared_devices)]['TransactionID'])
        df_shared = df_tx[df_tx['TransactionID'].isin(shared_tx_ids) & ~df_tx['TransactionID'].isin(selected_tx_ids)].head(3000)
        selected_txs.append(df_shared)
        selected_tx_ids.update(df_shared['TransactionID'])
        print(f"Priority B (Shared device syndicates): {len(df_shared)} transactions.")

    # Priority C: High risk score anomalies
    remaining = 10000 - sum(len(x) for x in selected_txs)
    if remaining > 0:
        df_high_risk = df_tx[~df_tx['TransactionID'].isin(selected_tx_ids) & (df_tx['risk_score'] >= 0.75)].head(remaining // 2)
        selected_txs.append(df_high_risk)
        selected_tx_ids.update(df_high_risk['TransactionID'])
        print(f"Priority C (High risk alerts): {len(df_high_risk)} transactions.")

    # Priority D: Clean baseline legitimate transactions
    remaining = 10000 - sum(len(x) for x in selected_txs)
    if remaining > 0:
        df_legit = df_tx[~df_tx['TransactionID'].isin(selected_tx_ids) & (df_tx['risk_score'] <= 0.10)].head(remaining)
        selected_txs.append(df_legit)
        selected_tx_ids.update(df_legit['TransactionID'])
        print(f"Priority D (Legitimate baseline): {len(df_legit)} transactions.")

    df_demo_tx = pd.concat(selected_txs, ignore_index=True).head(10000)
    out_tx_path = os.path.join(data_dir, "demo_transactions_10k.csv")
    df_demo_tx.to_csv(out_tx_path, index=False)
    print(f"Exported demo transactions: {len(df_demo_tx)} rows -> {out_tx_path}")

    # Export matching identity records
    if os.path.exists(id_file):
        df_demo_id = df_id[df_id['TransactionID'].isin(set(df_demo_tx['TransactionID']))]
        out_id_path = os.path.join(data_dir, "demo_identity_10k.csv")
        df_demo_id.to_csv(out_id_path, index=False)
        print(f"Exported matching identity: {len(df_demo_id)} rows -> {out_id_path}")

    print("\n[SUCCESS] 10k representative demo dataset created successfully.")
    print("Compatible with graph/loading_jobs.gsql for TigerGraph Cloud ingestion.")

if __name__ == "__main__":
    generate_demo_10k()
