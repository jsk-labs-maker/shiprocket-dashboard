"""
Staff Dashboard - Simple Label Downloader
==========================================
Super simple UI for warehouse staff to download labels.
No login, just big buttons and easy downloads.

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import json

st.set_page_config(
    page_title="📦 Labels - JSK Labs",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Configuration
DATA_DIR = Path("data")
LABELS_DIR = DATA_DIR / "labels"
HISTORY_FILE = DATA_DIR / "shipping_history.json"

# --- Helper Functions ---

def load_latest_labels():
    """Load the most recent batch of sorted labels."""
    if not LABELS_DIR.exists():
        return None, []
    
    # Find latest date directory
    date_dirs = [d for d in LABELS_DIR.iterdir() if d.is_dir() and d.name.startswith('2026')]
    if not date_dirs:
        return None, []
    
    latest_dir = sorted(date_dirs, reverse=True)[0]
    
    # Parse label files
    labels = {}  # {sku: {courier: filepath}}
    
    for file in latest_dir.glob("*.pdf"):
        if file.name.endswith("_raw.pdf"):
            continue
        
        # Parse filename: YYYY-MM-DD_HHMM_SKU_Courier.pdf
        parts = file.stem.split('_')
        if len(parts) >= 4:
            sku = parts[2]
            courier = parts[3]
            
            if sku not in labels:
                labels[sku] = {}
            labels[sku][courier] = str(file)
    
    timestamp = datetime.strptime(latest_dir.name, '%Y-%m-%d_%H%M%S')
    return timestamp, labels


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


def count_labels_in_pdf(filepath):
    """Count pages in PDF (= number of labels)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        return len(reader.pages)
    except:
        return '?'


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

# Load labels
timestamp, labels = load_latest_labels()

if not labels:
    st.info("🔍 No labels available yet. Wait for orders to be processed.")
    st.stop()

# Show timestamp
time_str = timestamp.strftime('%d %b %Y, %I:%M %p')
st.markdown(f"<p style='text-align: center; color: #888;'>📅 {time_str}</p>", unsafe_allow_html=True)

st.markdown("---")

# Display labels organized by SKU
for sku, couriers in sorted(labels.items()):
    # SKU header with box
    st.markdown(f"""
    <div style='background: #f0f0f0; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h3 style='margin: 0; font-size: 1.5rem;'>🏷️ {sku}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Courier buttons
    cols = st.columns(len(couriers))
    
    for i, (courier, filepath) in enumerate(sorted(couriers.items())):
        with cols[i]:
            # Count labels
            label_count = count_labels_in_pdf(filepath)
            
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
            with open(filepath, 'rb') as f:
                st.download_button(
                    label=f"⬇️ Download",
                    data=f.read(),
                    file_name=Path(filepath).name,
                    mime="application/pdf",
                    key=f"dl_{sku}_{courier}",
                    use_container_width=True
                )
    
    st.markdown("<br>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9rem;'>
    <p>🚚 Pickup scheduled for tomorrow</p>
    <p>Built with ❤️ by JSK Labs</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
