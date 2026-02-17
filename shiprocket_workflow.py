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


def download_labels(token, shipment_ids):
    """Download labels for shipments."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    url = f"{BASE_URL}/courier/generate/label"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json={"shipment_id": shipment_ids})
    response.raise_for_status()
    
    label_url = response.json().get("label_url", "")
    if label_url:
        label_response = requests.get(label_url)
        return label_response.content
    return None


def schedule_pickup(token, shipment_ids):
    """Schedule pickup for shipments (one by one)."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    url = f"{BASE_URL}/courier/generate/pickup"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    success_count = 0
    for sid in shipment_ids:
        try:
            response = requests.post(url, headers=headers, json={"shipment_id": [sid]})
            if response.status_code == 200:
                success_count += 1
            time.sleep(0.2)  # Avoid rate limiting
        except:
            pass
    
    return success_count


def generate_manifest(token, shipment_ids):
    """Generate manifest."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    url = f"{BASE_URL}/manifests/generate"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json={"shipment_id": shipment_ids})
    
    if response.status_code == 200:
        manifest_url = response.json().get("manifest_url", "")
        if manifest_url:
            manifest_response = requests.get(manifest_url)
            return manifest_response.content
    return None


def find_duplicate_orders(orders):
    """
    Find duplicate orders by phone number.
    Returns (duplicates_list, unique_list, duplicate_info)
    """
    from collections import defaultdict
    
    # Group orders by phone number
    phone_groups = defaultdict(list)
    
    for order in orders:
        # Get customer phone (try multiple fields)
        phone = (
            order.get("customer_phone") or 
            order.get("billing_phone") or 
            order.get("shipping_phone") or
            ""
        )
        # Normalize phone (last 10 digits)
        phone_clean = re.sub(r'\D', '', str(phone))[-10:] if phone else ""
        
        if phone_clean:
            phone_groups[phone_clean].append(order)
        else:
            # No phone = treat as unique
            phone_groups[f"no_phone_{order.get('id')}"].append(order)
    
    duplicates = []
    unique = []
    duplicate_info = []
    
    for phone, group in phone_groups.items():
        if len(group) > 1:
            # Multiple orders from same phone = duplicates
            duplicates.extend(group)
            customer_name = group[0].get("customer_name", "Unknown")
            duplicate_info.append({
                "phone": phone,
                "customer": customer_name,
                "count": len(group),
                "order_ids": [o.get("id") for o in group]
            })
        else:
            # Single order = unique
            unique.extend(group)
    
    return duplicates, unique, duplicate_info


def run_shipping_workflow():
    """
    Run complete shipping workflow with duplicate detection.
    
    Flow:
    1. Fetch NEW orders
    2. Find duplicates (same phone number)
    3. Ship duplicates → Download labels → Save for Telegram
    4. Ship remaining unique orders
    5. Download all labels, schedule pickup, generate manifest
    
    Returns dict with results including duplicate_labels_pdf for Telegram.
    """
    result = {
        "total_orders": 0,
        "duplicate_count": 0,
        "unique_count": 0,
        "shipped": 0,
        "failed": 0,
        "skipped": 0,
        "pickup_scheduled": 0,
        "labels_downloaded": False,
        "manifest_generated": False,
        "duplicate_labels_pdf": None,  # PDF bytes for duplicates (send to Telegram)
        "duplicate_info": [],  # Details about duplicates
        "all_labels_pdf": None,  # PDF bytes for all labels
        "errors": [],
        "details": []
    }
    
    try:
        # Authenticate
        result["details"].append("🔐 Authenticating...")
        token = authenticate()
        
        # Get NEW orders
        result["details"].append("📋 Fetching NEW orders...")
        orders = get_new_orders(token)
        result["total_orders"] = len(orders)
        
        if not orders:
            result["errors"].append("No NEW orders found")
            return result
        
        result["details"].append(f"Found {len(orders)} NEW orders")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Find duplicate orders (same phone number)
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("🔍 Checking for duplicate orders...")
        duplicates, unique_orders, duplicate_info = find_duplicate_orders(orders)
        
        result["duplicate_count"] = len(duplicates)
        result["unique_count"] = len(unique_orders)
        result["duplicate_info"] = duplicate_info
        
        if duplicates:
            result["details"].append(f"⚠️ Found {len(duplicates)} DUPLICATE orders ({len(duplicate_info)} customers)")
            for info in duplicate_info:
                result["details"].append(f"  📱 {info['phone']} ({info['customer']}): {info['count']} orders")
        else:
            result["details"].append("✅ No duplicates found")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Ship DUPLICATE orders first
        # ═══════════════════════════════════════════════════════════════
        duplicate_shipped_ids = []
        
        if duplicates:
            result["details"].append("🚀 Shipping DUPLICATE orders first...")
            
            for order in duplicates:
                order_id = order.get("id")
                shipments = order.get("shipments", [])
                
                if not shipments:
                    result["skipped"] += 1
                    continue
                
                shipment_id = shipments[0].get("id")
                if not shipment_id:
                    result["skipped"] += 1
                    continue
                
                success, response = ship_order(token, shipment_id)
                
                if success:
                    result["shipped"] += 1
                    duplicate_shipped_ids.append(shipment_id)
                    result["details"].append(f"  Order #{order_id}: ✅ Shipped (DUPLICATE)")
                else:
                    result["failed"] += 1
                    result["details"].append(f"  Order #{order_id}: ❌ Failed")
            
            # Download labels for duplicates only
            if duplicate_shipped_ids:
                result["details"].append(f"📄 Downloading labels for {len(duplicate_shipped_ids)} duplicates...")
                try:
                    duplicate_labels = download_labels(token, duplicate_shipped_ids)
                    if duplicate_labels:
                        result["duplicate_labels_pdf"] = duplicate_labels
                        result["details"].append("  ✅ Duplicate labels ready for Telegram")
                except Exception as e:
                    result["details"].append(f"  ❌ Duplicate labels error: {str(e)[:50]}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Ship UNIQUE orders
        # ═══════════════════════════════════════════════════════════════
        unique_shipped_ids = []
        
        if unique_orders:
            result["details"].append(f"🚀 Shipping {len(unique_orders)} UNIQUE orders...")
            
            for order in unique_orders:
                order_id = order.get("id")
                shipments = order.get("shipments", [])
                
                if not shipments:
                    result["skipped"] += 1
                    continue
                
                shipment_id = shipments[0].get("id")
                if not shipment_id:
                    result["skipped"] += 1
                    continue
                
                success, response = ship_order(token, shipment_id)
                
                if success:
                    result["shipped"] += 1
                    unique_shipped_ids.append(shipment_id)
                    result["details"].append(f"  Order #{order_id}: ✅ Shipped")
                else:
                    result["failed"] += 1
                    result["details"].append(f"  Order #{order_id}: ❌ Failed")
        
        # All shipped IDs (duplicates + unique)
        all_shipped_ids = duplicate_shipped_ids + unique_shipped_ids
        
        if not all_shipped_ids:
            result["errors"].append("Could not ship any orders")
            return result
        
        result["details"].append(f"✅ Total shipped: {len(all_shipped_ids)} orders")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Download ALL labels
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("📄 Downloading ALL labels...")
        try:
            all_labels = download_labels(token, all_shipped_ids)
            if all_labels:
                result["all_labels_pdf"] = all_labels
                result["labels_downloaded"] = True
                result["details"].append("  ✅ All labels downloaded")
        except Exception as e:
            result["details"].append(f"  ❌ Labels error: {str(e)[:50]}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Schedule pickup (one by one)
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("🚚 Scheduling pickup...")
        try:
            pickup_count = schedule_pickup(token, all_shipped_ids)
            result["pickup_scheduled"] = pickup_count
            result["details"].append(f"  ✅ Pickup scheduled: {pickup_count}/{len(all_shipped_ids)}")
        except Exception as e:
            result["details"].append(f"  ❌ Pickup error: {str(e)[:50]}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 6: Generate manifest
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("📋 Generating manifest...")
        try:
            manifest = generate_manifest(token, all_shipped_ids)
            if manifest:
                result["manifest_generated"] = True
                result["details"].append("  ✅ Manifest generated")
        except Exception as e:
            result["details"].append(f"  ❌ Manifest error: {str(e)[:50]}")
        
        result["details"].append("✅ Workflow complete!")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Workflow error: {str(e)}")
        import traceback
        result["errors"].append(traceback.format_exc())
        return result
