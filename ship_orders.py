"""
Shiprocket Order Shipping Automation
====================================
Full workflow: Ship → Labels → Pickup → Manifest

Used by Kluzo when triggered via Telegram ("Ship them buddy")
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time

# Configuration
BASE_URL = "https://apiv2.shiprocket.in/v1/external"
CREDENTIALS_FILE = "/Users/klaus/.openclaw/workspace/shiprocket-credentials.env"
DATA_DIR = Path("/Users/klaus/.openclaw/workspace/shiprocket-dashboard/data")
LABELS_DIR = DATA_DIR / "labels"
MANIFESTS_DIR = DATA_DIR / "manifests"
HISTORY_FILE = DATA_DIR / "shipping_history.json"


def load_credentials():
    """Load credentials from env file."""
    creds = {}
    with open(CREDENTIALS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                creds[key.strip()] = value.strip()
    return creds.get('SHIPROCKET_EMAIL'), creds.get('SHIPROCKET_PASSWORD')


def authenticate():
    """Authenticate and get token."""
    email, password = load_credentials()
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json={"email": email, "password": password})
    response.raise_for_status()
    return response.json()["token"]


def get_orders(token, status="new", days=7):
    """Fetch orders by status for last N days."""
    url = f"{BASE_URL}/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    params = {
        "filter": status,
        "per_page": 100,
        "from": from_date,
        "to": to_date
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])


def ship_order(token, shipment_id):
    """Assign AWB to shipment (auto courier)."""
    url = f"{BASE_URL}/courier/assign/awb"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"shipment_id": shipment_id})
    response.raise_for_status()
    return response.json()


def get_label_url(token, shipment_ids):
    """Get label PDF URL."""
    url = f"{BASE_URL}/courier/generate/label"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"shipment_id": shipment_ids})
    response.raise_for_status()
    return response.json().get("label_url", "")


def schedule_pickup(token, shipment_ids):
    """Schedule pickup for shipments."""
    url = f"{BASE_URL}/courier/generate/pickup"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    pickup_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = requests.post(url, headers=headers, json={
        "shipment_id": shipment_ids,
        "pickup_date": pickup_date
    })
    response.raise_for_status()
    return response.json()


def generate_manifest(token, shipment_ids):
    """Generate manifest for shipments."""
    url = f"{BASE_URL}/manifests/generate"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"shipment_id": shipment_ids})
    response.raise_for_status()
    return response.json()


def download_file(url, filepath):
    """Download file from URL."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
    return False


def sort_labels_by_courier(input_pdf_path, output_dir):
    """Sort labels PDF by courier. Returns dict of courier -> filepath."""
    try:
        from pypdf import PdfReader, PdfWriter
        import re
        from collections import defaultdict
        
        reader = PdfReader(input_pdf_path)
        courier_pages = defaultdict(list)
        
        courier_patterns = [
            (r'Ekart', 'Ekart'),
            (r'Delhivery', 'Delhivery'),
            (r'Xpressbees', 'Xpressbees'),
            (r'BlueDart', 'BlueDart'),
            (r'DTDC', 'DTDC'),
            (r'Shadowfax', 'Shadowfax'),
            (r'Ecom\s*Express', 'EcomExpress'),
        ]
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            courier = 'Unknown'
            
            for pattern, name in courier_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    courier = name
                    break
            
            courier_pages[courier].append(i)
        
        # Create sorted PDFs
        sorted_files = {}
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M')
        
        for courier, page_indices in courier_pages.items():
            if page_indices:
                writer = PdfWriter()
                for idx in page_indices:
                    writer.add_page(reader.pages[idx])
                
                filename = f"{date_str}_{courier}.pdf"
                filepath = output_dir / filename
                with open(filepath, 'wb') as f:
                    writer.write(f)
                
                sorted_files[courier] = {
                    'path': str(filepath),
                    'count': len(page_indices)
                }
        
        return sorted_files
    
    except Exception as e:
        print(f"Error sorting labels: {e}")
        return {}


def save_history(record):
    """Save shipping record to history."""
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    
    history.insert(0, record)  # Add to beginning
    history = history[:100]  # Keep last 100 records
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def run_full_workflow(days=7):
    """
    Run the complete shipping workflow:
    1. Ship all NEW orders
    2. Download labels
    3. Schedule pickup
    4. Download manifest
    5. Sort labels by courier
    
    Returns summary dict.
    """
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now()
    date_str = timestamp.strftime('%Y-%m-%d_%H%M%S')
    
    result = {
        "timestamp": timestamp.isoformat(),
        "date_display": timestamp.strftime('%b %d, %Y %I:%M %p'),
        "total_orders": 0,
        "shipped": 0,
        "unshipped": 0,
        "unshipped_orders": [],
        "labels_url": "",
        "labels_sorted": {},
        "manifest_url": "",
        "pickup_scheduled": False,
        "errors": []
    }
    
    try:
        print("🔐 Authenticating...")
        token = authenticate()
        
        # Step 1: Get NEW orders
        print("📋 Fetching NEW orders...")
        new_orders = get_orders(token, status="new", days=days)
        result["total_orders"] = len(new_orders)
        
        if not new_orders:
            result["errors"].append("No new orders found")
            return result
        
        print(f"   Found {len(new_orders)} orders")
        
        # Step 2: Ship all orders
        print("🚀 Shipping orders...")
        shipped_ids = []
        
        for order in new_orders:
            shipments = order.get("shipments", {})
            if isinstance(shipments, dict):
                shipment_id = shipments.get("id")
            elif isinstance(shipments, list) and shipments:
                shipment_id = shipments[0].get("id")
            else:
                shipment_id = None
            
            if shipment_id:
                try:
                    ship_result = ship_order(token, shipment_id)
                    if ship_result.get("awb_assign_status") == 1:
                        shipped_ids.append(shipment_id)
                        result["shipped"] += 1
                    else:
                        result["unshipped"] += 1
                        result["unshipped_orders"].append({
                            "order_id": order.get("channel_order_id"),
                            "reason": ship_result.get("response", {}).get("data", {}).get("message", "Unknown")
                        })
                except Exception as e:
                    result["unshipped"] += 1
                    result["unshipped_orders"].append({
                        "order_id": order.get("channel_order_id"),
                        "reason": str(e)
                    })
                
                time.sleep(0.3)  # Rate limiting
        
        print(f"   Shipped: {result['shipped']}, Unshipped: {result['unshipped']}")
        
        if not shipped_ids:
            result["errors"].append("No orders were shipped successfully")
            save_history(result)
            return result
        
        # Wait a moment for Shiprocket to process
        time.sleep(2)
        
        # Step 3: Get Ready To Ship orders and download labels
        print("📄 Downloading labels...")
        rts_orders = get_orders(token, status="ready_to_ship", days=days)
        
        rts_shipment_ids = []
        for order in rts_orders:
            shipments = order.get("shipments", {})
            if isinstance(shipments, dict):
                rts_shipment_ids.append(shipments.get("id"))
            elif isinstance(shipments, list) and shipments:
                rts_shipment_ids.append(shipments[0].get("id"))
        
        rts_shipment_ids = [sid for sid in rts_shipment_ids if sid]
        
        if rts_shipment_ids:
            label_url = get_label_url(token, rts_shipment_ids)
            result["labels_url"] = label_url
            
            if label_url:
                # Download and sort labels
                raw_labels_path = LABELS_DIR / f"{date_str}_raw.pdf"
                if download_file(label_url, raw_labels_path):
                    print("   Labels downloaded, sorting by courier...")
                    sorted_dir = LABELS_DIR / date_str
                    sorted_dir.mkdir(exist_ok=True)
                    result["labels_sorted"] = sort_labels_by_courier(raw_labels_path, sorted_dir)
                    print(f"   Sorted into {len(result['labels_sorted'])} courier files")
        
        # Step 4: Schedule pickup
        print("🚚 Scheduling pickup...")
        try:
            pickup_result = schedule_pickup(token, rts_shipment_ids)
            result["pickup_scheduled"] = True
            print("   Pickup scheduled for tomorrow")
        except Exception as e:
            result["errors"].append(f"Pickup scheduling failed: {str(e)}")
        
        # Step 5: Generate manifest
        print("📋 Generating manifest...")
        try:
            manifest_result = generate_manifest(token, rts_shipment_ids)
            manifest_url = manifest_result.get("manifest_url", "")
            result["manifest_url"] = manifest_url
            
            if manifest_url:
                manifest_path = MANIFESTS_DIR / f"{date_str}_manifest.pdf"
                download_file(manifest_url, manifest_path)
                result["manifest_path"] = str(manifest_path)
                print("   Manifest downloaded")
        except Exception as e:
            result["errors"].append(f"Manifest generation failed: {str(e)}")
        
        print("✅ Workflow complete!")
        
    except Exception as e:
        result["errors"].append(f"Workflow error: {str(e)}")
    
    # Save to history
    save_history(result)
    
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("SHIPROCKET SHIPPING AUTOMATION")
    print("=" * 50)
    
    result = run_full_workflow(days=7)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total Orders: {result['total_orders']}")
    print(f"Shipped: {result['shipped']}")
    print(f"Unshipped: {result['unshipped']}")
    
    if result['labels_sorted']:
        print("\nSorted Labels:")
        for courier, info in result['labels_sorted'].items():
            print(f"  {courier}: {info['count']} labels")
    
    if result['errors']:
        print("\nErrors:")
        for err in result['errors']:
            print(f"  ❌ {err}")
