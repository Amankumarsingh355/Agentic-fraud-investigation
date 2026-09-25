"""
TigerGraph Data Ingestion Runner
Loads transactions, identity, closed cases, and benchmark cases into TigerGraph.
Supports live TigerGraph connection via pyTigerGraph with fallback validation.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))

# Load configuration from .env if present
load_dotenv()

TG_HOST = os.getenv("TG_HOST", "http://127.0.0.1")
TG_GRAPHNAME = os.getenv("TG_GRAPHNAME", "FraudGraph")
TG_USERNAME = os.getenv("TG_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TG_PASSWORD", "tigergraph")
TG_API_TOKEN = os.getenv("TG_API_TOKEN", "")

def connect_tigergraph():
    try:
        import pyTigerGraph as tg
        print(f"Connecting to TigerGraph at {TG_HOST} (Graph: {TG_GRAPHNAME})...")
        conn = tg.TigerGraphConnection(
            host=TG_HOST,
            graphname=TG_GRAPHNAME,
            username=TG_USERNAME,
            password=TG_PASSWORD,
            apiToken=TG_API_TOKEN if TG_API_TOKEN else None
        )
        # Test connection
        res = conn.gsql("ls")
        print("Connected successfully to TigerGraph!")
        return conn
    except Exception as e:
        print(f"Live TigerGraph connection not established: {e}")
        return None

def deploy_schema(conn):
    if not conn:
        print("No live connection; skipping live schema deployment.")
        return
    schema_path = os.path.join("graph", "schema.gsql")
    print(f"Deploying schema from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_gsql = f.read()
    res = conn.gsql(schema_gsql)
    print("Schema deployed successfully.")
    print(res[:300])

def run_loading_jobs(conn):
    if not conn:
        print("No live connection; executing offline validation instead.")
        from graph.validate_ingestion import run_validation
        return run_validation()
    
    loading_path = os.path.join("graph", "loading_jobs.gsql")
    print(f"Deploying loading jobs from {loading_path}...")
    with open(loading_path, "r", encoding="utf-8") as f:
        jobs_gsql = f.read()
    res = conn.gsql(jobs_gsql)
    print("Loading jobs created successfully.")
    
    # Run the loading jobs with data files
    data_dir = os.path.abspath("data")
    tx_file = os.path.join(data_dir, "transactions.csv")
    id_file = os.path.join(data_dir, "identity.csv")
    cc_file = os.path.join(data_dir, "closed_cases_history.csv")
    bp_file = os.path.join(data_dir, "case_pack.csv")
    
    print(f"Executing load_transactions for {tx_file}...")
    conn.runLoadingJobWithFile(tx_file, "txn_file", "load_transactions")
    
    print(f"Executing load_identity for {id_file}...")
    conn.runLoadingJobWithFile(id_file, "id_file", "load_identity")
    
    print(f"Executing load_closed_cases for {cc_file}...")
    conn.runLoadingJobWithFile(cc_file, "cc_file", "load_closed_cases")
    
    print(f"Executing load_benchmark_cases for {bp_file}...")
    conn.runLoadingJobWithFile(bp_file, "bp_file", "load_benchmark_cases")
    
    print("All loading jobs completed successfully.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TigerGraph Ingestion Runner")
    parser.add_argument("--deploy-schema", action="store_true", help="Deploy schema.gsql")
    parser.add_argument("--load-data", action="store_true", help="Run loading jobs")
    parser.add_argument("--validate", action="store_true", help="Run integrity validations")
    args = parser.parse_args()
    
    conn = connect_tigergraph()
    
    if args.deploy_schema:
        deploy_schema(conn)
    if args.load_data:
        run_loading_jobs(conn)
    if args.validate or (not args.deploy_schema and not args.load_data):
        from graph.validate_ingestion import run_validation
        run_validation()
