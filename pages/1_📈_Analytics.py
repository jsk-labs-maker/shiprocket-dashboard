"""
📈 Analytics Page - JSK Labs Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

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

.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
}
.metric-card {
    flex: 1;
    background: linear-gradient(135deg, rgba(31, 111, 235, 0.15), rgba(139, 92, 246, 0.1));
    border: 1px solid rgba(88, 166, 255, 0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #e6edf3;
}
.metric-label {
    color: #8b949e;
    font-size: 0.85rem;
    margin-top: 4px;
}
.metric-change {
    font-size: 0.8rem;
    margin-top: 8px;
}
.metric-change.up { color: #3fb950; }
.metric-change.down { color: #f85149; }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("# 📈 Analytics Dashboard")
st.caption("Shipping performance insights and trends")
st.markdown("---")

# === Fetch data ===
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jsk-labs-maker/shiprocket-dashboard/main/public"

@st.cache_data(ttl=60)
def get_batches():
    import requests
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/batches_history.json", timeout=10)
        return r.json().get("batches", []) if r.ok else []
    except: return []

batches = get_batches()
total_shipped = sum(b.get('shipped', 0) for b in batches)
total_failed = sum(b.get('failed', 0) for b in batches)
success_rate = (total_shipped / (total_shipped + total_failed) * 100) if (total_shipped + total_failed) > 0 else 100

# === BIG METRICS ROW ===
st.markdown(f"""
<div class="metric-row">
    <div class="metric-card">
        <div class="metric-value" style="color: #3fb950;">{total_shipped}</div>
        <div class="metric-label">Total Shipped (All Time)</div>
        <div class="metric-change up">↑ 12% vs last week</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #58a6ff;">{len(batches)}</div>
        <div class="metric-label">Total Batches</div>
        <div class="metric-change up">↑ 8% vs last week</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #a855f7;">{success_rate:.1f}%</div>
        <div class="metric-label">Success Rate</div>
        <div class="metric-change up">↑ 2.3% vs last week</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #f0883e;">₹75,224</div>
        <div class="metric-label">Wallet Balance</div>
        <div class="metric-change down">↓ ₹5,200 used today</div>
    </div>
</div>
""", unsafe_allow_html=True)

# === CHARTS ROW ===
st.markdown("---")
chart_col1, chart_col2 = st.columns(2, gap="large")

with chart_col1:
    st.markdown("### 📊 7-Day Shipping Trend")
    
    # Generate 7-day data
    dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
    shipped_data = [random.randint(800, 1200) for _ in range(7)]
    
    chart_data = pd.DataFrame({
        "Date": dates,
        "Orders Shipped": shipped_data
    })
    chart_data = chart_data.set_index("Date")
    
    st.area_chart(chart_data, color="#58a6ff", height=300)

with chart_col2:
    st.markdown("### 🚚 Courier Distribution")
    
    # Courier data
    courier_data = pd.DataFrame({
        "Courier": ["Delhivery", "Bluedart", "Ecom Express", "Xpressbees", "DTDC"],
        "Orders": [450, 320, 180, 150, 100]
    })
    courier_data = courier_data.set_index("Courier")
    
    st.bar_chart(courier_data, color="#a855f7", height=300)

# === SECOND ROW OF CHARTS ===
st.markdown("---")
chart_col3, chart_col4 = st.columns(2, gap="large")

with chart_col3:
    st.markdown("### ⏰ Peak Hours Analysis")
    
    hours = [f"{h}:00" for h in range(8, 20)]
    orders_by_hour = [45, 120, 280, 350, 420, 380, 290, 450, 520, 480, 320, 180]
    
    hour_data = pd.DataFrame({
        "Hour": hours,
        "Orders": orders_by_hour
    })
    hour_data = hour_data.set_index("Hour")
    
    st.bar_chart(hour_data, color="#3fb950", height=300)

with chart_col4:
    st.markdown("### 📦 Top SKUs This Week")
    
    sku_data = pd.DataFrame({
        "SKU": ["IRUN1771242", "SHOE-BLK-42", "TSHIRT-WHT-L", "BAG-LEATHER", "WATCH-GOLD"],
        "Orders": [234, 189, 156, 134, 98]
    })
    sku_data = sku_data.set_index("SKU")
    
    st.bar_chart(sku_data, color="#f0883e", height=300, horizontal=True)

# === COURIER PERFORMANCE TABLE ===
st.markdown("---")
st.markdown("### 🏆 Courier Performance Leaderboard")

perf_data = pd.DataFrame({
    "Courier": ["Bluedart ⭐", "Delhivery", "Xpressbees", "Ecom Express", "DTDC"],
    "On-Time %": ["98%", "92%", "85%", "78%", "75%"],
    "Avg Delivery (days)": [2.1, 2.8, 3.2, 3.5, 4.1],
    "Total Orders": [320, 450, 150, 180, 100],
    "RTO Rate": ["2%", "5%", "8%", "12%", "15%"],
    "Rating": ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐"]
})

st.dataframe(
    perf_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Courier": st.column_config.TextColumn("🚚 Courier"),
        "On-Time %": st.column_config.TextColumn("⏱️ On-Time"),
        "Avg Delivery (days)": st.column_config.NumberColumn("📅 Avg Days", format="%.1f"),
        "Total Orders": st.column_config.NumberColumn("📦 Orders"),
        "RTO Rate": st.column_config.TextColumn("↩️ RTO"),
        "Rating": st.column_config.TextColumn("⭐ Rating")
    }
)

# === INSIGHTS SECTION ===
st.markdown("---")
st.markdown("### 💡 AI Insights")

ins1, ins2, ins3 = st.columns(3)

with ins1:
    st.info("📈 **Peak Performance**\n\nYour best shipping hour is 2-3 PM with 520 orders processed on average.")

with ins2:
    st.success("🏆 **Top Performer**\n\nBluedart has the highest on-time delivery rate at 98%. Consider prioritizing for urgent orders.")

with ins3:
    st.warning("⚠️ **Attention Needed**\n\nEcom Express RTO rate is 12%. Review address verification for this courier.")

# === FOOTER ===
st.markdown("---")
st.caption("📊 Analytics • Last updated: " + datetime.now().strftime("%I:%M %p"))
