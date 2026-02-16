"""
Admin Control Panel - Shiprocket Dashboard
==========================================
Admin features: Status, Stats, Logs, Bulk Label Download

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import requests
import json
from datetime import datetime
from io import BytesIO

st.set_page_config(
    page_title="🎛️ Admin Panel | JSK Labs",
    page_icon="🎛️",
    layout="wide"
)

# Configuration
GITHUB_REPO = "jsk-labs-maker/shiprocket-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/public"

# Shiprocket API
SHIPROCKET_API_BASE = "https://apiv2.shiprocket.in/v1/external"

# --- Helper Functions ---

def shiprocket_authenticate():
    """Authenticate with Shiprocket API."""
    # For now, show message that credentials needed
    # In production, read from Streamlit secrets
    st.warning("⚠️ Shiprocket credentials needed. Set in Streamlit Secrets.")
    return None

def download_labels_by_awb(awb_list, token):
    """Download labels for given AWB numbers."""
    if not token:
        return None
    
    url = f"{SHIPROCKET_API_BASE}/courier/generate/label"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Note: Shiprocket API uses shipment_id, not AWB
    # We'll need to first convert AWB to shipment_id
    # For now, show placeholder
    
    payload = {
        "awbs": awb_list  # This might need adjustment based on actual API
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            label_url = data.get("label_url")
            if label_url:
                label_response = requests.get(label_url, timeout=30)
                return label_response.content
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

@st.cache_data(ttl=10)
def fetch_processing_status():
    """Fetch current processing status from GitHub."""
    try:
        url = f"{GITHUB_RAW_BASE}/status.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=60)
def fetch_latest_labels():
    """Fetch latest labels metadata."""
    try:
        url = f"{GITHUB_RAW_BASE}/latest_labels.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=60)
def fetch_batches_history():
    """Fetch batches history."""
    try:
        url = f"{GITHUB_RAW_BASE}/batches_history.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("batches", [])
        return []
    except:
        return []

# --- UI ---

st.title("🎛️ Admin Control Panel")
st.markdown("**Manage shipping operations**")

st.markdown("---")

# === SECTION 1: STATUS & QUICK ACTIONS ===
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🟢 System Status")
    status_data = fetch_processing_status()
    
    if status_data:
        status = status_data.get("status", "idle")
        message = status_data.get("message", "")
        
        if status == "processing":
            st.info(f"🔄 **PROCESSING:** {message}")
            progress = status_data.get("progress", 0)
            if progress > 0:
                st.progress(progress / 100)
        elif status == "complete":
            st.success(f"✅ **COMPLETE:** {message}")
        elif status == "error":
            st.error(f"❌ **ERROR:** {message}")
        else:
            st.success("🟢 **IDLE** - Ready for tasks")
            latest = fetch_latest_labels()
            if latest:
                last_run = latest.get("date_display", "Unknown")
                st.caption(f"Last run: {last_run}")
    else:
        st.info("Status unavailable")

with col2:
    st.markdown("### ⚡ Quick Actions")
    if st.button("🚀 Ship Now", use_container_width=True):
        st.info("💬 Send to Telegram:")
        st.code("Ship them buddy")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# === SECTION 2: TODAY'S OVERVIEW ===
st.markdown("### 📊 Today's Overview")

batches = fetch_batches_history()
today = datetime.now().strftime('%Y-%m-%d')
today_batches = [b for b in batches if b.get("date") == today]

if today_batches:
    total_shipped = sum(b.get("shipped", 0) for b in today_batches)
    total_failed = sum(b.get("unshipped", 0) for b in today_batches)
    success_rate = (total_shipped / (total_shipped + total_failed) * 100) if (total_shipped + total_failed) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Batches", len(today_batches))
    with col2:
        st.metric("Shipped", f"{total_shipped} ✅")
    with col3:
        st.metric("Failed", f"{total_failed} ❌")
    with col4:
        st.metric("Success Rate", f"{success_rate:.1f}%")
else:
    st.info("No batches processed today yet")

st.markdown("---")

# === SECTION 3: BULK LABEL DOWNLOAD ===
st.markdown("### 📥 Bulk Label Download")

st.markdown("""
**Enter AWB numbers** (one per line) to download labels:
""")

awb_input = st.text_area(
    "AWB Numbers",
    height=150,
    placeholder="284931134807362\n284931134821395\n284931134821922",
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("📥 Download Labels", type="primary", use_container_width=True):
        if not awb_input.strip():
            st.error("Please enter at least one AWB number")
        else:
            # Parse AWB numbers
            awb_list = [line.strip() for line in awb_input.strip().split('\n') if line.strip()]
            
            st.info(f"🔍 Found {len(awb_list)} AWB numbers")
            
            # For now, show implementation note
            st.warning("""
            **⚙️ Implementation Note:**
            
            This feature needs Shiprocket API credentials configured.
            
            **Two options:**
            1. **Via Telegram** (Recommended): Message me the AWBs, I'll send labels
            2. **Direct API**: Add Shiprocket credentials to Streamlit Secrets
            
            For now, use option 1 - message me on Telegram! 📱
            """)
            
            # Show parsed AWBs
            with st.expander("AWB List"):
                for i, awb in enumerate(awb_list, 1):
                    st.code(f"{i}. {awb}")

with col2:
    st.caption("""
    💡 **Tips:**
    - Paste one AWB per line
    - Can handle 100+ AWBs at once
    - Works for ANY order (not just our batches)
    """)

st.markdown("---")

# === SECTION 4: PROCESSING LOG ===
st.markdown("### 📝 Recent Activity")

# Show latest 10 batches
recent_batches = batches[:10]

if recent_batches:
    for batch in recent_batches:
        time_display = f"{batch.get('date', '')} {batch.get('time', '')}"
        shipped = batch.get('shipped', 0)
        failed = batch.get('unshipped', 0)
        
        icon = "✅" if failed == 0 else "⚠️"
        
        st.markdown(f"""
        **{icon} {time_display}**  
        Shipped: {shipped} | Failed: {failed}
        """)
        st.markdown("---")
else:
    st.info("No recent activity")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by Kluzo 😎 for JSK Labs")
