"""
Pattern Library Dynamic Feedback Registry
Feeds newly recognized recurring fraud patterns and suspicious entities
(devices, proxy networks, merchant vectors) back into the Phase 3 pattern library.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

REGISTRY_FILE = os.path.join("data", "pattern_registry.json")

class PatternRegistry:
    def __init__(self, registry_file: str = REGISTRY_FILE):
        self.registry_file = registry_file
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not read {self.registry_file}, creating fresh registry: {e}")
        return {
            "flagged_devices": {},
            "flagged_proxies": {},
            "novel_patterns": {},
            "last_updated": datetime.now().isoformat()
        }

    def _save_registry(self):
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        self.registry["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2)

    def register_entity(
        self,
        entity_type: str, # "device", "proxy", "pattern"
        entity_value: str,
        case_id: str,
        pattern: str,
        notes: str = ""
    ):
        """
        Registers a confirmed or strongly suspected fraudulent entity back into the library.
        """
        now_iso = datetime.now().isoformat()
        if entity_type == "device":
            store = self.registry["flagged_devices"]
        elif entity_type == "proxy":
            store = self.registry["flagged_proxies"]
        elif entity_type == "pattern":
            store = self.registry["novel_patterns"]
        else:
            return

        if entity_value in store:
            store[entity_value]["case_count"] += 1
            if case_id not in store[entity_value]["associated_cases"]:
                store[entity_value]["associated_cases"].append(case_id)
            store[entity_value]["last_flagged_at"] = now_iso
        else:
            store[entity_value] = {
                "first_case_id": case_id,
                "associated_cases": [case_id],
                "case_count": 1,
                "pattern": pattern,
                "first_flagged_at": now_iso,
                "last_flagged_at": now_iso,
                "notes": notes
            }
        self._save_registry()

    def check_entity(
        self,
        device_profile: Optional[str] = None,
        proxy_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Checks if an incoming device profile or proxy status matches previously flagged entities.
        """
        matches = []
        if device_profile and device_profile in self.registry["flagged_devices"]:
            info = self.registry["flagged_devices"][device_profile]
            matches.append({
                "entity_type": "device",
                "entity_value": device_profile,
                "first_case_id": info["first_case_id"],
                "associated_cases": info["associated_cases"],
                "pattern": info["pattern"],
                "case_count": info["case_count"],
                "risk_signal": f"Hardware signature previously confirmed fraudulent in case {info['first_case_id']}"
            })
            
        if proxy_status and proxy_status in self.registry["flagged_proxies"]:
            info = self.registry["flagged_proxies"][proxy_status]
            matches.append({
                "entity_type": "proxy",
                "entity_value": proxy_status,
                "first_case_id": info["first_case_id"],
                "associated_cases": info["associated_cases"],
                "pattern": info["pattern"],
                "case_count": info["case_count"],
                "risk_signal": f"Proxy signature previously flagged in case {info['first_case_id']}"
            })
            
        return matches

    def clear(self):
        """Resets the registry to initial empty state."""
        self.registry = {
            "flagged_devices": {},
            "flagged_proxies": {},
            "novel_patterns": {},
            "last_updated": datetime.now().isoformat()
        }
        self._save_registry()
