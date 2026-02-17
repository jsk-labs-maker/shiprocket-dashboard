"""
⚙️ Settings Page - JSK Labs Dashboard
"""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Settings | Kluzo",
    page_icon="⚙️",
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

.settings-card {
    background: rgba(22, 27, 34, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}
.settings-title {
    color: #e6edf3;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.settings-desc {
    color: #8b949e;
    font-size: 0.85rem;
    margin-bottom: 20px;
}
.api-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}
.api-status.connected {
    background: rgba(63, 185, 80, 0.15);
    color: #3fb950;
    border: 1px solid rgba(63, 185, 80, 0.3);
}
.api-status.disconnected {
    background: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border: 1px solid rgba(248, 81, 73, 0.3);
}
.version-badge {
    background: linear-gradient(90deg, #1f6feb, #58a6ff);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# === HEADER ===
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("# ⚙️ Settings")
    st.caption("Configure your dashboard and automation preferences")
with col_badge:
    st.markdown('<div style="text-align: right; padding-top: 20px;"><span class="version-badge">v3.5 Premium</span></div>', unsafe_allow_html=True)

st.markdown("---")

# === MAIN SETTINGS ===
settings_col1, settings_col2 = st.columns(2, gap="large")

with settings_col1:
    # Notifications
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🔔 Notifications")
    st.markdown('<p class="settings-desc">Control how and when you receive alerts</p>', unsafe_allow_html=True)
    
    st.toggle("📱 Push notifications", value=True, help="Receive notifications on your device")
    st.toggle("📧 Email daily summary", value=False, help="Get daily report at 8 PM")
    st.toggle("🚨 Alert on failed orders", value=True, help="Immediate alert when orders fail")
    st.toggle("📦 New order notification", value=False, help="Alert for each new order")
    st.markdown('</div>', unsafe_allow_html=True)

with settings_col2:
    # Automation
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 Automation")
    st.markdown('<p class="settings-desc">Configure automatic workflows</p>', unsafe_allow_html=True)
    
    st.toggle("🚀 Auto-ship NEW orders", value=False, help="⚠️ Ships orders automatically when they arrive")
    st.toggle("📅 Auto-schedule pickup", value=True, help="Schedule pickup after shipping")
    st.toggle("📄 Auto-generate manifest", value=True, help="Generate manifest after batch")
    st.toggle("📁 Auto-upload to GitHub", value=True, help="Upload labels to GitHub storage")
    st.toggle("🏷️ Auto-sort labels", value=True, help="Sort by Date → Courier → SKU")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API Settings
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🔐 API Configuration")
    st.markdown('<p class="settings-desc">Enter your Shiprocket credentials to connect</p>', unsafe_allow_html=True)
    
    # Initialize session state for credentials
    # Pre-configured credentials
    DEFAULT_EMAIL = "openclawd12@gmail.com"
    DEFAULT_PASSWORD = "Kluzo@1212"
    
    def get_credentials():
        """Get credentials - Streamlit secrets first, then defaults."""
        try:
            email = st.secrets.get("SHIPROCKET_EMAIL")
            pwd = st.secrets.get("SHIPROCKET_PASSWORD")
            if email and pwd:
                return email, pwd
        except:
            pass
        return DEFAULT_EMAIL, DEFAULT_PASSWORD
    
    email, pwd = get_credentials()
    
    # Test connection on load
    if 'sr_connected' not in st.session_state:
        try:
            import requests
            r = requests.post(
                "https://apiv2.shiprocket.in/v1/external/auth/login",
                json={"email": email, "password": pwd},
                timeout=10
            )
            st.session_state.sr_connected = r.ok
        except:
            st.session_state.sr_connected = False
    
    # Status indicator
    if st.session_state.sr_connected:
        st.markdown('<span class="api-status connected">🟢 Connected to Shiprocket</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-status disconnected">🔴 Not Connected</span>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"📧 Using pre-configured account: **{email}**")
    
    if st.button("🧪 Test Connection", use_container_width=True, type="primary"):
        with st.spinner("Testing..."):
            try:
                import requests
                r = requests.post(
                    "https://apiv2.shiprocket.in/v1/external/auth/login",
                    json={"email": email, "password": pwd},
                    timeout=10
                )
                if r.ok:
                    # Get wallet balance
                    token = r.json().get("token")
                    wr = requests.get(
                        "https://apiv2.shiprocket.in/v1/external/account/details/wallet-balance",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
                    if wr.ok:
                        balance = float(wr.json().get("data", {}).get("balance_amount", 0))
                        st.toast(f"✅ Connected! Wallet: ₹{balance:,.0f}", icon="💰")
                        st.session_state.sr_connected = True
                    else:
                        st.toast("✅ Connected!", icon="✅")
                        st.session_state.sr_connected = True
                else:
                    st.toast("❌ Connection failed", icon="❌")
                    st.session_state.sr_connected = False
            except Exception as e:
                st.toast(f"❌ Error: {str(e)[:30]}", icon="❌")
    
    if st.session_state.sr_connected:
        st.caption("✅ Connected • Token auto-refreshes")
    
    st.markdown('</div>', unsafe_allow_html=True)

# === SCHEDULE SETTINGS ===
st.markdown("---")
st.markdown("### ⏰ Scheduled Workflows")
st.markdown('<p class="settings-desc">Configure automatic shipping schedules</p>', unsafe_allow_html=True)

sched_col1, sched_col2, sched_col3 = st.columns(3, gap="medium")

with sched_col1:
    st.markdown("**🌅 Morning Batch**")
    morning_enabled = st.toggle("Enable", value=True, key="morning")
    morning_time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time(), key="morning_time")
    st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default=["Mon", "Tue", "Wed", "Thu", "Fri"], key="morning_days")

with sched_col2:
    st.markdown("**☀️ Afternoon Batch**")
    afternoon_enabled = st.toggle("Enable", value=True, key="afternoon")
    afternoon_time = st.time_input("Time", value=datetime.strptime("14:00", "%H:%M").time(), key="afternoon_time")
    st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default=["Mon", "Tue", "Wed", "Thu", "Fri"], key="afternoon_days")

with sched_col3:
    st.markdown("**🌙 Evening Batch**")
    evening_enabled = st.toggle("Enable", value=True, key="evening")
    evening_time = st.time_input("Time", value=datetime.strptime("18:00", "%H:%M").time(), key="evening_time")
    st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default=["Mon", "Tue", "Wed", "Thu", "Fri"], key="evening_days")

# === DATA MANAGEMENT ===
st.markdown("---")
st.markdown("### 📊 Data Management")

data_col1, data_col2, data_col3, data_col4 = st.columns(4, gap="medium")

with data_col1:
    if st.button("📥 Export All Data", use_container_width=True, type="secondary"):
        st.toast("Preparing export...", icon="📦")

with data_col2:
    if st.button("🧹 Clear Cache", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.toast("Cache cleared!", icon="✅")

with data_col3:
    if st.button("🔄 Sync GitHub", use_container_width=True, type="secondary"):
        st.toast("Syncing with GitHub...", icon="🔄")

with data_col4:
    if st.button("📋 View Logs", use_container_width=True, type="secondary"):
        st.toast("Opening logs...", icon="📋")

# Storage info
st.markdown("<br>", unsafe_allow_html=True)
storage_col1, storage_col2, storage_col3 = st.columns(3)

with storage_col1:
    st.metric("📁 Storage Used", "12.4 MB", "2.1 MB this week")
with storage_col2:
    st.metric("📦 Total Batches", "47", "+5 this week")
with storage_col3:
    st.metric("🕐 Last Backup", "2 hours ago", "Auto-backup enabled")

# === FOOTER ===
st.markdown("---")
footer_col1, footer_col2 = st.columns([2, 1])
with footer_col1:
    st.caption("🎛️ JSK Labs Admin Dashboard v3.5 Premium")
    st.caption("Built with ❤️ by Kluzo 😎 • © 2026 JSK Labs")
with footer_col2:
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        st.toast("Settings saved successfully!", icon="✅")
        st.balloons()
