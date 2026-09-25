"""
Graph Subgraph Extractor
Pulls connected subgraph entities and relationships for any transaction or customer:
Customer -> Cards -> Transactions -> Device -> BillingRegion -> Rings
"""

import os
import sys
import pandas as pd
import numpy as np

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))

class SubgraphExtractor:
    def __init__(self):
        print("Initializing SubgraphExtractor with dataset indexes...")
        # Load transactions with indexed access
        self.df_tx = pd.read_csv("data/transactions.csv", usecols=[
            'TransactionID', 'customer_id', 'ts', 'TransactionAmt', 'channel', 
            'ProductCD', 'risk_score', 'addr1', 'addr2', 'card1', 'card2', 'card4', 'card6',
            'P_emaildomain', 'R_emaildomain'
        ])
        self.df_tx['ts'] = pd.to_datetime(self.df_tx['ts'])
        self.tx_by_id = self.df_tx.set_index('TransactionID').to_dict(orient='index')
        
        # Load identity
        self.df_id = pd.read_csv("data/identity.csv")
        self.id_by_tx = self.df_id.set_index('TransactionID').to_dict(orient='index')
        
        # Precompute device profile mappings
        self.df_id_valid = self.df_id.dropna(subset=['DeviceInfo', 'id_30', 'id_31', 'id_33']).copy()
        self.df_id_valid['device_profile'] = (
            self.df_id_valid['DeviceInfo'].astype(str) + " | " +
            self.df_id_valid['id_30'].astype(str) + " | " +
            self.df_id_valid['id_31'].astype(str) + " | " +
            self.df_id_valid['id_33'].astype(str)
        )
        self.tx_to_device = dict(zip(self.df_id_valid['TransactionID'], self.df_id_valid['device_profile']))
        
        # Device to cards mapping for ring detection
        merged_dev = self.df_id_valid.merge(self.df_tx[['TransactionID', 'customer_id']], on='TransactionID')
        self.device_to_custs = merged_dev.groupby('device_profile')['customer_id'].unique().to_dict()
        print("SubgraphExtractor initialized successfully.")

    def extract_subgraph(self, transaction_id: int):
        if transaction_id not in self.tx_by_id:
            return None
            
        target = self.tx_by_id[transaction_id]
        cust_id = target['customer_id']
        anchor_dt = target['ts']
        card_id = f"{cust_id}-K1" # Primary card convention
        
        # 1. Customer history
        cust_txns = self.df_tx[self.df_tx['customer_id'] == cust_id].sort_values('ts')
        total_txns = len(cust_txns)
        total_volume = float(cust_txns['TransactionAmt'].sum())
        
        # Determine home region (mode of addr1)
        valid_regions = cust_txns['addr1'].dropna()
        home_region = float(valid_regions.mode().iloc[0]) if len(valid_regions) > 0 else np.nan
        
        # 2. Card Recent Timeline (Rolling 72 hours up to target txn)
        start_72h = anchor_dt - pd.Timedelta(hours=72)
        recent_txns = cust_txns[(cust_txns['ts'] >= start_72h) & (cust_txns['ts'] <= anchor_dt)]
        
        timeline = []
        prev_ts = None
        for _, r in recent_txns.iterrows():
            delta_s = (r['ts'] - prev_ts).total_seconds() if prev_ts is not None else 0.0
            timeline.append({
                "txn_id": int(r['TransactionID']),
                "ts": str(r['ts']),
                "amount": float(r['TransactionAmt']),
                "channel": str(r['channel']),
                "product_cd": str(r['ProductCD']),
                "risk_score": round(float(r['risk_score']), 4) if pd.notna(r['risk_score']) else None,
                "addr1": float(r['addr1']) if pd.notna(r['addr1']) else None,
                "delta_s": round(delta_s, 0)
            })
            prev_ts = r['ts']
            
        # 3. Identity & Hardware Footprint
        device_info = None
        device_profile_str = None
        is_new_device = False
        proxy_type = None
        
        if transaction_id in self.id_by_tx:
            id_data = self.id_by_tx[transaction_id]
            is_new_device = (id_data.get('id_15') == 'New')
            proxy_type = str(id_data.get('id_23')) if pd.notna(id_data.get('id_23')) else "Direct/None"
            device_profile_str = self.tx_to_device.get(transaction_id, f"{id_data.get('DeviceInfo')} | {id_data.get('id_30')} | {id_data.get('id_31')}")
            device_info = {
                "device_type": str(id_data.get('DeviceType')),
                "device_info": str(id_data.get('DeviceInfo')),
                "os": str(id_data.get('id_30')),
                "browser": str(id_data.get('id_31')),
                "screen": str(id_data.get('id_33')),
                "is_new": is_new_device,
                "proxy_status": proxy_type,
                "device_profile": device_profile_str
            }
            
        # 4. Shared Device Rings & Cross-Customer Linkages
        shared_ring = {
            "has_shared_ring": False,
            "connected_customers": [],
            "ring_size": 1
        }
        if device_profile_str and device_profile_str in self.device_to_custs:
            linked_custs = [c for c in self.device_to_custs[device_profile_str] if c != cust_id]
            if len(linked_custs) > 0:
                shared_ring["has_shared_ring"] = True
                shared_ring["connected_customers"] = linked_custs[:5] # top 5
                shared_ring["ring_size"] = len(linked_custs) + 1
                
        # 5. Pattern Signals Check
        # Card testing check: micro auths (<$10) followed by large (>=$50)
        online_recent = [t for t in timeline if t['channel'] == 'online']
        micro_txns = [t['txn_id'] for t in online_recent if t['amount'] <= 10.0]
        large_txns = [t['txn_id'] for t in online_recent if t['amount'] >= 50.0]
        is_card_testing = (len(micro_txns) >= 1 and len(large_txns) >= 1)
        
        # CNP check
        is_cnp = (len(online_recent) >= 1)
        
        # Out of region check
        is_out_of_region = False
        if target['channel'] == 'in_person' and pd.notna(target['addr1']):
            if pd.notna(home_region) and float(target['addr1']) != home_region:
                is_out_of_region = True
                
        # Account takeover check
        channels = set([t['channel'] for t in timeline])
        is_ato = is_new_device and (len(channels) > 1 or len(timeline) >= 2)
        
        # 6. Hybrid Graph Strategy: Probe Live TigerGraph Cloud vs Local Engine
        investigation_source = "local_index_fallback"
        graph_status = "degraded"
        fallback_used = True
        fallback_reason = "cloud_instance_paused"
        live_result = None

        try:
            from graph.tigergraph_tools import check_cloud_status, find_shared_devices_tool
            cloud_probe = check_cloud_status()
            if cloud_probe.get("available"):
                live_res = find_shared_devices_tool(str(cust_id))
                if live_res.get("status") == "success" and live_res.get("connected_count", 0) > 0:
                    investigation_source = "tigergraph_cloud"
                    graph_status = "live"
                    fallback_used = False
                    fallback_reason = None
                    live_result = live_res
                elif live_res.get("status") == "success":
                    # Cloud online but no connections found in cloud partition
                    investigation_source = "hybrid"
                    graph_status = "live_partial"
                    fallback_used = True
                    fallback_reason = "cloud_partition_entity_miss"
                else:
                    investigation_source = "hybrid"
                    graph_status = "degraded"
                    fallback_used = True
                    fallback_reason = live_res.get("error", "cloud_query_empty")
            else:
                investigation_source = "local_index_fallback"
                graph_status = "degraded"
                fallback_used = True
                fallback_reason = cloud_probe.get("status", "cloud_workspace_paused")
        except Exception as e:
            investigation_source = "local_index_fallback"
            graph_status = "degraded"
            fallback_used = True
            fallback_reason = f"exception: {str(e)}"

        # 7. Construct Observable Graph Forensic Chain
        connected_list = shared_ring.get("connected_customers", [])
        nodes_discovered = [f"Customer:{cust_id}", f"Card:{card_id}"]
        if device_info:
            nodes_discovered.append(f"Device:{device_info.get('device_profile')}")
        for c in connected_list:
            nodes_discovered.append(f"Customer:{c}")

        edges_discovered = [
            f"OWNS(Customer:{cust_id} -> Card:{card_id})",
            f"PERFORMED(Card:{card_id} -> Txn:{transaction_id})"
        ]
        if device_info:
            edges_discovered.append(f"USED_DEVICE(Txn:{transaction_id} -> Device:{device_info.get('device_profile')})")
        for c in connected_list:
            edges_discovered.append(f"SHARED_HARDWARE(Device -> Customer:{c})")

        graph_forensic_chain = {
            "query_executed": "findSharedDevices" if investigation_source == "tigergraph_cloud" else "find_shared_devices_hybrid",
            "source": investigation_source,
            "nodes_discovered": nodes_discovered,
            "edges_discovered": edges_discovered,
            "relationship": "SHARED_HARDWARE_RING" if shared_ring.get("has_shared_ring") else "SINGLE_USER_TOPOLOGY",
            "fraud_implication": (
                f"Multi-card syndicate nexus detected across {shared_ring.get('ring_size')} distinct cardholder accounts."
                if shared_ring.get("has_shared_ring") else "No shared hardware ring detected for this entity."
            ),
            "decision_impact": (
                "Escalates fraud probability and activates Bank Fraud Policy Rule R6."
                if shared_ring.get("has_shared_ring") else "Supports lower baseline suspicion; Rule R1 applies."
            )
        }

        return {
            "graph_metadata": {
                "investigation_source": investigation_source,
                "graph_status": graph_status,
                "fallback_used": fallback_used,
                "fallback_reason": fallback_reason,
                "engine": "TigerGraph Hybrid Engine (Savanna Cloud + Local 590k Indexed Topology)"
            },
            "graph_forensic_chain": graph_forensic_chain,
            "target_transaction": {
                "txn_id": transaction_id,
                "customer_id": cust_id,
                "card_id": card_id,
                "amount": float(target['TransactionAmt']),
                "ts": str(anchor_dt),
                "channel": str(target['channel']),
                "product_cd": str(target['ProductCD']),
                "risk_score": round(float(target['risk_score']), 4) if pd.notna(target['risk_score']) else None,
                "addr1": float(target['addr1']) if pd.notna(target['addr1']) else None,
                "addr2": float(target['addr2']) if pd.notna(target['addr2']) else None,
                "card_network": str(target.get('card4', 'unknown')),
                "card_type": str(target.get('card6', 'unknown')),
                "purchaser_email": str(target.get('P_emaildomain', 'none'))
            },
            "customer_profile": {
                "customer_id": cust_id,
                "total_historical_txns": total_txns,
                "total_historical_volume": round(total_volume, 2),
                "home_region": home_region,
                "first_seen": str(cust_txns['ts'].min()),
                "last_seen": str(cust_txns['ts'].max())
            },
            "card_timeline_72h": timeline,
            "identity_device": device_info,
            "shared_hardware_ring": shared_ring,
            "pattern_signals": {
                "card_testing": {
                    "flagged": is_card_testing,
                    "micro_count": len(micro_txns),
                    "large_count": len(large_txns)
                },
                "card_not_present": {
                    "flagged": is_cnp,
                    "online_count": len(online_recent)
                },
                "cnp_new_device": {
                    "flagged": is_cnp and is_new_device,
                    "is_new": is_new_device
                },
                "out_of_region": {
                    "flagged": is_out_of_region,
                    "current_region": target['addr1'],
                    "home_region": home_region
                },
                "account_takeover": {
                    "flagged": is_ato,
                    "mixed_channels": len(channels) > 1
                }
            }
        }

if __name__ == "__main__":
    extractor = SubgraphExtractor()
    subgraph = extractor.extract_subgraph(3514030) # HHG-001
    print("\n=== Subgraph Extraction Sample (Txn: 3514030) ===")
    print("Target Txn:", subgraph["target_transaction"])
    print("Customer Profile:", subgraph["customer_profile"])
    print("Pattern Signals:", subgraph["pattern_signals"])
    print("Timeline Events:", len(subgraph["card_timeline_72h"]))
