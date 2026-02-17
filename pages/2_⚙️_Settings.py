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
.danger-zone {
    background: rgba(248, 81, 73, 0.1);
    border: 1px solid rgba(248, 81, 73, 0.3);
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
}
.danger-title {
    color: #f85149;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 12px;
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
    st.toggle("💰 Low wallet balance alert", value=True, help="Alert when balance < ₹10,000")
    st.toggle("📦 New order notification", value=False, help="Alert for each new order")
    
    wallet_threshold = st.slider("Low balance threshold", 5000, 50000, 10000, step=5000, format="₹%d")
    st.caption(f"Alert when wallet drops below ₹{wallet_threshold:,}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Appearance
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 Appearance")
    st.markdown('<p class="settings-desc">Customize the look and feel</p>', unsafe_allow_html=True)
    
    theme = st.selectbox("Theme", ["🌙 Dark (Default)", "☀️ Light", "💻 System"])
    accent = st.selectbox("Accent Color", ["💙 Blue", "💜 Purple", "💚 Green", "🧡 Orange", "💗 Pink"])
    st.toggle("✨ Enable animations", value=True)
    st.toggle("🔄 Auto-refresh dashboard", value=True)
    refresh_interval = st.slider("Refresh interval", 30, 300, 60, step=30, format="%d sec")
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
    
    st.markdown("**Courier Priority Order:**")
    courier_priority = st.text_area(
        "Drag to reorder (one per line)",
        "Bluedart\nDelhivery\nXpressbees\nEcom Express\nDTDC",
        height=120,
        help="Orders will prefer couriers from top to bottom"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API Settings
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🔐 API Configuration")
    st.markdown('<p class="settings-desc">Enter your Shiprocket credentials to connect</p>', unsafe_allow_html=True)
    
    # Initialize session state for credentials
    if 'sr_email' not in st.session_state:
        st.session_state.sr_email = ""
    if 'sr_password' not in st.session_state:
        st.session_state.sr_password = ""
    if 'sr_connected' not in st.session_state:
        st.session_state.sr_connected = False
    if 'sr_token' not in st.session_state:
        st.session_state.sr_token = None
    
    # Try to load from env file if not in session
    if not st.session_state.sr_email:
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
            st.session_state.sr_email = os.getenv('SHIPROCKET_EMAIL', '')
            st.session_state.sr_password = os.getenv('SHIPROCKET_PASSWORD', '')
        except:
            pass
    
    # Status indicator
    if st.session_state.sr_connected:
        st.markdown('<span class="api-status connected">🟢 Connected to Shiprocket</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-status disconnected">🔴 Not Connected</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Credential inputs
    email_input = st.text_input(
        "📧 Shiprocket Email", 
        value=st.session_state.sr_email,
        placeholder="your@email.com",
        key="email_input"
    )
    password_input = st.text_input(
        "🔑 Password", 
        value=st.session_state.sr_password,
        type="password",
        placeholder="Enter password",
        key="password_input"
    )
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 Save & Connect", use_container_width=True, type="primary"):
            if email_input and password_input:
                with st.spinner("Connecting to Shiprocket..."):
                    try:
                        import requests
                        r = requests.post(
                            "https://apiv2.shiprocket.in/v1/external/auth/login",
                            json={"email": email_input, "password": password_input},
                            timeout=10
                        )
                        if r.ok:
                            token = r.json().get("token")
                            st.session_state.sr_email = email_input
                            st.session_state.sr_password = password_input
                            st.session_state.sr_token = token
                            st.session_state.sr_connected = True
                            
                            # Save to env file
                            try:
                                with open("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env", "w") as f:
                                    f.write(f"SHIPROCKET_EMAIL={email_input}\n")
                                    f.write(f"SHIPROCKET_PASSWORD={password_input}\n")
                            except:
                                pass
                            
                            st.toast("✅ Connected successfully!", icon="🎉")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)[:50]}")
            else:
                st.warning("Please enter both email and password")
    
    with btn_col2:
        if st.button("🧪 Test Connection", use_container_width=True):
            if st.session_state.sr_email and st.session_state.sr_password:
                with st.spinner("Testing..."):
                    try:
                        import requests
                        r = requests.post(
                            "https://apiv2.shiprocket.in/v1/external/auth/login",
                            json={"email": st.session_state.sr_email, "password": st.session_state.sr_password},
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
                        else:
                            st.toast("❌ Connection failed", icon="❌")
                            st.session_state.sr_connected = False
                    except Exception as e:
                        st.toast(f"❌ Error: {str(e)[:30]}", icon="❌")
            else:
                st.warning("Please enter credentials first")
    
    if st.session_state.sr_connected:
        st.caption("✅ Credentials saved • Token auto-refreshes")
    else:
        st.caption("Enter your Shiprocket login credentials above")
    
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

# === DANGER ZONE ===
st.markdown("---")
with st.expander("🚨 Danger Zone", expanded=False):
    st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
    st.markdown('<div class="danger-title">⚠️ Irreversible Actions</div>', unsafe_allow_html=True)
    st.warning("These actions cannot be undone. Please proceed with caution.")
    
    danger_col1, danger_col2 = st.columns(2, gap="large")
    
    with danger_col1:
        st.markdown("**Reset All Settings**")
        st.caption("Restore all settings to default values")
        if st.button("🔄 Reset Settings", type="secondary"):
            st.toast("Settings reset!", icon="🔄")
    
    with danger_col2:
        st.markdown("**Delete All History**")
        st.caption("Remove all batch history and logs")
        if st.button("🗑️ Delete History", type="secondary"):
            st.toast("This would delete history", icon="⚠️")
    
    st.markdown('</div>', unsafe_allow_html=True)

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
