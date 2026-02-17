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
    
    Logic:
    - 3 orders same phone → Keep 1, Cancel 2
    - 2 orders same phone → Keep 1, Cancel 1
    - 1 order = unique (ship normally)
    
    Returns (orders_to_cancel, orders_to_ship, duplicate_info)
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
    
    orders_to_cancel = []
    orders_to_ship = []
    duplicate_info = []
    
    for phone, group in phone_groups.items():
        if len(group) > 1:
            # Multiple orders from same phone
            # Sort by order ID (keep oldest/first order)
            group_sorted = sorted(group, key=lambda x: x.get("id", 0))
            
            # Keep first order, cancel the rest
            orders_to_ship.append(group_sorted[0])
            orders_to_cancel.extend(group_sorted[1:])
            
            customer_name = group[0].get("customer_name", "Unknown")
            duplicate_info.append({
                "phone": phone,
                "customer": customer_name,
                "total_orders": len(group),
                "keep_order_id": group_sorted[0].get("id"),
                "cancel_order_ids": [o.get("id") for o in group_sorted[1:]]
            })
        else:
            # Single order = ship normally
            orders_to_ship.extend(group)
    
    return orders_to_cancel, orders_to_ship, duplicate_info


def cancel_order(token, order_id):
    """Cancel a single order."""
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"
    url = f"{BASE_URL}/orders/cancel"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json={"ids": [order_id]})
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text


def export_cancelled_orders_to_excel(cancelled_orders):
    """
    Export cancelled orders to Excel file.
    Returns file path.
    """
    import pandas as pd
    
    # Extract relevant fields
    data = []
    for order in cancelled_orders:
        data.append({
            "Order ID": order.get("id"),
            "Channel Order ID": order.get("channel_order_id"),
            "Customer Name": order.get("customer_name"),
            "Phone": order.get("customer_phone") or order.get("billing_phone"),
            "Email": order.get("customer_email"),
            "City": order.get("customer_city"),
            "State": order.get("customer_state"),
            "Pincode": order.get("customer_pincode"),
            "Total": order.get("total"),
            "Payment Method": order.get("payment_method"),
            "Order Date": order.get("created_at"),
            "Cancel Reason": "Duplicate Order (Same Phone Number)"
        })
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filepath = f"/tmp/cancelled_duplicates_{timestamp}.xlsx"
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    return filepath


def run_shipping_workflow():
    """
    Run complete shipping workflow with duplicate detection & cancellation.
    
    Flow:
    1. Fetch NEW orders
    2. Find duplicates (same phone number)
    3. CANCEL extra duplicate orders (keep 1 per phone)
    4. Export cancelled orders to Excel → Return for Telegram
    5. Ship remaining unique orders (1 per phone)
    6. Download labels, schedule pickup, generate manifest
    
    Returns dict with results including cancelled_excel_path for Telegram.
    """
    result = {
        "total_orders": 0,
        "cancelled_count": 0,
        "to_ship_count": 0,
        "shipped": 0,
        "failed": 0,
        "skipped": 0,
        "pickup_scheduled": 0,
        "labels_downloaded": False,
        "manifest_generated": False,
        "cancelled_excel_path": None,  # Excel file path for Telegram
        "cancelled_orders": [],  # List of cancelled order objects
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
        orders_to_cancel, orders_to_ship, duplicate_info = find_duplicate_orders(orders)
        
        result["cancelled_count"] = len(orders_to_cancel)
        result["to_ship_count"] = len(orders_to_ship)
        result["duplicate_info"] = duplicate_info
        
        if orders_to_cancel:
            result["details"].append(f"⚠️ Found {len(orders_to_cancel)} orders to CANCEL (duplicates)")
            for info in duplicate_info:
                result["details"].append(f"  📱 {info['phone']} ({info['customer']}): {info['total_orders']} orders → Keep #{info['keep_order_id']}, Cancel {info['cancel_order_ids']}")
        else:
            result["details"].append("✅ No duplicates found")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: CANCEL duplicate orders
        # ═══════════════════════════════════════════════════════════════
        cancelled_orders = []
        
        if orders_to_cancel:
            result["details"].append(f"🚫 Cancelling {len(orders_to_cancel)} duplicate orders...")
            
            for order in orders_to_cancel:
                order_id = order.get("id")
                
                success, response = cancel_order(token, order_id)
                
                if success:
                    cancelled_orders.append(order)
                    result["details"].append(f"  Order #{order_id}: ❌ Cancelled (duplicate)")
                else:
                    result["details"].append(f"  Order #{order_id}: ⚠️ Cancel failed - {str(response)[:50]}")
                
                time.sleep(0.2)  # Avoid rate limiting
            
            result["cancelled_orders"] = cancelled_orders
            result["details"].append(f"✅ Cancelled {len(cancelled_orders)} duplicate orders")
            
            # Export cancelled orders to Excel
            if cancelled_orders:
                result["details"].append("📊 Exporting cancelled orders to Excel...")
                try:
                    excel_path = export_cancelled_orders_to_excel(cancelled_orders)
                    result["cancelled_excel_path"] = excel_path
                    result["details"].append(f"  ✅ Excel ready: {excel_path}")
                except Exception as e:
                    result["details"].append(f"  ❌ Excel export error: {str(e)[:50]}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Ship remaining UNIQUE orders (1 per phone)
        # ═══════════════════════════════════════════════════════════════
        shipped_ids = []
        
        if orders_to_ship:
            result["details"].append(f"🚀 Shipping {len(orders_to_ship)} unique orders...")
            
            for order in orders_to_ship:
                order_id = order.get("id")
                shipments = order.get("shipments", [])
                
                if not shipments:
                    result["skipped"] += 1
                    result["details"].append(f"  Order #{order_id}: ⏭️ Skipped (no shipment)")
                    continue
                
                shipment_id = shipments[0].get("id")
                if not shipment_id:
                    result["skipped"] += 1
                    result["details"].append(f"  Order #{order_id}: ⏭️ Skipped (no shipment ID)")
                    continue
                
                success, response = ship_order(token, shipment_id)
                
                if success:
                    result["shipped"] += 1
                    shipped_ids.append(shipment_id)
                    result["details"].append(f"  Order #{order_id}: ✅ Shipped")
                else:
                    result["failed"] += 1
                    error_msg = str(response)[:50]
                    result["details"].append(f"  Order #{order_id}: ❌ Failed - {error_msg}")
        
        if not shipped_ids:
            result["errors"].append("Could not ship any orders")
            return result
        
        result["details"].append(f"✅ Shipped {len(shipped_ids)} orders")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Download labels
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("📄 Downloading labels...")
        try:
            labels_pdf = download_labels(token, shipped_ids)
            if labels_pdf:
                result["all_labels_pdf"] = labels_pdf
                result["labels_downloaded"] = True
                result["details"].append("  ✅ Labels downloaded")
        except Exception as e:
            result["details"].append(f"  ❌ Labels error: {str(e)[:50]}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Schedule pickup (one by one)
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("🚚 Scheduling pickup...")
        try:
            pickup_count = schedule_pickup(token, shipped_ids)
            result["pickup_scheduled"] = pickup_count
            result["details"].append(f"  ✅ Pickup scheduled: {pickup_count}/{len(shipped_ids)}")
        except Exception as e:
            result["details"].append(f"  ❌ Pickup error: {str(e)[:50]}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 6: Generate manifest
        # ═══════════════════════════════════════════════════════════════
        result["details"].append("📋 Generating manifest...")
        try:
            manifest = generate_manifest(token, shipped_ids)
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
