"""
Shiprocket Order Shipping Automation
====================================
Full workflow: Ship → Labels → Pickup → Manifest

Used by Kluzo when triggered via Telegram ("Ship them buddy")
"""

import os
import json
import requests
import re
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
    """Schedule pickup for shipments (one by one for reliability)."""
    url = f"{BASE_URL}/courier/generate/pickup"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    success_count = 0
    for sid in shipment_ids:
        try:
            response = requests.post(url, headers=headers, json={"shipment_id": [sid]})
            if response.status_code == 200:
                success_count += 1
            time.sleep(0.2)  # Small delay to avoid rate limiting
        except:
            pass
    
    return {"scheduled": success_count, "total": len(shipment_ids)}


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


def normalize_sku(sku_raw: str) -> str:
    """Normalize SKU for filename safety."""
    return re.sub(r'[^\w\-]', '', sku_raw.replace(' ', '-'))[:50]


def extract_label_info(page_text: str) -> dict:
    """Extract courier, SKU, and date from label text."""
    info = {
        'courier': 'Unknown',
        'sku': 'Unknown',
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Courier patterns
    courier_patterns = [
        (r'Ekart[^\n]*', 'Ekart'),
        (r'Delhivery[^\n]*', 'Delhivery'),
        (r'Xpressbees[^\n]*', 'Xpressbees'),
        (r'BlueDart[^\n]*', 'BlueDart'),
        (r'DTDC[^\n]*', 'DTDC'),
        (r'Shadowfax[^\n]*', 'Shadowfax'),
        (r'Ecom\s*Express[^\n]*', 'EcomExpress'),
    ]
    
    for pattern, name in courier_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            info['courier'] = name
            break
    
    # SKU extraction - look for "SKU: XXXXX"
    sku_match = re.search(r'SKU:\s*([^\n]+)', page_text)
    if sku_match:
        info['sku'] = normalize_sku(sku_match.group(1).strip())
    
    # Date extraction
    date_match = re.search(r'Invoice Date:\s*(\d{4}-\d{2}-\d{2})', page_text)
    if date_match:
        info['date'] = date_match.group(1)
    else:
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', page_text)
        if date_match:
            info['date'] = date_match.group(1)
    
    return info


def sort_labels_by_sku_courier(input_pdf_path, output_dir):
    """Sort labels PDF by Date + Courier + SKU. Returns nested dict."""
    try:
        from pypdf import PdfReader, PdfWriter
        from collections import defaultdict
        
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        
        # Group pages by (date, courier, sku)
        groups = defaultdict(list)
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            info = extract_label_info(text)
            key = (info['date'], info['courier'], info['sku'])
            groups[key].append(i)
        
        # Create sorted PDFs - return in {sku: {courier: {path, count}}} format
        sorted_files = {}
        
        for (date, courier, sku), page_indices in sorted(groups.items()):
            if page_indices:
                # Output filename: YYYY-MM-DD_Courier_SKU.pdf
                filename = f"{date}_{courier}_{sku}.pdf"
                filepath = output_dir / filename
                
                writer = PdfWriter()
                for idx in page_indices:
                    writer.add_page(reader.pages[idx])
                
                with open(filepath, 'wb') as f:
                    writer.write(f)
                
                # Organize by SKU -> Courier
                if sku not in sorted_files:
                    sorted_files[sku] = {}
                
                sorted_files[sku][courier] = {
                    'path': filename,  # Just filename, not full path
                    'count': len(page_indices)
                }
        
        return sorted_files
    
    except Exception as e:
        print(f"Error sorting labels: {e}")
        return {}


def sort_labels_by_courier(input_pdf_path, output_dir):
    """Sort labels PDF by courier only (legacy). Returns dict of courier -> filepath."""
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


def add_activity_log(result):
    """Add entry to activity log."""
    try:
        import uuid
        
        PUBLIC_DIR = Path(__file__).parent / "public" / "logs"
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        log_file = PUBLIC_DIR / "activity.json"
        
        logs = {"logs": [], "updated_at": None}
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        shipped = result.get("shipped", 0)
        failed = result.get("unshipped", 0)
        log_type = "success" if failed == 0 else ("warning" if shipped > 0 else "error")
        
        log_entry = {
            "id": f"log-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "Shipping Workflow",
            "message": f"Shipped: {shipped}, Failed: {failed}, Total: {result.get('total_orders', 0)}",
            "type": log_type
        }
        
        logs["logs"].insert(0, log_entry)
        logs["logs"] = logs["logs"][:500]  # Keep last 500 logs
        logs["updated_at"] = datetime.now().isoformat()
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except:
        pass  # Don't fail workflow if logging fails


def update_status(status, message="", progress=0, push_to_github=False):
    """Update processing status for dashboard.
    
    Args:
        status: Status type (idle, processing, complete, error)
        message: Status message
        progress: Progress percentage 0-100
        push_to_github: If True, commit and push to GitHub (slower but real-time)
    """
    try:
        PUBLIC_DIR = Path(__file__).parent / "public"
        PUBLIC_DIR.mkdir(exist_ok=True)
        status_file = PUBLIC_DIR / "status.json"
        ai_status_file = PUBLIC_DIR / "ai" / "status.json"
        
        # Create ai directory if needed
        (PUBLIC_DIR / "ai").mkdir(exist_ok=True)
        
        status_data = {
            "status": status,  # idle, processing, complete, error
            "message": message,
            "current_task": message if status == "processing" else None,
            "timestamp": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": progress
        }
        
        # Write to both status files (backward compatibility)
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        with open(ai_status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        # Only push to GitHub for major status changes (start, complete, error)
        if push_to_github or status in ["complete", "error"]:
            import subprocess
            subprocess.run(["git", "-C", str(PUBLIC_DIR.parent), "add", str(status_file), str(ai_status_file)], 
                          capture_output=True, timeout=5)
            subprocess.run(["git", "-C", str(PUBLIC_DIR.parent), "commit", "-m", f"Status: {status}"], 
                          capture_output=True, timeout=5)
            subprocess.run(["git", "-C", str(PUBLIC_DIR.parent), "push", "origin", "main"], 
                          capture_output=True, timeout=10)
    except:
        pass  # Don't fail workflow if status update fails


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
    # Update status: Starting (push to show we're active)
    update_status("processing", "Starting workflow...", 10, push_to_github=True)
    
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
        update_status("processing", "Authenticating with Shiprocket...", 20)
        token = authenticate()
        
        # Step 1: Get NEW orders
        print("📋 Fetching NEW orders...")
        update_status("processing", "Fetching NEW orders...", 30)
        new_orders = get_orders(token, status="new", days=days)
        result["total_orders"] = len(new_orders)
        
        if not new_orders:
            result["errors"].append("No new orders found")
            return result
        
        print(f"   Found {len(new_orders)} orders")
        
        # Step 2: Ship all orders
        print("🚀 Shipping orders...")
        update_status("processing", f"Shipping {len(new_orders)} orders...", 40)
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
        
        # Step 3: Download labels ONLY for the shipments we just shipped
        print("📄 Downloading labels...")
        update_status("processing", f"Downloading labels for {len(shipped_ids)} orders...", 60)
        # Use only the shipment IDs we successfully shipped
        rts_shipment_ids = shipped_ids
        
        if rts_shipment_ids:
            label_url = get_label_url(token, rts_shipment_ids)
            result["labels_url"] = label_url
            
            if label_url:
                # Download and sort labels
                raw_labels_path = LABELS_DIR / f"{date_str}_raw.pdf"
                if download_file(label_url, raw_labels_path):
                    print("   Labels downloaded, sorting by SKU + Courier...")
                    sorted_dir = LABELS_DIR / date_str
                    sorted_dir.mkdir(exist_ok=True)
                    result["labels_sorted"] = sort_labels_by_sku_courier(raw_labels_path, sorted_dir)
                    # Count total files
                    total_files = sum(len(couriers) for couriers in result["labels_sorted"].values())
                    print(f"   Sorted into {total_files} files ({len(result['labels_sorted'])} SKUs)")
        
        # Step 4: Schedule pickup (only for orders we just shipped)
        print("🚚 Scheduling pickup...")
        try:
            pickup_result = schedule_pickup(token, shipped_ids)
            scheduled = pickup_result.get("scheduled", 0)
            total = pickup_result.get("total", 0)
            result["pickup_scheduled"] = scheduled > 0
            result["pickup_count"] = scheduled
            print(f"   Pickup scheduled for {scheduled}/{total} shipments")
        except Exception as e:
            result["errors"].append(f"Pickup scheduling failed: {str(e)}")
        
        # Step 5: Generate manifest (only for orders we just shipped)
        print("📋 Generating manifest...")
        try:
            manifest_result = generate_manifest(token, shipped_ids)
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
        update_status("processing", "Uploading to GitHub...", 90)
        
    except Exception as e:
        result["errors"].append(f"Workflow error: {str(e)}")
        update_status("error", f"Error: {str(e)}", 0)
    
    # Save to history
    save_history(result)
    
    # Add activity log entry
    add_activity_log(result)
    
    # Final status (push to GitHub)
    update_status("complete", f"✅ Done! {result.get('shipped', 0)} orders shipped", 100, push_to_github=True)
    
    # Create ZIP and push to GitHub
    try:
        print("\n📤 Uploading to GitHub...")
        upload_to_github(result)
        print("   ✅ Uploaded to GitHub")
    except Exception as e:
        print(f"   ⚠️ GitHub upload failed: {e}")
        result["errors"].append(f"GitHub upload failed: {str(e)}")
    
    return result


def upload_to_github(result):
    """Create ZIP of sorted labels, save to history, and push to GitHub."""
    import zipfile
    import subprocess
    
    timestamp = datetime.now()
    date_str = timestamp.strftime('%Y-%m-%d_%H%M%S')
    date_only = timestamp.strftime('%Y-%m-%d')
    time_only = timestamp.strftime('%I:%M %p')
    
    PUBLIC_DIR = Path(__file__).parent / "public"
    PUBLIC_DIR.mkdir(exist_ok=True)
    
    # Create ZIP with all sorted labels (in public folder for download)
    zip_filename = f"batch_{date_str}.zip"
    zip_path = PUBLIC_DIR / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Add all sorted label files
        labels_sorted = result.get("labels_sorted", {})
        for sku, couriers in labels_sorted.items():
            for courier, info in couriers.items():
                filepath = info.get("path")
                # filepath is just filename now, need to find actual file
                if filepath:
                    # Search in labels directories
                    for labels_dir in LABELS_DIR.glob("2026-*/"):
                        full_path = labels_dir / filepath
                        if full_path.exists():
                            zf.write(full_path, arcname=filepath)
                            break
        
        # Add manifest if available
        manifest_path = result.get("manifest_path")
        if manifest_path and os.path.exists(manifest_path):
            manifest_filename = os.path.basename(manifest_path)
            zf.write(manifest_path, arcname=manifest_filename)
    
    # Create batch record
    labels_sorted = result.get("labels_sorted", {})
    sku_list = list(labels_sorted.keys()) if labels_sorted else []
    
    batch_record = {
        "timestamp": timestamp.isoformat(),
        "date": date_only,
        "time": time_only,
        "display_time": time_only,
        "total_orders": result.get("total_orders", 0),
        "shipped": result.get("shipped", 0),
        "unshipped": result.get("unshipped", 0),
        "skus": sku_list,
        "sku_count": len(sku_list),
        "labels_sorted": labels_sorted,
        "zip_file": f"public/{zip_filename}",
        "zip_filename": zip_filename,
        "manifest_filename": os.path.basename(manifest_path) if manifest_path and os.path.exists(manifest_path) else None
    }
    
    # Update latest_labels.json (for backwards compatibility)
    latest_metadata = {
        "timestamp": timestamp.isoformat(),
        "date_display": timestamp.strftime('%d %b %Y, %I:%M %p'),
        "total_orders": result.get("total_orders", 0),
        "shipped": result.get("shipped", 0),
        "unshipped": result.get("unshipped", 0),
        "labels_sorted": result.get("labels_sorted", {}),
        "zip_filename": zip_filename
    }
    
    latest_path = PUBLIC_DIR / "latest_labels.json"
    with open(latest_path, 'w') as f:
        json.dump(latest_metadata, f, indent=2)
    
    # Append to batches history
    history_path = PUBLIC_DIR / "batches_history.json"
    history = {"batches": []}
    if history_path.exists():
        with open(history_path, 'r') as f:
            history = json.load(f)
    
    history["batches"].insert(0, batch_record)  # Add to beginning
    history["batches"] = history["batches"][:100]  # Keep last 100 batches
    
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    
    # Git commit and push
    repo_path = Path(__file__).parent
    subprocess.run(["git", "add", str(PUBLIC_DIR)], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", f"📦 Batch {date_str} - {result.get('shipped', 0)} orders"], cwd=repo_path, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, check=True)


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
        print("\nSorted Labels (SKU + Courier):")
        for sku, couriers in result['labels_sorted'].items():
            print(f"  📦 {sku}:")
            for courier, info in couriers.items():
                print(f"      {courier}: {info['count']} labels")
    
    if result['errors']:
        print("\nErrors:")
        for err in result['errors']:
            print(f"  ❌ {err}")
