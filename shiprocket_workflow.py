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
    try:
        # Try Streamlit secrets first
        if hasattr(st, 'secrets') and 'shiprocket' in st.secrets:
            email = st.secrets['shiprocket'].get('email')
            password = st.secrets['shiprocket'].get('password')
            api_key = st.secrets['shiprocket'].get('api_key')
            
            if api_key:
                return {'api_key': api_key}
            elif email and password:
                return {'email': email, 'password': password}
        
        # Fallback to environment
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('SHIPROCKET_API_KEY')
        if api_key:
            return {'api_key': api_key}
        
        email = os.getenv('SHIPROCKET_EMAIL')
        password = os.getenv('SHIPROCKET_PASSWORD')
        if email and password:
            return {'email': email, 'password': password}
        
        return None
    except:
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
    new_orders = [o for o in all_orders if o.get("status_code") == 6]  # Status code 6 = NEW
    
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
        "unshipped": 0,
        "errors": []
    }
    
    try:
        # Authenticate
        token = authenticate()
        
        # Get NEW orders
        orders = get_new_orders(token)
        result["total_orders"] = len(orders)
        
        if not orders:
            result["errors"].append("No NEW orders found")
            return result
        
        # Ship each order
        for order in orders:
            shipment_id = order.get("shipments", [{}])[0].get("id") if order.get("shipments") else None
            
            if not shipment_id:
                result["unshipped"] += 1
                continue
            
            success, response = ship_order(token, shipment_id)
            
            if success:
                result["shipped"] += 1
            else:
                result["unshipped"] += 1
        
        if result["shipped"] == 0:
            result["errors"].append("No orders were shipped successfully")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Workflow error: {str(e)}")
        return result
