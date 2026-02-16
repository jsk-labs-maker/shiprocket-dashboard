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
    try:
        # Try to get API key from Streamlit secrets first
        if hasattr(st, 'secrets') and 'shiprocket' in st.secrets:
            api_key = st.secrets['shiprocket'].get('api_key')
            
            # If API key provided, use it directly (no login needed)
            if api_key:
                return api_key
            
            # Fallback to email/password authentication
            email = st.secrets['shiprocket'].get('email')
            password = st.secrets['shiprocket'].get('password')
        else:
            # Fallback to env file for local testing
            from dotenv import load_dotenv
            import os
            load_dotenv()
            api_key = os.getenv('SHIPROCKET_API_KEY')
            
            if api_key:
                return api_key
            
            email = os.getenv('SHIPROCKET_EMAIL')
            password = os.getenv('SHIPROCKET_PASSWORD')
        
        # If API key found, return it
        if api_key:
            return api_key
        
        # Otherwise, authenticate with email/password
        if not email or not password:
            return None
        
        url = f"{SHIPROCKET_API_BASE}/auth/login"
        response = requests.post(url, json={"email": email, "password": password}, timeout=10)
        
        if response.status_code == 200:
            return response.json()["token"]
        return None
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return None

def get_shipment_id_by_awb(awb, token):
    """Get shipment ID for an AWB number."""
    url = f"{SHIPROCKET_API_BASE}/courier/track/awb/{awb}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tracking_data = data.get("tracking_data", {})
            return tracking_data.get("shipment_id")
        return None
    except:
        return None


def download_labels_by_awb(awb_list, token):
    """Download labels for given AWB numbers."""
    if not token:
        return None, []
    
    results = []
    shipment_ids = []
    
    # Step 1: Convert AWBs to shipment IDs
    for awb in awb_list:
        shipment_id = get_shipment_id_by_awb(awb, token)
        if shipment_id:
            shipment_ids.append(shipment_id)
            results.append({"awb": awb, "status": "found", "shipment_id": shipment_id})
        else:
            results.append({"awb": awb, "status": "not_found"})
    
    if not shipment_ids:
        return None, results
    
    # Step 2: Download labels for all shipment IDs
    url = f"{SHIPROCKET_API_BASE}/courier/generate/label"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {"shipment_id": shipment_ids}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            label_url = data.get("label_url")
            
            if label_url:
                # Download the PDF
                label_response = requests.get(label_url, timeout=30)
                if label_response.status_code == 200:
                    return label_response.content, results
        
        return None, results
    except Exception as e:
        st.error(f"Download error: {str(e)}")
        return None, results

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
    if st.button("🚀 Ship Orders Now", type="primary", use_container_width=True):
        st.info("🔄 Starting shipping workflow...")
        
        # Progress placeholder
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            from shiprocket_workflow import run_shipping_workflow
            
            progress_text.text("🔐 Authenticating...")
            progress_bar.progress(20)
            
            progress_text.text("📋 Fetching NEW orders...")
            progress_bar.progress(40)
            
            progress_text.text("🚀 Shipping orders...")
            progress_bar.progress(60)
            
            # Run the workflow
            result = run_shipping_workflow()
            
            progress_bar.progress(100)
            progress_text.empty()
            
            # Show results
            st.markdown("### 📊 Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("NEW Orders", result.get("total_orders", 0))
            with col2:
                st.metric("✅ Shipped", result.get("shipped", 0))
            with col3:
                st.metric("❌ Failed", result.get("failed", 0))
            with col4:
                st.metric("⏭️ Skipped", result.get("skipped", 0))
            
            # Additional status
            st.markdown("### 📋 Workflow Status")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pickup = result.get("pickup_scheduled", 0)
                shipped = result.get("shipped", 0)
                if pickup > 0:
                    st.success(f"🚚 Pickup: {pickup}/{shipped}")
                else:
                    st.info("🚚 Pickup: Not scheduled")
            
            with col2:
                if result.get("labels_downloaded"):
                    st.success("📄 Labels: ✅ Downloaded")
                else:
                    st.info("📄 Labels: ⚠️ Not downloaded")
            
            with col3:
                if result.get("manifest_generated"):
                    st.success("📋 Manifest: ✅ Generated")
                else:
                    st.info("📋 Manifest: ⚠️ Not generated")
            
            if result.get("shipped", 0) > 0:
                st.success(f"✅ Successfully processed {result['shipped']} orders!")
                st.info("📥 Check staff dashboard for labels (GitHub upload coming soon)")
            else:
                st.warning(f"⚠️ No orders shipped")
                
                if result.get("errors"):
                    with st.expander("❌ Error Details"):
                        for error in result["errors"]:
                            if "Traceback" not in error:
                                st.error(error)
            
            # Show details
            if result.get("details"):
                with st.expander("📋 Detailed Log"):
                    for detail in result["details"]:
                        st.text(detail)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Debug Info"):
                st.code(traceback.format_exc())
        finally:
            progress_text.empty()
            progress_bar.empty()
    
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
            
            st.info(f"🔍 Processing {len(awb_list)} AWB numbers...")
            
            # Authenticate
            with st.spinner("🔐 Authenticating..."):
                token = shiprocket_authenticate()
            
            if not token:
                st.error("❌ Authentication failed. Please configure Shiprocket credentials in Streamlit Secrets.")
                st.info("""
                **Setup Instructions:**
                1. Go to Streamlit Cloud dashboard
                2. Open app settings → Secrets
                3. Add:
                ```toml
                [shiprocket]
                email = "openclawd12@gmail.com"
                password = "Kluzo@1212"
                ```
                """)
            else:
                # Download labels
                with st.spinner("📥 Downloading labels..."):
                    pdf_data, results = download_labels_by_awb(awb_list, token)
                
                # Show results
                st.markdown("### 📋 Results")
                
                found = [r for r in results if r["status"] == "found"]
                not_found = [r for r in results if r["status"] == "not_found"]
                
                if found:
                    st.success(f"✅ Found {len(found)} labels")
                    for r in found:
                        st.text(f"✓ {r['awb']}")
                
                if not_found:
                    st.warning(f"⚠️ Not found: {len(not_found)}")
                    for r in not_found:
                        st.text(f"✗ {r['awb']}")
                
                # Download button
                if pdf_data:
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    filename = f"labels_{timestamp}.pdf"
                    
                    st.download_button(
                        label="📥 Download All Labels (PDF)",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.success(f"✅ Ready! Click above to download {len(found)} labels")
                else:
                    st.error("❌ Could not generate labels PDF")

with col2:
    st.caption("""
    💡 **Tips:**
    - Paste one AWB per line
    - Can handle 100+ AWBs at once
    - Works for ANY order (not just our batches)
    - Download includes all found labels in one PDF
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
