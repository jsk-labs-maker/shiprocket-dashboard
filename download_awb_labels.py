"""
Download Shiprocket Labels by AWB
==================================
Helper script to download labels for specific AWB numbers.

Usage:
  python3 download_awb_labels.py AWB1 AWB2 AWB3
  
Or via Telegram:
  Send: "Download labels: AWB1, AWB2, AWB3"
"""

import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv(Path(__file__).parent.parent / "shiprocket-credentials.env")

EMAIL = os.getenv("SHIPROCKET_EMAIL")
PASSWORD = os.getenv("SHIPROCKET_PASSWORD")
BASE_URL = "https://apiv2.shiprocket.in/v1/external"


def authenticate():
    """Get auth token."""
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json={"email": EMAIL, "password": PASSWORD})
    response.raise_for_status()
    return response.json()["token"]


def get_shipment_id_by_awb(token, awb):
    """Find shipment ID for AWB number."""
    url = f"{BASE_URL}/courier/track/awb/{awb}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract shipment_id from tracking data
            tracking_data = data.get("tracking_data", {})
            return tracking_data.get("shipment_id")
        return None
    except:
        return None


def download_label_by_shipment_id(token, shipment_id):
    """Download label for shipment ID."""
    url = f"{BASE_URL}/courier/generate/label"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json={"shipment_id": [shipment_id]})
    response.raise_for_status()
    
    data = response.json()
    label_url = data.get("label_url")
    
    if label_url:
        label_response = requests.get(label_url)
        return label_response.content
    return None


def download_labels_by_awb(awb_list):
    """Download labels for list of AWB numbers."""
    print(f"🔐 Authenticating...")
    token = authenticate()
    
    print(f"📋 Processing {len(awb_list)} AWB numbers...")
    
    labels = []
    for awb in awb_list:
        print(f"   {awb}...", end=" ")
        
        # Get shipment ID
        shipment_id = get_shipment_id_by_awb(token, awb)
        
        if shipment_id:
            # Download label
            label_data = download_label_by_shipment_id(token, shipment_id)
            if label_data:
                labels.append((awb, label_data))
                print("✅")
            else:
                print("❌ Download failed")
        else:
            print("❌ Not found")
    
    if labels:
        # Save combined PDF or individual PDFs
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        output_dir = Path(__file__).parent / "data" / "awb_downloads"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for awb, label_data in labels:
            output_path = output_dir / f"{timestamp}_{awb}.pdf"
            with open(output_path, 'wb') as f:
                f.write(label_data)
            print(f"📄 Saved: {output_path}")
        
        return [output_dir / f"{timestamp}_{awb}.pdf" for awb, _ in labels]
    
    return []


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 download_awb_labels.py AWB1 AWB2 AWB3")
        sys.exit(1)
    
    awb_list = sys.argv[1:]
    
    result = download_labels_by_awb(awb_list)
    
    if result:
        print(f"\n✅ Downloaded {len(result)} labels")
    else:
        print(f"\n❌ No labels downloaded")
