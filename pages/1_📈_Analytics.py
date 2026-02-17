"""
📈 Analytics Page - SKU Delivery Performance
Auto-fetch from Shiprocket or upload export file
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

load_dotenv()

st.set_page_config(
    page_title="Analytics | Kluzo",
    page_icon="📈",
    layout="wide"
)

# DISABLE auto-refresh on this page (fetching takes time)
st.markdown("""
<style>
/* Override any auto-refresh */
</style>
<script>
// Stop any auto-refresh timers
if (window.autoRefreshInterval) {
    clearInterval(window.autoRefreshInterval);
}
</script>
""", unsafe_allow_html=True)

# === CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp { 
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%) !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }

[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0a0e14 0%, #111820 100%) !important;
}

.stat-card {
    background: rgba(22, 27, 34, 0.9);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s ease;
}
.stat-card:hover {
    border-color: #58a6ff;
    transform: translateY(-2px);
}
.stat-value {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.stat-label {
    color: #8b949e;
    font-size: 0.85rem;
    margin-bottom: 8px;
}
.stat-percent {
    font-size: 1rem;
    font-weight: 600;
}

.unshipped { border-left: 4px solid #8b949e; }
.unshipped .stat-value { color: #8b949e; }
.unshipped .stat-percent { color: #8b949e; }

.intransit { border-left: 4px solid #58a6ff; }
.intransit .stat-value { color: #58a6ff; }
.intransit .stat-percent { color: #58a6ff; }

.delivered { border-left: 4px solid #3fb950; }
.delivered .stat-value { color: #3fb950; }
.delivered .stat-percent { color: #3fb950; }

.rto { border-left: 4px solid #f85149; }
.rto .stat-value { color: #f85149; }
.rto .stat-percent { color: #f85149; }

.undelivered { border-left: 4px solid #f0883e; }
.undelivered .stat-value { color: #f0883e; }
.undelivered .stat-percent { color: #f0883e; }

.total-card {
    background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(139, 92, 246, 0.1));
    border: 1px solid #58a6ff;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# === SHIPROCKET CONFIG ===
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
    44: "Disposed Off", 45: "Cancelled By User", 46: "RTO Delivered To Origin", 47: "AWB Not Assigned"
}

def get_shiprocket_credentials():
    email = os.getenv("SHIPROCKET_EMAIL", "openclawd12@gmail.com")
    password = os.getenv("SHIPROCKET_PASSWORD", "Kluzo@1212")
    return email, password

def fetch_shiprocket_data(days=30, progress_callback=None):
    """Fetch orders from Shiprocket API with progress"""
    email, password = get_shiprocket_credentials()
    
    # Login
    if progress_callback:
        progress_callback(0, "🔐 Logging in to Shiprocket...")
    
    try:
        auth = requests.post(f"{SHIPROCKET_API}/auth/login", json={"email": email, "password": password}, timeout=30)
        if not auth.ok:
            return None, "Login failed"
    except Exception as e:
        return None, f"Login error: {e}"
    
    token = auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    if progress_callback:
        progress_callback(5, f"📅 Fetching orders from {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}...")
    
    # Fetch orders with progress
    all_orders = []
    max_pages = 200  # Handle up to 40,000 orders (200 per page)
    
    for page in range(1, max_pages + 1):
        try:
            if progress_callback:
                progress_callback(5 + min(page, 80), f"📥 Page {page}... ({len(all_orders)} orders so far)")
            
            r = requests.get(f"{SHIPROCKET_API}/orders", headers=headers, params={
                "per_page": 200, "page": page,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d")
            }, timeout=120)  # Longer timeout for large datasets
            
            if r.ok:
                orders = r.json().get("data", [])
                if not orders:
                    break
                all_orders.extend(orders)
            else:
                break
        except requests.exceptions.Timeout:
            if progress_callback:
                progress_callback(85, f"⏳ Timeout on page {page}, continuing with {len(all_orders)} orders...")
            break
        except Exception as e:
            break
    
    if progress_callback:
        progress_callback(90, f"🔄 Processing {len(all_orders)} orders...")
    
    # Process orders
    rows = []
    for order in all_orders:
        shipments = order.get("shipments", [])
        shipment = shipments[0] if shipments else {}
        
        status_raw = shipment.get("status", order.get("status", ""))
        if isinstance(status_raw, int):
            status = STATUS_MAP.get(status_raw, f"Status {status_raw}")
        else:
            status = str(status_raw) if status_raw else "Unknown"
        
        for product in order.get("products", [{}]):
            rows.append({
                "Order ID": order.get("channel_order_id", order.get("id", "")),
                "Created At": order.get("created_at", "")[:10] if order.get("created_at") else "",
                "Status": status,
                "SKU": product.get("sku", ""),
                "Product Name": product.get("name", ""),
                "AWB": shipment.get("awb", ""),
                "Courier": shipment.get("courier_name", ""),
            })
    
    if progress_callback:
        progress_callback(100, f"✅ Done! Loaded {len(rows)} order rows")
    
    return pd.DataFrame(rows), None

def categorize_status(status):
    """Group statuses into 5 categories"""
    status = str(status).upper().strip() if status else ""
    
    unshipped = ["NEW", "INVOICED", "CANCELLED", "CANCELED", "CANCELLATION REQUESTED", "PENDING PAYMENT", "PROCESSING", "CANCELLED BY USER", "CANCELLED BEFORE DISPATCHED"]
    intransit = ["PICKUP SCHEDULED", "PICKED UP", "IN TRANSIT", "OUT FOR DELIVERY", "SHIPPED", "PICKUP GENERATED", "PICKUP QUEUED", "REACHED DESTINATION HUB", "REACHED AT DESTINATION HUB", "MISROUTED", "PENDING", "DISPATCHED", "MANIFESTED", "AWB ASSIGNED", "LABEL GENERATED", "MANIFEST GENERATED", "OUT FOR PICKUP", "HANDOVER TO COURIER", "SHIPMENT BOOKED", "IN TRANSIT TO DESTINATION HUB", "IN FLIGHT", "CUSTOM CLEARED", "DELAYED", "SHIPMENT HELD"]
    delivered = ["DELIVERED", "COMPLETE", "COMPLETED", "PARTIAL DELIVERED", "SELF FULFILLED", "FULFILLED"]
    rto = ["RTO INITIATED", "RTO IN TRANSIT", "RTO DELIVERED", "RTO", "RETURNED", "RTO NDR", "RTO OFD", "RTO ACKNOWLEDGED", "RTO DELIVERED TO ORIGIN"]
    undelivered = ["UNDELIVERED", "FAILED", "DELIVERY FAILED", "LOST", "DAMAGED", "DESTROYED", "DISPOSED OFF", "QC FAILED", "PICKUP ERROR", "PICKUP EXCEPTION", "CONTACT CUSTOMER CARE"]
    
    for s in unshipped:
        if s in status:
            return "unshipped"
    for s in delivered:
        if s in status:
            return "delivered"
    for s in rto:
        if s in status:
            return "rto"
    for s in undelivered:
        if s in status:
            return "undelivered"
    for s in intransit:
        if s in status:
            return "intransit"
    
    if "CANCEL" in status:
        return "unshipped"
    if "RTO" in status or "RETURN" in status:
        return "rto"
    if "DELIVER" in status:
        return "delivered"
    if "TRANSIT" in status or "PICKUP" in status or "SHIP" in status:
        return "intransit"
    
    return "unshipped"

# === HEADER ===
st.markdown("# 📈 SKU Delivery Analytics")
st.caption("Analyze delivery performance by SKU")
st.markdown("---")

# === DATA SOURCE SELECTION ===
st.markdown("### 📊 Load Data")

# Check if already have cached data
if "analytics_df" in st.session_state and st.session_state["analytics_df"] is not None:
    cached_info = st.session_state.get("data_source", "")
    st.info(f"📁 **Cached data loaded:** {cached_info} ({len(st.session_state['analytics_df'])} rows)")
    if st.button("🗑️ Clear & Reload", type="secondary"):
        del st.session_state["analytics_df"]
        st.rerun()

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    days_option = st.selectbox("📅 Select Period", [30, 60, 90, 180, 365], index=0, format_func=lambda x: f"Last {x} Days")
    fetch_clicked = st.button("🔄 Fetch from Shiprocket", type="primary", use_container_width=True)

with col_btn2:
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📤 Or Upload Export", type=["xlsx", "xls", "csv"], label_visibility="collapsed")

# === LOAD DATA ===
df = None
data_source = None

if fetch_clicked:
    # Create progress display
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(pct, msg):
        progress_bar.progress(min(pct, 100))
        status_text.text(msg)
    
    update_progress(0, "🚀 Starting fetch...")
    
    df, error = fetch_shiprocket_data(days=days_option, progress_callback=update_progress)
    
    if error:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ {error}")
    elif df is not None and len(df) > 0:
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        st.session_state["analytics_df"] = df
        st.session_state["data_source"] = f"Shiprocket API (Last {days_option} days) - {len(df)} rows"
        st.success(f"✅ Loaded {len(df)} orders from Shiprocket!")
        st.rerun()  # Refresh to show data
    else:
        progress_bar.empty()
        status_text.empty()
        st.warning("📭 No orders found for selected period")

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state["analytics_df"] = df
        st.session_state["data_source"] = f"Uploaded: {uploaded_file.name}"
        st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# Use session state data
if "analytics_df" in st.session_state:
    df = st.session_state["analytics_df"]
    data_source = st.session_state.get("data_source", "")

if df is None or len(df) == 0:
    st.info("👆 Click **Fetch from Shiprocket** or upload an export file to get started")
    st.stop()

st.markdown(f"📁 **Data Source:** {data_source}")
st.markdown("---")

# === PROCESS DATA ===
# Find columns
def find_col(possible):
    for p in possible:
        for c in df.columns:
            if p.lower() in c.lower():
                return c
    return None

sku_col = find_col(["sku", "product sku", "item sku"])
status_col = find_col(["status", "order status", "shipment status"])
date_col = find_col(["created", "date", "order date"])
order_col = find_col(["order id", "channel order"])
awb_col = find_col(["awb", "tracking"])
courier_col = find_col(["courier", "shipping provider"])

if not status_col:
    st.error("❌ Could not find Status column")
    st.write("Available columns:", list(df.columns))
    st.stop()

# Process rows
processed = []
all_skus = set()

for _, row in df.iterrows():
    sku = str(row[sku_col]).strip() if sku_col and pd.notna(row.get(sku_col)) else "Unknown"
    status = str(row[status_col]).strip() if pd.notna(row.get(status_col)) else ""
    date_val = str(row[date_col])[:10] if date_col and pd.notna(row.get(date_col)) else ""
    order_id = str(row[order_col]) if order_col and pd.notna(row.get(order_col)) else ""
    awb = str(row[awb_col]) if awb_col and pd.notna(row.get(awb_col)) else ""
    courier = str(row[courier_col]) if courier_col and pd.notna(row.get(courier_col)) else ""
    
    category = categorize_status(status)
    
    if sku and sku != "Unknown" and sku != "nan":
        all_skus.add(sku)
    
    processed.append({
        "order_id": order_id, "sku": sku, "status": status,
        "category": category, "date": date_val, "awb": awb, "courier": courier
    })

# === FILTERS ===
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    sku_options = ["ALL"] + sorted(list(all_skus))
    selected_sku = st.selectbox("🔍 Select SKU", sku_options, index=0)

# Date range
dates = [p["date"] for p in processed if p["date"] and len(p["date"]) >= 10]
if dates:
    try:
        date_objs = [datetime.strptime(d[:10], "%Y-%m-%d") for d in dates]
        min_date, max_date = min(date_objs).date(), max(date_objs).date()
    except:
        min_date = max_date = datetime.now().date()
else:
    min_date = max_date = datetime.now().date()

with col2:
    from_date = st.date_input("📅 From", value=min_date)
with col3:
    to_date = st.date_input("📅 To", value=max_date)

st.markdown("---")

# === FILTER DATA ===
filtered = []
for item in processed:
    if selected_sku != "ALL" and item["sku"] != selected_sku:
        continue
    if item["date"]:
        try:
            item_date = datetime.strptime(item["date"][:10], "%Y-%m-%d").date()
            if item_date < from_date or item_date > to_date:
                continue
        except:
            pass
    filtered.append(item)

# === STATS ===
stats = {"unshipped": 0, "intransit": 0, "delivered": 0, "rto": 0, "undelivered": 0}
for item in filtered:
    stats[item["category"]] += 1

total = len(filtered)
if total == 0:
    st.warning("📭 No orders found for selected filters")
    st.stop()

pct = {k: (v / total * 100) for k, v in stats.items()}

# === DISPLAY ===
sku_display = selected_sku if selected_sku != "ALL" else "All SKUs"
st.markdown(f"""
<div class="total-card">
    <div style="font-size: 1rem; color: #8b949e;">Total Orders for <strong>{sku_display}</strong></div>
    <div style="font-size: 3rem; font-weight: 700; color: #e6edf3;">{total}</div>
    <div style="color: #8b949e; font-size: 0.9rem;">{from_date.strftime('%b %d, %Y')} — {to_date.strftime('%b %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5 Cards
c1, c2, c3, c4, c5 = st.columns(5, gap="medium")
cards = [
    (c1, "unshipped", "📦 Unshipped"),
    (c2, "intransit", "🚚 In-Transit"),
    (c3, "delivered", "✅ Delivered"),
    (c4, "rto", "↩️ RTO"),
    (c5, "undelivered", "❌ Undelivered")
]
for col, key, label in cards:
    with col:
        st.markdown(f"""
        <div class="stat-card {key}">
            <div class="stat-value">{stats[key]}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-percent">{pct[key]:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

# Delivery Rate
st.markdown("<br>", unsafe_allow_html=True)
shipped_total = stats["intransit"] + stats["delivered"] + stats["rto"] + stats["undelivered"]
delivery_rate = (stats["delivered"] / shipped_total * 100) if shipped_total > 0 else 0

if delivery_rate >= 90:
    rc, re, rt = "#3fb950", "🏆", "Excellent"
elif delivery_rate >= 80:
    rc, re, rt = "#58a6ff", "👍", "Good"
elif delivery_rate >= 70:
    rc, re, rt = "#f0883e", "⚠️", "Needs Improvement"
else:
    rc, re, rt = "#f85149", "🚨", "Critical"

st.markdown(f"""
<div style="background: rgba(22, 27, 34, 0.9); border: 1px solid {rc}; border-radius: 12px; padding: 20px; text-align: center;">
    <div style="font-size: 1rem; color: #8b949e;">Delivery Success Rate</div>
    <div style="font-size: 3rem; font-weight: 700; color: {rc};">{delivery_rate:.1f}%</div>
    <div style="font-size: 1.2rem; color: {rc};">{re} {rt}</div>
</div>
""", unsafe_allow_html=True)

# Table
st.markdown("---")
st.markdown("### 📋 Order Details")

filter_cat = st.selectbox("Filter", ["All", "Unshipped", "In-Transit", "Delivered", "RTO", "Undelivered"])
cat_map = {"Unshipped": "unshipped", "In-Transit": "intransit", "Delivered": "delivered", "RTO": "rto", "Undelivered": "undelivered"}

if filter_cat != "All":
    table_data = [o for o in filtered if o["category"] == cat_map[filter_cat]]
else:
    table_data = filtered

if table_data:
    display_df = pd.DataFrame(table_data)[["order_id", "sku", "date", "status", "awb", "courier"]]
    display_df.columns = ["Order ID", "SKU", "Date", "Status", "AWB", "Courier"]
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    csv = display_df.to_csv(index=False)
    st.download_button("📥 Export to CSV", csv, f"analytics_{selected_sku}.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.caption(f"📊 {data_source} • {total} orders • Updated {datetime.now().strftime('%I:%M %p')}")
