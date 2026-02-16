"""
Shiprocket Workflow Module
===========================
Callable functions for shipping workflow (Streamlit-compatible)
"""

import os
import requests
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import streamlit as st


def get_credentials():
    """Get Shiprocket credentials from secrets or env."""
    # Try Streamlit secrets first (when running in Streamlit)
    try:
        if hasattr(st, 'secrets') and hasattr(st.secrets, '__getitem__') and 'shiprocket' in st.secrets:
            email = st.secrets['shiprocket'].get('email')
            password = st.secrets['shiprocket'].get('password')
            api_key = st.secrets['shiprocket'].get('api_key')
            
            if api_key:
                return {'api_key': api_key}
            elif email and password:
                return {'email': email, 'password': password}
    except:
        pass  # Streamlit not available or secrets not configured
    
    # Fallback to environment variables
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Try to load from credentials file
    creds_path = Path("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
    if creds_path.exists():
        load_dotenv(creds_path)
    else:
        load_dotenv()  # Load from .env in current directory
    
    api_key = os.getenv('SHIPROCKET_API_KEY')
    if api_key:
        return {'api_key': api_key}
    
    email = os.getenv('SHIPROCKET_EMAIL')
    password = os.getenv('SHIPROCKET_PASSWORD')
    if email and password:
        return {'email': email, 'password': password}
    
    return None


def authenticate():
    """Get auth token."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    creds = get_credentials()
    
    if not creds:
        raise Exception("No credentials found")
    
    # If API key, return it directly
    if 'api_key' in creds:
        return creds['api_key']
    
    # Otherwise, authenticate with email/password
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json={"email": creds['email'], "password": creds['password']})
    response.raise_for_status()
    return response.json()["token"]


def get_new_orders(token, days=7):
    """Fetch NEW orders."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    url = f"{BASE_URL}/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    params = {
        "filter": "new",
        "per_page": 100,
        "from": from_date,
        "to": to_date
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    # Filter to only truly NEW orders (not shipped, not canceled)
    all_orders = response.json().get("data", [])
    
    # Status code 1 = NEW (ready to ship)
    # Exclude: 5 = CANCELED, 18 = CANCELLATION REQUESTED, 4 = PICKUP SCHEDULED (already shipped)
    new_orders = []
    for order in all_orders:
        status = order.get("status", "")
        status_code = order.get("status_code")
        
        # Only include if status is "NEW"
        if status == "NEW":
            # Check if already has shipment with AWB (already shipped)
            shipments = order.get("shipments", [])
            if shipments:
                shipment = shipments[0]
                awb = shipment.get("awb_code")
                if not awb:  # No AWB = not shipped yet
                    new_orders.append(order)
            else:
                new_orders.append(order)
    
    return new_orders


def ship_order(token, shipment_id):
    """Ship single order."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    url = f"{BASE_URL}/courier/assign/awb"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json={"shipment_id": shipment_id})
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text


def run_shipping_workflow():
    """
    Run complete shipping workflow (Streamlit-compatible).
    Returns dict with results.
    """
    result = {
        "total_orders": 0,
        "shipped": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "details": []
    }
    
    try:
        # Authenticate
        token = authenticate()
        
        # Get NEW orders
        orders = get_new_orders(token)
        result["total_orders"] = len(orders)
        
        if not orders:
            result["errors"].append("No NEW orders found (all orders are either shipped, canceled, or not ready)")
            return result
        
        # Ship each order
        for order in orders:
            order_id = order.get("id")
            
            # Get shipment ID
            shipments = order.get("shipments", [])
            if not shipments:
                result["skipped"] += 1
                result["details"].append(f"Order #{order_id}: No shipment created yet")
                continue
            
            shipment_id = shipments[0].get("id")
            if not shipment_id:
                result["skipped"] += 1
                result["details"].append(f"Order #{order_id}: No shipment ID")
                continue
            
            # Try to ship
            success, response = ship_order(token, shipment_id)
            
            if success:
                result["shipped"] += 1
                awb = response.get("response", {}).get("data", {}).get("awb_assign_status", "Unknown")
                result["details"].append(f"Order #{order_id}: ✅ Shipped (AWB assigned)")
            else:
                result["failed"] += 1
                error_msg = str(response)[:100]  # Limit error message length
                result["details"].append(f"Order #{order_id}: ❌ Failed - {error_msg}")
        
        # Summary message
        if result["shipped"] == 0 and result["total_orders"] > 0:
            result["errors"].append(f"Found {result['total_orders']} NEW orders but could not ship any")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Workflow error: {str(e)}")
        import traceback
        result["errors"].append(traceback.format_exc())
        return result
