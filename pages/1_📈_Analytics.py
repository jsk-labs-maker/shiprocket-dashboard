"""
📈 Analytics Page - SKU Delivery Performance
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Analytics | Kluzo",
    page_icon="📈",
    layout="wide"
)

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

# === SHIPROCKET API ===
SHIPROCKET_API = "https://apiv2.shiprocket.in/v1/external"

def get_shiprocket_credentials():
    email = os.getenv("SHIPROCKET_EMAIL", "openclawd12@gmail.com")
    password = os.getenv("SHIPROCKET_PASSWORD", "Kluzo@1212")
    return email, password

@st.cache_data(ttl=300)
def get_auth_token():
    email, password = get_shiprocket_credentials()
    try:
        r = requests.post(f"{SHIPROCKET_API}/auth/login", json={"email": email, "password": password}, timeout=15)
        return r.json().get("token", "") if r.ok else ""
    except:
        return ""

@st.cache_data(ttl=300)
def get_all_skus(token):
    """Fetch all unique SKUs from orders"""
    headers = {"Authorization": f"Bearer {token}"}
    skus = set()
    try:
        # Fetch from orders (multiple pages)
        for page in range(1, 6):  # First 5 pages
            r = requests.get(f"{SHIPROCKET_API}/orders", headers=headers, params={"per_page": 200, "page": page}, timeout=30)
            if r.ok:
                orders = r.json().get("data", [])
                if not orders:
                    break
                for order in orders:
                    for product in order.get("products", []):
                        sku = product.get("sku", "")
                        if sku:
                            skus.add(sku)
    except:
        pass
    return sorted(list(skus))

def get_orders_by_date_range(token, from_date, to_date):
    """Fetch orders within date range"""
    headers = {"Authorization": f"Bearer {token}"}
    all_orders = []
    try:
        for page in range(1, 20):  # Up to 20 pages
            params = {
                "per_page": 200,
                "page": page,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d")
            }
            r = requests.get(f"{SHIPROCKET_API}/orders", headers=headers, params=params, timeout=30)
            if r.ok:
                orders = r.json().get("data", [])
                if not orders:
                    break
                all_orders.extend(orders)
            else:
                break
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
    return all_orders

def categorize_status(status):
    """Group Shiprocket statuses into 5 categories"""
    status = str(status).upper() if status else ""
    
    # Unshipped orders (not yet dispatched)
    unshipped_statuses = [
        "NEW", "INVOICED", "CANCELED", "CANCELLED", 
        "CANCELLATION REQUESTED", "CANCELLATION_REQUESTED"
    ]
    
    # In-Transit statuses
    intransit_statuses = [
        "PICKUP SCHEDULED", "PICKED UP", "IN TRANSIT", "OUT FOR DELIVERY",
        "SHIPPED", "PICKUP GENERATED", "PICKUP QUEUED", "IN_TRANSIT",
        "OUT_FOR_DELIVERY", "REACHED DESTINATION HUB", "REACHED AT DESTINATION HUB",
        "MISROUTED", "PENDING"
    ]
    
    # Delivered
    delivered_statuses = ["DELIVERED", "COMPLETE"]
    
    # RTO (Return to Origin)
    rto_statuses = [
        "RTO INITIATED", "RTO IN TRANSIT", "RTO DELIVERED", "RTO",
        "RTO_INITIATED", "RTO_INTRANSIT", "RTO_DELIVERED", "RETURNED",
        "RTO NDR", "RTO OFD", "RTO_NDR", "RTO_OFD"
    ]
    
    # Undelivered / Failed (after shipping attempt)
    undelivered_statuses = [
        "UNDELIVERED", "FAILED", "DELIVERY FAILED", "LOST", "DAMAGED",
        "UNDELIVERED_RETURNED"
    ]
    
    # Check unshipped first
    for s in unshipped_statuses:
        if s in status or status == s:
            return "unshipped"
    
    for s in delivered_statuses:
        if s in status:
            return "delivered"
    
    for s in rto_statuses:
        if s in status:
            return "rto"
    
    for s in undelivered_statuses:
        if s in status:
            return "undelivered"
    
    for s in intransit_statuses:
        if s in status:
            return "intransit"
    
    # Default to in-transit if status contains transit keywords
    if "TRANSIT" in status or "PICKUP" in status or "SHIPPED" in status:
        return "intransit"
    
    return "unshipped"  # Default to unshipped if unknown

def analyze_sku_performance(orders, selected_sku):
    """Analyze delivery performance for selected SKU"""
    stats = {
        "unshipped": 0,
        "intransit": 0,
        "delivered": 0,
        "rto": 0,
        "undelivered": 0,
        "total": 0
    }
    
    order_details = []
    
    for order in orders:
        # Check if order contains the selected SKU
        order_skus = [p.get("sku", "") for p in order.get("products", [])]
        
        if selected_sku == "ALL" or selected_sku in order_skus:
            # Get the order/shipment status
            status = order.get("status", "")
            
            # Also check shipment status if available
            shipments = order.get("shipments", [])
            if shipments:
                status = shipments[0].get("status", status)
            
            category = categorize_status(status)
            stats[category] += 1
            stats["total"] += 1
            
            # Store order details
            order_details.append({
                "order_id": order.get("channel_order_id", order.get("id", "")),
                "date": order.get("created_at", "")[:10],
                "status": status,
                "category": category,
                "awb": shipments[0].get("awb", "") if shipments else "",
                "courier": shipments[0].get("courier_name", "") if shipments else ""
            })
    
    return stats, order_details

# === HEADER ===
st.markdown("# 📈 SKU Delivery Analytics")
st.caption("Track delivery performance by SKU with custom date range")
st.markdown("---")

# === AUTH ===
token = get_auth_token()
if not token:
    st.error("❌ Failed to connect to Shiprocket. Check credentials.")
    st.stop()

# === FILTERS ===
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # SKU Dropdown with search
    all_skus = get_all_skus(token)
    sku_options = ["ALL"] + all_skus
    selected_sku = st.selectbox(
        "🔍 Select SKU",
        options=sku_options,
        index=0,
        help="Search or select a SKU to analyze"
    )

with col2:
    from_date = st.date_input(
        "📅 From Date",
        value=datetime.now() - timedelta(days=30),
        max_value=datetime.now()
    )

with col3:
    to_date = st.date_input(
        "📅 To Date",
        value=datetime.now(),
        max_value=datetime.now()
    )

# Validate dates
if from_date > to_date:
    st.error("❌ 'From Date' must be before 'To Date'")
    st.stop()

st.markdown("---")

# === FETCH & ANALYZE ===
with st.spinner("📊 Fetching orders from Shiprocket..."):
    orders = get_orders_by_date_range(token, from_date, to_date)

if not orders:
    st.warning(f"📭 No orders found between {from_date} and {to_date}")
    st.stop()

# Analyze
stats, order_details = analyze_sku_performance(orders, selected_sku)
total = stats["total"]

if total == 0:
    st.warning(f"📭 No orders found for SKU: {selected_sku}")
    st.stop()

# Calculate percentages
pct_unshipped = (stats["unshipped"] / total * 100) if total > 0 else 0
pct_intransit = (stats["intransit"] / total * 100) if total > 0 else 0
pct_delivered = (stats["delivered"] / total * 100) if total > 0 else 0
pct_rto = (stats["rto"] / total * 100) if total > 0 else 0
pct_undelivered = (stats["undelivered"] / total * 100) if total > 0 else 0

# === TOTAL ORDERS BANNER ===
st.markdown(f"""
<div class="total-card">
    <div style="font-size: 1rem; color: #8b949e;">Total Orders for <strong>{selected_sku}</strong></div>
    <div style="font-size: 3rem; font-weight: 700; color: #e6edf3;">{total}</div>
    <div style="color: #8b949e; font-size: 0.9rem;">{from_date.strftime('%b %d, %Y')} — {to_date.strftime('%b %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# === 5 STAT CARDS ===
c1, c2, c3, c4, c5 = st.columns(5, gap="medium")

with c1:
    st.markdown(f"""
    <div class="stat-card unshipped">
        <div class="stat-value">{stats["unshipped"]}</div>
        <div class="stat-label">📦 Unshipped</div>
        <div class="stat-percent">{pct_unshipped:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card intransit">
        <div class="stat-value">{stats["intransit"]}</div>
        <div class="stat-label">🚚 In-Transit</div>
        <div class="stat-percent">{pct_intransit:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card delivered">
        <div class="stat-value">{stats["delivered"]}</div>
        <div class="stat-label">✅ Delivered</div>
        <div class="stat-percent">{pct_delivered:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card rto">
        <div class="stat-value">{stats["rto"]}</div>
        <div class="stat-label">↩️ RTO</div>
        <div class="stat-percent">{pct_rto:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="stat-card undelivered">
        <div class="stat-value">{stats["undelivered"]}</div>
        <div class="stat-label">❌ Undelivered</div>
        <div class="stat-percent">{pct_undelivered:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# === DELIVERY SUCCESS RATE ===
st.markdown("<br>", unsafe_allow_html=True)

# Calculate delivery rate from shipped orders only (excluding unshipped)
shipped_total = stats["intransit"] + stats["delivered"] + stats["rto"] + stats["undelivered"]
delivery_rate = (stats["delivered"] / shipped_total * 100) if shipped_total > 0 else 0

if delivery_rate >= 90:
    rate_color = "#3fb950"
    rate_emoji = "🏆"
    rate_text = "Excellent"
elif delivery_rate >= 80:
    rate_color = "#58a6ff"
    rate_emoji = "👍"
    rate_text = "Good"
elif delivery_rate >= 70:
    rate_color = "#f0883e"
    rate_emoji = "⚠️"
    rate_text = "Needs Improvement"
else:
    rate_color = "#f85149"
    rate_emoji = "🚨"
    rate_text = "Critical"

st.markdown(f"""
<div style="background: rgba(22, 27, 34, 0.9); border: 1px solid {rate_color}; border-radius: 12px; padding: 20px; text-align: center;">
    <div style="font-size: 1rem; color: #8b949e;">Delivery Success Rate (from shipped orders)</div>
    <div style="font-size: 3rem; font-weight: 700; color: {rate_color};">{delivery_rate:.1f}%</div>
    <div style="font-size: 1.2rem; color: {rate_color};">{rate_emoji} {rate_text}</div>
    <div style="font-size: 0.85rem; color: #8b949e; margin-top: 8px;">Based on {shipped_total} shipped orders</div>
</div>
""", unsafe_allow_html=True)

# === ORDER DETAILS TABLE ===
st.markdown("---")
st.markdown("### 📋 Order Details")

# Filter options
filter_category = st.selectbox(
    "Filter by Status",
    ["All", "Unshipped", "In-Transit", "Delivered", "RTO", "Undelivered"],
    index=0
)

# Filter order details
if filter_category != "All":
    category_map = {"Unshipped": "unshipped", "In-Transit": "intransit", "Delivered": "delivered", "RTO": "rto", "Undelivered": "undelivered"}
    filtered_details = [o for o in order_details if o["category"] == category_map[filter_category]]
else:
    filtered_details = order_details

# Display table
if filtered_details:
    import pandas as pd
    df = pd.DataFrame(filtered_details)
    df = df.rename(columns={
        "order_id": "Order ID",
        "date": "Date",
        "status": "Status",
        "awb": "AWB",
        "courier": "Courier"
    })
    df = df[["Order ID", "Date", "Status", "AWB", "Courier"]]
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Export button
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Export to CSV",
        csv,
        f"sku_analytics_{selected_sku}_{from_date}_{to_date}.csv",
        "text/csv",
        use_container_width=True
    )
else:
    st.info("No orders found for selected filter")

# === FOOTER ===
st.markdown("---")
st.caption(f"📊 Last updated: {datetime.now().strftime('%I:%M %p')} • Data from Shiprocket API")
