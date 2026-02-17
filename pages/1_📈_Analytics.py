"""
📈 Analytics Page - SKU Delivery Performance (File Upload)
Upload your Shiprocket export and analyze delivery metrics
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

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

.upload-zone {
    border: 2px dashed #30363d;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    background: rgba(22, 27, 34, 0.5);
}
</style>
""", unsafe_allow_html=True)

def categorize_status(status):
    """Group Shiprocket statuses into 5 categories"""
    status = str(status).upper().strip() if status else ""
    
    # Unshipped orders (not yet dispatched)
    unshipped_statuses = [
        "NEW", "INVOICED", "CANCELED", "CANCELLED", 
        "CANCELLATION REQUESTED", "CANCELLATION_REQUESTED",
        "PENDING PAYMENT", "PROCESSING"
    ]
    
    # In-Transit statuses
    intransit_statuses = [
        "PICKUP SCHEDULED", "PICKED UP", "IN TRANSIT", "OUT FOR DELIVERY",
        "SHIPPED", "PICKUP GENERATED", "PICKUP QUEUED", "IN_TRANSIT",
        "OUT_FOR_DELIVERY", "REACHED DESTINATION HUB", "REACHED AT DESTINATION HUB",
        "MISROUTED", "PENDING", "IN TRANSIT TO DESTINATION",
        "DISPATCHED", "MANIFESTED"
    ]
    
    # Delivered
    delivered_statuses = ["DELIVERED", "COMPLETE", "COMPLETED"]
    
    # RTO (Return to Origin)
    rto_statuses = [
        "RTO INITIATED", "RTO IN TRANSIT", "RTO DELIVERED", "RTO",
        "RTO_INITIATED", "RTO_INTRANSIT", "RTO_DELIVERED", "RETURNED",
        "RTO NDR", "RTO OFD", "RTO_NDR", "RTO_OFD", "RTO REQUESTED"
    ]
    
    # Undelivered / Failed (after shipping attempt)
    undelivered_statuses = [
        "UNDELIVERED", "FAILED", "DELIVERY FAILED", "LOST", "DAMAGED",
        "UNDELIVERED_RETURNED", "NDR", "NOT DELIVERED"
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
    
    # Default logic
    if "TRANSIT" in status or "PICKUP" in status or "SHIPPED" in status or "DISPATCH" in status:
        return "intransit"
    if "RTO" in status or "RETURN" in status:
        return "rto"
    if "DELIVER" in status:
        return "delivered"
    
    return "unshipped"  # Default to unshipped if unknown

def find_column(df, possible_names):
    """Find column by possible names (case-insensitive)"""
    df_cols_lower = {col.lower().strip(): col for col in df.columns}
    for name in possible_names:
        if name.lower() in df_cols_lower:
            return df_cols_lower[name.lower()]
    return None

def process_shiprocket_export(df):
    """Process Shiprocket export file and extract relevant data"""
    
    # Common column name mappings for Shiprocket exports
    sku_cols = ["sku", "sku code", "product sku", "item sku", "sku_code"]
    status_cols = ["status", "order status", "shipment status", "delivery status", "current status"]
    date_cols = ["created at", "order date", "date", "created_at", "order_date", "created date"]
    order_id_cols = ["order id", "order_id", "channel order id", "channel_order_id", "shiprocket order id"]
    awb_cols = ["awb", "awb code", "awb_code", "tracking number", "awb number"]
    courier_cols = ["courier", "courier name", "courier_name", "shipping provider"]
    
    # Find columns
    sku_col = find_column(df, sku_cols)
    status_col = find_column(df, status_cols)
    date_col = find_column(df, date_cols)
    order_id_col = find_column(df, order_id_cols)
    awb_col = find_column(df, awb_cols)
    courier_col = find_column(df, courier_cols)
    
    if not status_col:
        st.error("❌ Could not find 'Status' column in the file. Please check your export.")
        st.write("**Available columns:**", list(df.columns))
        return None, []
    
    # Process data
    processed_data = []
    all_skus = set()
    
    for _, row in df.iterrows():
        sku = str(row[sku_col]).strip() if sku_col and pd.notna(row[sku_col]) else "Unknown"
        status = str(row[status_col]).strip() if pd.notna(row[status_col]) else ""
        date_val = str(row[date_col])[:10] if date_col and pd.notna(row[date_col]) else ""
        order_id = str(row[order_id_col]) if order_id_col and pd.notna(row[order_id_col]) else ""
        awb = str(row[awb_col]) if awb_col and pd.notna(row[awb_col]) else ""
        courier = str(row[courier_col]) if courier_col and pd.notna(row[courier_col]) else ""
        
        category = categorize_status(status)
        
        if sku and sku != "Unknown" and sku != "nan":
            all_skus.add(sku)
        
        processed_data.append({
            "order_id": order_id,
            "sku": sku,
            "status": status,
            "category": category,
            "date": date_val,
            "awb": awb,
            "courier": courier
        })
    
    return processed_data, sorted(list(all_skus))

# === HEADER ===
st.markdown("# 📈 SKU Delivery Analytics")
st.caption("Upload your Shiprocket export to analyze delivery performance")
st.markdown("---")

# === FILE UPLOAD ===
st.markdown("### 📤 Upload Shiprocket Export")
st.caption("Export orders from Shiprocket dashboard and upload here (Excel or CSV)")

uploaded_file = st.file_uploader(
    "Choose file",
    type=["xlsx", "xls", "csv"],
    help="Export orders from Shiprocket → Download as Excel/CSV → Upload here"
)

if not uploaded_file:
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size: 48px; margin-bottom: 16px;">📁</div>
        <div style="color: #8b949e; font-size: 1.1rem;">Drag & drop your Shiprocket export here</div>
        <div style="color: #6e7681; font-size: 0.9rem; margin-top: 8px;">Supports: .xlsx, .xls, .csv</div>
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background: rgba(88, 166, 255, 0.1); border-radius: 12px; border: 1px solid #30363d;">
        <div style="font-weight: 600; color: #58a6ff; margin-bottom: 12px;">📋 How to export from Shiprocket:</div>
        <ol style="color: #8b949e; margin: 0; padding-left: 20px;">
            <li>Go to Shiprocket Dashboard → Orders</li>
            <li>Set date range (e.g., Last 30 days)</li>
            <li>Click "Export" → Download Excel/CSV</li>
            <li>Upload the file here</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# === LOAD FILE ===
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")
except Exception as e:
    st.error(f"❌ Error reading file: {e}")
    st.stop()

# === PROCESS DATA ===
with st.spinner("🔄 Processing data..."):
    processed_data, all_skus = process_shiprocket_export(df)

if not processed_data:
    st.stop()

st.markdown("---")

# === FILTERS ===
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    sku_options = ["ALL"] + all_skus
    selected_sku = st.selectbox(
        "🔍 Select SKU",
        options=sku_options,
        index=0,
        help="Filter by specific SKU"
    )

# Get date range from data
dates_in_data = [d["date"] for d in processed_data if d["date"]]
if dates_in_data:
    try:
        date_objects = [datetime.strptime(d[:10], "%Y-%m-%d") for d in dates_in_data if d and len(d) >= 10]
        if date_objects:
            min_date = min(date_objects).date()
            max_date = max(date_objects).date()
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()
    except:
        min_date = datetime.now().date() - timedelta(days=30)
        max_date = datetime.now().date()
else:
    min_date = datetime.now().date() - timedelta(days=30)
    max_date = datetime.now().date()

with col2:
    from_date = st.date_input("📅 From", value=min_date, min_value=min_date, max_value=max_date)

with col3:
    to_date = st.date_input("📅 To", value=max_date, min_value=min_date, max_value=max_date)

st.markdown("---")

# === FILTER DATA ===
filtered_data = []
for item in processed_data:
    # SKU filter
    if selected_sku != "ALL" and item["sku"] != selected_sku:
        continue
    
    # Date filter
    if item["date"]:
        try:
            item_date = datetime.strptime(item["date"][:10], "%Y-%m-%d").date()
            if item_date < from_date or item_date > to_date:
                continue
        except:
            pass
    
    filtered_data.append(item)

# === CALCULATE STATS ===
stats = {"unshipped": 0, "intransit": 0, "delivered": 0, "rto": 0, "undelivered": 0}

for item in filtered_data:
    stats[item["category"]] += 1

total = len(filtered_data)

if total == 0:
    st.warning(f"📭 No orders found for selected filters")
    st.stop()

# Calculate percentages
pct_unshipped = (stats["unshipped"] / total * 100)
pct_intransit = (stats["intransit"] / total * 100)
pct_delivered = (stats["delivered"] / total * 100)
pct_rto = (stats["rto"] / total * 100)
pct_undelivered = (stats["undelivered"] / total * 100)

# === TOTAL ORDERS BANNER ===
sku_display = selected_sku if selected_sku != "ALL" else "All SKUs"
st.markdown(f"""
<div class="total-card">
    <div style="font-size: 1rem; color: #8b949e;">Total Orders for <strong>{sku_display}</strong></div>
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

shipped_total = stats["intransit"] + stats["delivered"] + stats["rto"] + stats["undelivered"]
delivery_rate = (stats["delivered"] / shipped_total * 100) if shipped_total > 0 else 0

if delivery_rate >= 90:
    rate_color, rate_emoji, rate_text = "#3fb950", "🏆", "Excellent"
elif delivery_rate >= 80:
    rate_color, rate_emoji, rate_text = "#58a6ff", "👍", "Good"
elif delivery_rate >= 70:
    rate_color, rate_emoji, rate_text = "#f0883e", "⚠️", "Needs Improvement"
else:
    rate_color, rate_emoji, rate_text = "#f85149", "🚨", "Critical"

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

filter_category = st.selectbox(
    "Filter by Status",
    ["All", "Unshipped", "In-Transit", "Delivered", "RTO", "Undelivered"],
    index=0
)

if filter_category != "All":
    category_map = {"Unshipped": "unshipped", "In-Transit": "intransit", "Delivered": "delivered", "RTO": "rto", "Undelivered": "undelivered"}
    table_data = [o for o in filtered_data if o["category"] == category_map[filter_category]]
else:
    table_data = filtered_data

if table_data:
    display_df = pd.DataFrame(table_data)
    display_df = display_df.rename(columns={
        "order_id": "Order ID",
        "sku": "SKU",
        "status": "Status",
        "date": "Date",
        "awb": "AWB",
        "courier": "Courier"
    })
    display_df = display_df[["Order ID", "SKU", "Date", "Status", "AWB", "Courier"]]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    csv = display_df.to_csv(index=False)
    st.download_button(
        "📥 Export Filtered Data to CSV",
        csv,
        f"analytics_{selected_sku}_{from_date}_{to_date}.csv",
        "text/csv",
        use_container_width=True
    )
else:
    st.info("No orders found for selected filter")

# === FOOTER ===
st.markdown("---")
st.caption(f"📊 File: {uploaded_file.name} • {len(df)} total rows • Processed at {datetime.now().strftime('%I:%M %p')}")
