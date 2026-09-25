import os
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import pyTigerGraph as tg

from crewai.tools import tool

@tool("Find Shared Devices Tool")
def find_shared_devices_crew_tool(user_id: str) -> str:
    """
    Finds other users sharing devices with the given input user_id on TigerGraph graph database.
    Input should be a user ID string (e.g., 'USER_1').
    Returns connected users, their risk scores, and graph connections.
    """
    res = find_shared_devices_tool(user_id)
    return str(res)

# Root environment loading
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

HOST_URL = os.getenv("TIGERGRAPH_HOST")
GRAPH_NAME = os.getenv("TIGERGRAPH_GRAPH_NAME", "FraudDetectionGraph")
SECRET = os.getenv("TIGERGRAPH_SECRET")
WORKGROUP_ID = os.getenv("TG_WORKGROUP_ID") or os.getenv("TIGERGRAPH_WORKGROUP_ID")
DATABASE_ID = os.getenv("TG_DATABASE_ID") or os.getenv("TIGERGRAPH_DATABASE_ID")
USERNAME = os.getenv("TIGERGRAPH_USERNAME", "tigergraph")
PASSWORD = os.getenv("TIGERGRAPH_PASSWORD", "")

_cached_connection = None
_cloud_status_cache = None

def check_cloud_status(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Safely probes TigerGraph Cloud instance status.
    Returns clear diagnosis without crashing if Cloud workspace is paused or unreachable.
    Caches result to avoid repeated 4s network roundtrips during batch runs.
    """
    global _cloud_status_cache
    if not force_refresh and _cloud_status_cache is not None:
        return _cloud_status_cache

    if not HOST_URL:
        _cloud_status_cache = {
            "available": False,
            "status": "unconfigured",
            "message": "TIGERGRAPH_HOST is not configured in .env",
            "endpoint": None
        }
        return _cloud_status_cache

    try:
        import requests
        headers = {}
        if SECRET:
            headers["Authorization"] = f"Bearer {SECRET}"
        if WORKGROUP_ID:
            headers["X-Workgroup-Id"] = WORKGROUP_ID
        if DATABASE_ID:
            headers["X-Database-Id"] = DATABASE_ID

        url = f"{HOST_URL.rstrip('/')}/restpp/query/{GRAPH_NAME}/findSharedDevicesv2?input_user=ping"
        res = requests.get(url, headers=headers, timeout=3)
        
        if res.status_code == 200:
            _cloud_status_cache = {
                "available": True,
                "status": "online",
                "message": "TigerGraph Cloud instance is active and responding.",
                "endpoint": HOST_URL
            }
        elif "Failed to start workspace" in res.text or "Auto start is not enabled" in res.text:
            _cloud_status_cache = {
                "available": False,
                "status": "workspace_paused",
                "message": "TigerGraph Cloud workspace is stopped/paused in TG Cloud console.",
                "endpoint": HOST_URL,
                "detail": "Failed to start workspace (auto-start disabled)"
            }
        else:
            _cloud_status_cache = {
                "available": False,
                "status": "degraded",
                "message": f"TigerGraph Cloud returned HTTP {res.status_code}",
                "endpoint": HOST_URL,
                "detail": res.text[:200]
            }
    except Exception as e:
        _cloud_status_cache = {
            "available": False,
            "status": "unreachable",
            "message": f"Connection error to TigerGraph Cloud: {str(e)}",
            "endpoint": HOST_URL
        }
    return _cloud_status_cache

def get_tigergraph_connection() -> Optional[tg.TigerGraphConnection]:
    global _cached_connection
    if _cached_connection is not None:
        return _cached_connection

    if not HOST_URL:
        print("[TigerGraph] TIGERGRAPH_HOST not configured in .env.")
        return None

    cloud_check = check_cloud_status()
    if not cloud_check["available"]:
        print(f"[TigerGraph] Cloud notice ({cloud_check['status']}): {cloud_check['message']}. Using resilient local graph engine.")
        return None

    try:
        conn = tg.TigerGraphConnection(
            host=HOST_URL,
            graphname=GRAPH_NAME,
            username=USERNAME,
            password=PASSWORD,
            apiToken=SECRET
        )

        headers = {}
        if WORKGROUP_ID:
            headers["X-Workgroup-Id"] = WORKGROUP_ID
        if DATABASE_ID:
            headers["X-Database-Id"] = DATABASE_ID

        if headers:
            conn._session.headers.update(headers)
            if hasattr(conn, "_cached_auth"):
                conn._cached_auth.update(headers)

        if SECRET and hasattr(conn, "_cached_auth"):
            conn._cached_auth["Authorization"] = f"Bearer {SECRET}"

        _cached_connection = conn
        return _cached_connection

    except Exception as e:
        print(f"[TigerGraph] Connection failed: {e}")
        return None


def find_shared_devices_tool(user_id: str) -> Dict[str, Any]:
    conn = get_tigergraph_connection()
    if conn is None:
        return {
            "status": "unavailable",
            "message": "Live TigerGraph connection is not available.",
            "ConnectedUsers": []
        }

    clean_user = str(user_id).strip()
    params = {"input_user": (clean_user,)}

    try:
        result = conn.runInstalledQuery("findSharedDevices", params)
        if isinstance(result, list) and len(result) > 0:
            connected = result[0].get("ConnectedUsers", [])
            return {
                "status": "success",
                "user_id": clean_user,
                "connected_count": len(connected),
                "ConnectedUsers": connected
            }
        return {
            "status": "empty",
            "user_id": clean_user,
            "connected_count": 0,
            "ConnectedUsers": []
        }
    except Exception as e:
        return {
            "status": "error",
            "user_id": clean_user,
            "error": str(e),
            "connected_count": 0,
            "ConnectedUsers": []
        }

if __name__ == "__main__":
    conn = get_tigergraph_connection()
    if conn:
        print("Ping Test Result:", conn.ping())
        print("Connection Success!")


if __name__ == "__main__":
    conn = get_tigergraph_connection()
    if conn:
        print("Ping Test Result:", conn.ping())
        
        # Test User ID pass karo (wo user jo tumhare TigerGraph DB mein ho, e.g., 'USER_1' ya 'CUST_101')
        test_user = "USER_1"
        print(f"\nQuerying findSharedDevices for {test_user}...")
        
        res = find_shared_devices_tool(test_user)
        print("Result:", res)