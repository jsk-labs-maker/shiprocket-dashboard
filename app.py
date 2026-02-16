"""
Staff Dashboard - Simple Label Downloader
==========================================
Fetches labels from GitHub repo. No local files needed.

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import requests
import json
from datetime import datetime
from io import BytesIO
import zipfile
import tempfile

st.set_page_config(
    page_title="📦 Labels - JSK Labs",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Configuration
GITHUB_REPO = "jsk-labs-maker/shiprocket-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/public"

# --- Helper Functions ---

@st.cache_data(ttl=10)  # Cache for 10 seconds (faster updates)
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


@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_latest_labels():
    """Fetch latest labels metadata from GitHub."""
    try:
        url = f"{GITHUB_RAW_BASE}/latest_labels.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_zip_download_url(zip_filename):
    """Get GitHub raw URL for ZIP file."""
    return f"{GITHUB_RAW_BASE}/{zip_filename}"


def get_courier_emoji(courier):
    """Get emoji for courier."""
    emoji_map = {
        'Delhivery': '🔵',
        'Ekart': '🟡',
        'Xpressbees': '🟣',
        'BlueDart': '🔴',
        'DTDC': '🟢',
        'Shadowfax': '🟠',
        'EcomExpress': '⚫'
    }
    return emoji_map.get(courier, '📦')


def download_and_extract_label(zip_url, filename):
    """Download ZIP and extract specific label file."""
    try:
        response = requests.get(zip_url, timeout=30)
        if response.status_code == 200:
            with zipfile.ZipFile(BytesIO(response.content)) as zf:
                return zf.read(filename)
        return None
    except:
        return None


# --- UI ---

# Header with emoji
st.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='font-size: 3rem; margin: 0;'>📦</h1>
    <h2 style='margin: 0.5rem 0;'>आज के लेबल्स</h2>
    <p style='color: #666; margin: 0;'>Today's Labels</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Live processing status banner
status_data = fetch_processing_status()
if status_data and status_data.get("status") == "processing":
    st.info(f"🔄 **{status_data.get('message', 'Processing orders...')}**")
    progress = status_data.get("progress", 0)
    if progress > 0:
        st.progress(progress / 100)
    st.caption("Please wait... Dashboard will auto-update when complete.")
    st.markdown("---")
elif status_data and status_data.get("status") == "complete":
    st.success(f"✅ **{status_data.get('message', 'Processing complete!')}**")
    st.caption("Showing latest batch below")
    st.markdown("---")

# Ship Now button (admin feature)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Ship Now", type="primary", use_container_width=True):
        # Trigger via webhook or show Telegram command
        st.warning("⚠️ Make sure you have NEW orders in Shiprocket!")
        
        # For now, show telegram command (will implement webhook later)
        st.info("💬 Send this message to Kluzo on Telegram:")
        st.code("Ship them buddy", language=None)
        st.caption("Dashboard will auto-update after processing (~2-3 minutes)")

st.markdown("---")

# Fetch labels
with st.spinner("Loading labels..."):
    labels_data = fetch_latest_labels()

if not labels_data:
    st.info("🔍 No labels available yet. Wait for orders to be processed.")
    st.caption("Labels appear here after running 'Ship them buddy'")
    st.stop()

# Show timestamp
timestamp_str = labels_data.get("date_display", "Unknown")
st.markdown(f"<p style='text-align: center; color: #888;'>📅 {timestamp_str}</p>", unsafe_allow_html=True)

# Show summary stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Total", labels_data.get("total_orders", 0))
with col2:
    st.metric("✅ Shipped", labels_data.get("shipped", 0))
with col3:
    st.metric("❌ Unshipped", labels_data.get("unshipped", 0))

st.markdown("---")

# Get ZIP URL
zip_filename = labels_data.get("zip_filename", "")
zip_url = get_zip_download_url(zip_filename) if zip_filename else None

# Download entire ZIP button
if zip_url:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h3>📥 Download All Labels</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        response = requests.get(zip_url, timeout=30)
        if response.status_code == 200:
            st.download_button(
                label="⬇️ Download All Labels (ZIP)",
                data=response.content,
                file_name=zip_filename,
                mime="application/zip",
                type="primary",
                use_container_width=True
            )
    except:
        st.error("Could not fetch labels from GitHub")

st.markdown("---")
st.markdown("<h3 style='text-align: center;'>📋 Labels by SKU</h3>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Display labels organized by SKU
labels_sorted = labels_data.get("labels_sorted", {})

for sku, couriers in sorted(labels_sorted.items()):
    # SKU header with box
    st.markdown(f"""
    <div style='background: #f0f0f0; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h3 style='margin: 0; font-size: 1.5rem;'>🏷️ {sku}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Courier buttons
    cols = st.columns(len(couriers))
    
    for i, (courier, info) in enumerate(sorted(couriers.items())):
        with cols[i]:
            label_count = info.get("count", 0)
            filepath = info.get("path", "")
            filename = filepath.split('/')[-1] if filepath else ""
            
            # Get emoji
            emoji = get_courier_emoji(courier)
            
            # Display info
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 0.5rem;'>
                <div style='font-size: 2rem;'>{emoji}</div>
                <div style='font-weight: bold;'>{courier}</div>
                <div style='color: #666; font-size: 0.9rem;'>{label_count} labels</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Download button
            if zip_url and filename:
                label_data = download_and_extract_label(zip_url, filename)
                if label_data:
                    st.download_button(
                        label=f"⬇️ Download",
                        data=label_data,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"dl_{sku}_{courier}",
                        use_container_width=True
                    )
                else:
                    st.error("File not found", icon="⚠️")
    
    st.markdown("<br>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9rem;'>
    <p>🚚 Pickup scheduled for tomorrow</p>
    <p>Built with ❤️ by JSK Labs</p>
</div>
""", unsafe_allow_html=True)

# Refresh button
if st.button("🔄 Refresh", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
