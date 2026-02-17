"""
📈 Analytics Page - SKU Delivery Performance
Uses pre-processed data for instant loading
"""

import streamlit as st
import pandas as pd
import json
import os
import subprocess
from datetime import datetime, timedelta

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
}
.stat-card:hover { border-color: #58a6ff; }
.stat-value { font-size: 2rem; font-weight: 700; margin-bottom: 4px; }
.stat-label { color: #8b949e; font-size: 0.85rem; margin-bottom: 8px; }
.stat-percent { font-size: 1rem; font-weight: 600; }

.unshipped { border-left: 4px solid #8b949e; }
.unshipped .stat-value, .unshipped .stat-percent { color: #8b949e; }

.intransit { border-left: 4px solid #58a6ff; }
.intransit .stat-value, .intransit .stat-percent { color: #58a6ff; }

.delivered { border-left: 4px solid #3fb950; }
.delivered .stat-value, .delivered .stat-percent { color: #3fb950; }

.rto { border-left: 4px solid #f85149; }
.rto .stat-value, .rto .stat-percent { color: #f85149; }

.undelivered { border-left: 4px solid #f0883e; }
.undelivered .stat-value, .undelivered .stat-percent { color: #f0883e; }

.total-card {
    background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(139, 92, 246, 0.1));
    border: 1px solid #58a6ff;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
CSV_FILE = os.path.join(DATA_DIR, "analytics_data.csv")
STATS_FILE = os.path.join(DATA_DIR, "analytics_stats.json")

def load_data():
    """Load pre-processed data"""
    if os.path.exists(CSV_FILE) and os.path.exists(STATS_FILE):
        df = pd.read_csv(CSV_FILE)
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
        return df, stats
    return None, None

def refresh_data(days=30, from_date=None, to_date=None):
    """Run the fetch script to refresh data"""
    script_path = os.path.join(os.path.dirname(SCRIPT_DIR), "fetch_analytics.py")
    
    cmd = ["python", script_path]
    if from_date and to_date:
        cmd.extend(["--from-date", from_date, "--to-date", to_date])
    else:
        cmd.extend(["--days", str(days)])
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(SCRIPT_DIR))
    return result.returncode == 0, result.stdout, result.stderr

# === STATUS CATEGORIZATION (same as fetch_analytics.py) ===
def categorize_status(status):
    """Categorize status into 5 groups"""
    status = str(status).upper().strip()
    
    # Check RTO first
    if "RTO" in status or "RETURN" in status:
        return "rto"
    
    # Delivered
    if "DELIVERED" in status and "RTO" not in status and "UNDELIVERED" not in status:
        return "delivered"
    if status in ["COMPLETE", "FULFILLED"]:
        return "delivered"
    
    # Undelivered
    for s in ["UNDELIVERED", "FAILED", "DELIVERY FAILED", "LOST", "DAMAGED", "DESTROYED"]:
        if s in status:
            return "undelivered"
    
    # In-Transit
    for s in ["SHIPPED", "IN TRANSIT", "IN-TRANSIT", "PICKED UP", "OUT FOR DELIVERY",
              "REACHED AT DESTINATION", "DELIVERY DELAYED", "MISROUTED", "HANDOVER", "IN FLIGHT"]:
        if s in status:
            return "intransit"
    
    # Unshipped
    for s in ["NEW", "INVOICED", "PENDING", "AWB ASSIGNED", "LABEL GENERATED", 
              "PICKUP SCHEDULED", "PICKUP QUEUED", "MANIFEST GENERATED", "OUT FOR PICKUP", "SHIPMENT BOOKED"]:
        if s in status:
            return "unshipped"
    
    if "CANCEL" in status:
        return "unshipped"
    
    return "intransit"

def process_uploaded_csv(uploaded_file):
    """Process uploaded Shiprocket CSV export"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Map common Shiprocket CSV column names
        column_mapping = {
            # Order ID variations
            'Order ID': 'order_id', 'order_id': 'order_id', 'Order Id': 'order_id',
            'Channel Order ID': 'order_id', 'channel_order_id': 'order_id',
            # Date variations
            'Created At': 'date', 'created_at': 'date', 'Order Date': 'date',
            'order_date': 'date', 'Date': 'date',
            # Status variations
            'Status': 'status', 'status': 'status', 'Shipment Status': 'status',
            'shipment_status': 'status', 'Current Status': 'status',
            # SKU variations
            'SKU': 'sku', 'sku': 'sku', 'Channel SKU': 'sku', 'channel_sku': 'sku',
            'Product SKU': 'sku', 'product_sku': 'sku',
            # AWB variations
            'AWB': 'awb', 'awb': 'awb', 'AWB Code': 'awb', 'awb_code': 'awb',
            'Tracking Number': 'awb',
            # Courier variations
            'Courier': 'courier', 'courier': 'courier', 'Courier Name': 'courier',
            'courier_name': 'courier', 'Carrier': 'courier',
            # Product name
            'Product Name': 'product_name', 'product_name': 'product_name',
            'Product': 'product_name', 'Item Name': 'product_name'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required = ['order_id', 'status']
        for col in required:
            if col not in df.columns:
                return None, f"Missing required column: {col}"
        
        # Fill missing optional columns
        if 'date' not in df.columns:
            df['date'] = ''
        if 'sku' not in df.columns:
            df['sku'] = 'Unknown'
        if 'awb' not in df.columns:
            df['awb'] = ''
        if 'courier' not in df.columns:
            df['courier'] = ''
        if 'product_name' not in df.columns:
            df['product_name'] = ''
        
        # Clean date column
        df['date'] = df['date'].astype(str).str[:10]
        
        # Categorize status
        df['category'] = df['status'].apply(categorize_status)
        
        # Select final columns
        result_df = df[['order_id', 'date', 'status', 'category', 'sku', 'product_name', 'awb', 'courier']].copy()
        
        return result_df, None
    except Exception as e:
        return None, str(e)

# === HEADER ===
st.markdown("# 📈 SKU Delivery Analytics")
st.caption("Fast analytics with pre-processed data")
st.markdown("---")

# === LOAD DATA ===
df, stats = load_data()

# === DATA SOURCE TABS ===
tab1, tab2 = st.tabs(["🔄 Fetch from API", "📤 Upload CSV"])

with tab1:
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        date_mode = st.radio("Mode", ["Preset", "Custom Days", "Date Range"], horizontal=True)

    with col2:
        if date_mode == "Preset":
            days = st.selectbox("Period", [30, 60, 90, 180, 365], format_func=lambda x: f"Last {x} Days")
        elif date_mode == "Custom Days":
            days = st.number_input("Days", min_value=1, max_value=730, value=45, step=1)
        else:
            from_date = st.date_input("From", value=datetime.now() - timedelta(days=30))

    with col3:
        if date_mode == "Date Range":
            to_date = st.date_input("To", value=datetime.now())
        else:
            st.write("")

    with col4:
        st.write("")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            with st.spinner("⏳ Fetching data from Shiprocket..."):
                if date_mode in ["Preset", "Custom Days"]:
                    success, stdout, stderr = refresh_data(days=days)
                else:
                    success, stdout, stderr = refresh_data(
                        from_date=from_date.strftime("%Y-%m-%d"),
                        to_date=to_date.strftime("%Y-%m-%d")
                    )
                
                if success:
                    st.success("✅ Data refreshed!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {stderr}")

with tab2:
    st.markdown("Upload a CSV file exported from Shiprocket")
    st.caption("Supports order exports with columns: Order ID, Status, SKU, AWB, Courier, Date")
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="csv_upload")
    
    if uploaded_file is not None:
        with st.spinner("📊 Processing CSV..."):
            processed_df, error = process_uploaded_csv(uploaded_file)
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                # Show preview
                st.success(f"✅ Loaded {len(processed_df)} rows")
                
                with st.expander("📋 Preview Data", expanded=False):
                    st.dataframe(processed_df.head(20), use_container_width=True, hide_index=True)
                
                # Show category breakdown
                cat_counts = processed_df['category'].value_counts().to_dict()
                st.markdown(f"""
                **Categories found:**
                - 📦 Unshipped: {cat_counts.get('unshipped', 0)}
                - 🚚 In-Transit: {cat_counts.get('intransit', 0)}
                - ✅ Delivered: {cat_counts.get('delivered', 0)}
                - ↩️ RTO: {cat_counts.get('rto', 0)}
                - ❌ Undelivered: {cat_counts.get('undelivered', 0)}
                """)
                
                if st.button("💾 Save & Use This Data", type="primary", use_container_width=True):
                    # Save to data files
                    os.makedirs(DATA_DIR, exist_ok=True)
                    
                    # Save CSV
                    processed_df.to_csv(CSV_FILE, index=False)
                    
                    # Calculate and save stats
                    dates = processed_df['date'].dropna()
                    dates = dates[dates != '']
                    min_date = dates.min() if len(dates) > 0 else "N/A"
                    max_date = dates.max() if len(dates) > 0 else "N/A"
                    
                    new_stats = {
                        "total": len(processed_df),
                        "unshipped": cat_counts.get('unshipped', 0),
                        "intransit": cat_counts.get('intransit', 0),
                        "delivered": cat_counts.get('delivered', 0),
                        "rto": cat_counts.get('rto', 0),
                        "undelivered": cat_counts.get('undelivered', 0),
                        "skus": processed_df['sku'].nunique(),
                        "from_date": str(min_date),
                        "to_date": str(max_date),
                        "updated_at": datetime.now().isoformat(),
                        "source": "csv_upload"
                    }
                    
                    with open(STATS_FILE, "w") as f:
                        json.dump(new_stats, f, indent=2)
                    
                    st.success("✅ Data saved! Refreshing...")
                    st.rerun()

# Show data info
if stats:
    st.info(f"📁 **Data loaded:** {stats.get('from_date', 'N/A')} to {stats.get('to_date', 'N/A')} • {stats.get('total', 0)} orders • Updated {stats.get('updated_at', 'N/A')[:16]}")
else:
    st.warning("⚠️ No data found. Click **Refresh Data** to fetch from Shiprocket.")
    st.stop()

st.markdown("---")

# === SKU FILTER ===
all_skus = ["ALL"] + sorted(df["sku"].dropna().unique().tolist()) if df is not None else ["ALL"]
selected_sku = st.selectbox("🔍 Select SKU", all_skus)

# Filter data
if selected_sku != "ALL":
    filtered_df = df[df["sku"] == selected_sku]
else:
    filtered_df = df

# === CALCULATE STATS ===
total = len(filtered_df)
if total == 0:
    st.warning("📭 No data for selected SKU")
    st.stop()

cat_counts = filtered_df["category"].value_counts().to_dict()
s_unshipped = cat_counts.get("unshipped", 0)
s_intransit = cat_counts.get("intransit", 0)
s_delivered = cat_counts.get("delivered", 0)
s_rto = cat_counts.get("rto", 0)
s_undelivered = cat_counts.get("undelivered", 0)

# === DISPLAY ===
sku_display = selected_sku if selected_sku != "ALL" else "All SKUs"
st.markdown(f"""
<div class="total-card">
    <div style="font-size: 1rem; color: #8b949e;">Total Orders for <strong>{sku_display}</strong></div>
    <div style="font-size: 3rem; font-weight: 700; color: #e6edf3;">{total}</div>
    <div style="color: #8b949e; font-size: 0.9rem;">{stats.get('from_date', '')} — {stats.get('to_date', '')}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Net Total = only COMPLETED orders (Delivered + RTO + Undelivered)
# Excludes: Unshipped (not processed) and In-Transit (not final)
net_total = s_delivered + s_rto + s_undelivered

# 5 Cards
c1, c2, c3, c4, c5 = st.columns(5, gap="medium")

# Unshipped card (not part of net total)
with c1:
    st.markdown(f"""
    <div class="stat-card unshipped">
        <div class="stat-value">{s_unshipped}</div>
        <div class="stat-label">📦 Unshipped</div>
        <div class="stat-percent">Not shipped</div>
    </div>
    """, unsafe_allow_html=True)

# In-Transit card (not part of net total - still pending)
with c2:
    st.markdown(f"""
    <div class="stat-card intransit">
        <div class="stat-value">{s_intransit}</div>
        <div class="stat-label">🚚 In-Transit</div>
        <div class="stat-percent">Pending</div>
    </div>
    """, unsafe_allow_html=True)

# Completed cards (% of net total - these 3 add up to 100%)
completed_cards = [
    (c3, "delivered", "✅ Delivered", s_delivered),
    (c4, "rto", "↩️ RTO", s_rto),
    (c5, "undelivered", "❌ Undelivered", s_undelivered)
]

for col, key, label, count in completed_cards:
    pct = count / net_total * 100 if net_total > 0 else 0
    with col:
        st.markdown(f"""
        <div class="stat-card {key}">
            <div class="stat-value">{count}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-percent">{pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

# Net Delivery Rate (based on COMPLETED orders only)
st.markdown("<br>", unsafe_allow_html=True)
# net_total already defined above: Delivered + RTO + Undelivered (excludes In-Transit)
net_delivery_rate = (s_delivered / net_total * 100) if net_total > 0 else 0

if net_delivery_rate >= 90:
    rc, re, rt = "#3fb950", "🏆", "Excellent"
elif net_delivery_rate >= 80:
    rc, re, rt = "#58a6ff", "👍", "Good"
elif net_delivery_rate >= 70:
    rc, re, rt = "#f0883e", "⚠️", "Needs Improvement"
else:
    rc, re, rt = "#f85149", "🚨", "Critical"

st.markdown(f"""
<div style="background: rgba(22, 27, 34, 0.9); border: 1px solid {rc}; border-radius: 12px; padding: 20px; text-align: center;">
    <div style="font-size: 0.85rem; color: #8b949e; margin-bottom: 4px;">Net Total (Completed): <strong style="color: #e6edf3;">{net_total}</strong></div>
    <div style="font-size: 1rem; color: #8b949e;">Net Delivery %</div>
    <div style="font-size: 3rem; font-weight: 700; color: {rc};">{net_delivery_rate:.1f}%</div>
    <div style="font-size: 1.2rem; color: {rc};">{re} {rt}</div>
    <div style="font-size: 0.75rem; color: #6e7681; margin-top: 8px;">Delivered ÷ (Delivered + RTO + Undelivered)</div>
</div>
""", unsafe_allow_html=True)

# === ORDER TABLE ===
st.markdown("---")
st.markdown("### 📋 Order Details")

filter_cat = st.selectbox("Filter", ["All", "Unshipped", "In-Transit", "Delivered", "RTO", "Undelivered"])
cat_map = {"Unshipped": "unshipped", "In-Transit": "intransit", "Delivered": "delivered", "RTO": "rto", "Undelivered": "undelivered"}

if filter_cat != "All":
    table_df = filtered_df[filtered_df["category"] == cat_map[filter_cat]]
else:
    table_df = filtered_df

if len(table_df) > 0:
    display_df = table_df[["order_id", "sku", "date", "status", "awb", "courier"]].copy()
    display_df.columns = ["Order ID", "SKU", "Date", "Status", "AWB", "Courier"]
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    csv = display_df.to_csv(index=False)
    st.download_button("📥 Export to CSV", csv, f"analytics_{selected_sku}.csv", "text/csv", use_container_width=True)
else:
    st.info("No orders found")

st.markdown("---")
st.caption(f"📊 Data from: {stats.get('from_date', '')} to {stats.get('to_date', '')} • {total} orders")
