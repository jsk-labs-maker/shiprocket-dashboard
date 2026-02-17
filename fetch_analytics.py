"""
🐍 Shiprocket Analytics Data Fetcher
Fetches and pre-processes data for fast Analytics loading
Run: python fetch_analytics.py --days 60
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import argparse
import json
import os

SHIPROCKET_API = "https://apiv2.shiprocket.in/v1/external"

STATUS_MAP = {
    1: "AWB Assigned", 2: "Label Generated", 3: "Pickup Scheduled", 4: "Pickup Queued",
    5: "Manifest Generated", 6: "Shipped", 7: "Delivered", 8: "Cancelled",
    9: "RTO Initiated", 10: "RTO Delivered", 11: "Pending", 12: "Lost",
    13: "Pickup Error", 14: "RTO Acknowledged", 15: "Pickup Rescheduled",
    16: "Cancellation Requested", 17: "Out For Delivery", 18: "In Transit",
    19: "Out For Pickup", 20: "Pickup Exception", 21: "Undelivered", 22: "Delayed",
    23: "Partial Delivered", 24: "Destroyed", 25: "Damaged", 26: "Fulfilled",
    27: "Reached At Destination Hub", 28: "Misrouted", 29: "RTO NDR", 30: "RTO OFD",
    31: "Disposed Off", 32: "Cancelled Before Dispatched", 33: "RTO In Transit",
    34: "QC Failed", 35: "Reached Warehouse", 36: "Custom Cleared", 37: "In Flight",
    38: "Handover to Courier", 39: "Shipment Booked", 40: "In Transit To Destination Hub",
    41: "Contact Customer Care", 42: "Shipment Held", 43: "Self Fulfilled",
    44: "Disposed Off", 45: "Cancelled By User", 46: "RTO Delivered To Origin"
}

def categorize_status(status):
    """Categorize status into 5 groups"""
    status = str(status).upper().strip()
    
    # Check RTO first
    if "RTO" in status or "RETURN" in status:
        return "rto"
    
    rto = ["RTO INITIATED", "RTO IN TRANSIT", "RTO DELIVERED", "RTO NDR", "RTO OFD", "RTO ACKNOWLEDGED"]
    for s in rto:
        if s in status:
            return "rto"
    
    # Delivered FIRST (most important)
    delivered = ["DELIVERED", "COMPLETE", "FULFILLED"]
    for s in delivered:
        if s in status:
            return "delivered"
    
    # Undelivered (failed attempts)
    undelivered = ["UNDELIVERED", "FAILED", "DELIVERY FAILED", "LOST", "DAMAGED", "DESTROYED"]
    for s in undelivered:
        if s in status:
            return "undelivered"
    
    # In-Transit (shipped and on the way)
    intransit = ["SHIPPED", "IN TRANSIT", "IN-TRANSIT", "PICKED UP", "OUT FOR DELIVERY",
                 "REACHED AT DESTINATION HUB", "REACHED DESTINATION HUB", 
                 "DELIVERY DELAYED", "MISROUTED", "HANDOVER", "IN FLIGHT"]
    for s in intransit:
        if s in status:
            return "intransit"
    
    # Unshipped (not yet handed to courier)
    unshipped = ["NEW", "INVOICED", "PENDING", "AWB ASSIGNED", "LABEL GENERATED", 
                 "PICKUP SCHEDULED", "PICKUP QUEUED", "MANIFEST GENERATED", 
                 "OUT FOR PICKUP", "SHIPMENT BOOKED"]
    for s in unshipped:
        if s in status:
            return "unshipped"
    
    # Cancelled (separate from unshipped)
    if "CANCEL" in status:
        return "unshipped"
    
    # Default: intransit for unknown shipped statuses
    return "intransit"

def fetch_data(email, password, from_date, to_date):
    """Fetch orders from Shiprocket API"""
    print(f"🔐 Logging in...")
    auth = requests.post(f"{SHIPROCKET_API}/auth/login", 
                        json={"email": email, "password": password}, timeout=30)
    if not auth.ok:
        print("❌ Login failed!")
        return None
    
    token = auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in!")
    
    print(f"📅 Fetching: {from_date} to {to_date}")
    
    all_orders = []
    page = 1
    
    while True:
        print(f"📥 Page {page}... ({len(all_orders)} orders)", end="\r")
        
        try:
            r = requests.get(f"{SHIPROCKET_API}/orders", headers=headers, params={
                "per_page": 200,
                "page": page,
                "from": from_date,
                "to": to_date
            }, timeout=120)
            
            if not r.ok:
                break
            
            orders = r.json().get("data", [])
            if not orders:
                break
            
            all_orders.extend(orders)
            page += 1
            
        except Exception as e:
            print(f"\n⚠️ Error on page {page}: {e}")
            break
    
    print(f"\n✅ Fetched {len(all_orders)} orders")
    return all_orders

def process_orders(orders):
    """Process orders into analytics-ready format"""
    print("🔄 Processing orders...")
    
    rows = []
    for order in orders:
        shipments = order.get("shipments", [])
        shipment = shipments[0] if shipments else {}
        
        # Get status
        status_raw = shipment.get("status", order.get("status", ""))
        if isinstance(status_raw, int):
            status = STATUS_MAP.get(status_raw, f"Unknown-{status_raw}")
        else:
            status = str(status_raw) if status_raw else "Unknown"
        
        category = categorize_status(status)
        
        # Process each product in order
        for product in order.get("products", [{}]):
            # SKU is stored as 'channel_sku' in Shiprocket API
            sku = product.get("channel_sku") or product.get("sku") or "Unknown"
            rows.append({
                "order_id": order.get("channel_order_id", order.get("id", "")),
                "date": order.get("created_at", "")[:10] if order.get("created_at") else "",
                "status": status,
                "category": category,
                "sku": sku,
                "product_name": product.get("name", ""),
                "awb": shipment.get("awb", ""),
                "courier": shipment.get("courier_name", "")
            })
    
    df = pd.DataFrame(rows)
    print(f"✅ Processed {len(df)} rows")
    return df

def calculate_stats(df):
    """Calculate summary statistics"""
    stats = {
        "total": len(df),
        "unshipped": len(df[df["category"] == "unshipped"]),
        "intransit": len(df[df["category"] == "intransit"]),
        "delivered": len(df[df["category"] == "delivered"]),
        "rto": len(df[df["category"] == "rto"]),
        "undelivered": len(df[df["category"] == "undelivered"]),
        "skus": df["sku"].nunique(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Calculate delivery rate
    shipped = stats["intransit"] + stats["delivered"] + stats["rto"] + stats["undelivered"]
    stats["delivery_rate"] = round(stats["delivered"] / shipped * 100, 1) if shipped > 0 else 0
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Fetch Shiprocket Analytics Data")
    parser.add_argument("--days", type=int, default=30, help="Number of days to fetch")
    parser.add_argument("--from-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to-date", type=str, help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    
    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    email = os.getenv("SHIPROCKET_EMAIL", "openclawd12@gmail.com")
    password = os.getenv("SHIPROCKET_PASSWORD", "Kluzo@1212")
    
    # Set date range
    if args.from_date and args.to_date:
        from_date = args.from_date
        to_date = args.to_date
    else:
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    # Fetch and process
    orders = fetch_data(email, password, from_date, to_date)
    if not orders:
        print("❌ No orders fetched")
        return
    
    df = process_orders(orders)
    stats = calculate_stats(df)
    
    # Save to files
    os.makedirs("data", exist_ok=True)
    
    # Save CSV
    csv_file = "data/analytics_data.csv"
    df.to_csv(csv_file, index=False)
    print(f"💾 Saved: {csv_file}")
    
    # Save stats
    stats_file = "data/analytics_stats.json"
    stats["from_date"] = from_date
    stats["to_date"] = to_date
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"💾 Saved: {stats_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    print(f"Date Range: {from_date} to {to_date}")
    print(f"Total Orders: {stats['total']}")
    print(f"Unique SKUs: {stats['skus']}")
    print(f"\n📦 Unshipped:   {stats['unshipped']} ({stats['unshipped']/stats['total']*100:.1f}%)")
    print(f"🚚 In-Transit:  {stats['intransit']} ({stats['intransit']/stats['total']*100:.1f}%)")
    print(f"✅ Delivered:   {stats['delivered']} ({stats['delivered']/stats['total']*100:.1f}%)")
    print(f"↩️ RTO:         {stats['rto']} ({stats['rto']/stats['total']*100:.1f}%)")
    print(f"❌ Undelivered: {stats['undelivered']} ({stats['undelivered']/stats['total']*100:.1f}%)")
    print(f"\n🎯 Delivery Rate: {stats['delivery_rate']}%")
    print("="*50)

if __name__ == "__main__":
    main()
