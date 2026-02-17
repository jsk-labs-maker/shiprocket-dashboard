"""
📥 Bulk AWB Download - JSK Labs Dashboard
Download labels for any AWB numbers directly from Shiprocket
"""

import streamlit as st
import requests
from datetime import datetime
import os

st.set_page_config(
    page_title="Bulk Download | Kluzo",
    page_icon="📥",
    layout="wide"
)

# === CONSTANTS ===
SHIPROCKET_API = "https://apiv2.shiprocket.in/v1/external"

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

.download-card {
    background: rgba(22, 27, 34, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}
.download-title {
    color: #58a6ff;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.download-desc {
    color: #8b949e;
    font-size: 0.9rem;
    margin-bottom: 20px;
}
.result-card {
    background: rgba(13, 17, 23, 0.8);
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.result-card.success {
    border-left: 3px solid #3fb950;
}
.result-card.error {
    border-left: 3px solid #f85149;
}
.awb-text {
    color: #e6edf3;
    font-family: monospace;
    font-size: 0.9rem;
}
.status-badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}
.status-badge.success {
    background: rgba(63, 185, 80, 0.15);
    color: #3fb950;
}
.status-badge.error {
    background: rgba(248, 81, 73, 0.15);
    color: #f85149;
}
.stats-row {
    display: flex;
    gap: 20px;
    margin: 20px 0;
}
.stat-box {
    background: rgba(22, 27, 34, 0.6);
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px 24px;
    text-align: center;
    flex: 1;
}
.stat-value {
    font-size: 2rem;
    font-weight: 700;
}
.stat-value.green { color: #3fb950; }
.stat-value.red { color: #f85149; }
.stat-value.blue { color: #58a6ff; }
.stat-label {
    color: #8b949e;
    font-size: 0.8rem;
    margin-top: 4px;
}
.instructions {
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 20px;
}
.instructions-title {
    color: #58a6ff;
    font-weight: 600;
    margin-bottom: 8px;
}
.instructions-text {
    color: #8b949e;
    font-size: 0.85rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# === FUNCTIONS ===
@st.cache_data(ttl=600)
def get_auth_token():
    """Get Shiprocket auth token"""
    try:
        # Try environment file first
        from dotenv import load_dotenv
        load_dotenv("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
        email = os.getenv('SHIPROCKET_EMAIL')
        password = os.getenv('SHIPROCKET_PASSWORD')
        
        if not email or not password:
            # Try Streamlit secrets
            email = st.secrets.get("SHIPROCKET_EMAIL")
            password = st.secrets.get("SHIPROCKET_PASSWORD")
        
        if email and password:
            r = requests.post(
                f"{SHIPROCKET_API}/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            if r.ok:
                return r.json().get("token")
    except Exception as e:
        st.error(f"Auth error: {e}")
    return None

def track_awb(token, awb):
    """Track AWB and get shipment details"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(
            f"{SHIPROCKET_API}/courier/track/awb/{awb}",
            headers=headers,
            timeout=15
        )
        if r.ok:
            data = r.json()
            # Extract shipment_id from tracking data
            tracking = data.get("tracking_data", {})
            shipment_id = tracking.get("shipment_id")
            if shipment_id:
                return {"success": True, "shipment_id": shipment_id, "data": tracking}
            # Try alternate path
            if "shipment_track" in data:
                for track in data.get("shipment_track", []):
                    if track.get("awb_code") == awb:
                        return {"success": True, "shipment_id": track.get("shipment_id"), "data": track}
        return {"success": False, "error": "Shipment not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def download_labels(token, shipment_ids):
    """Download labels for given shipment IDs"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(
            f"{SHIPROCKET_API}/courier/generate/label",
            headers=headers,
            json={"shipment_id": shipment_ids},
            timeout=30
        )
        if r.ok:
            data = r.json()
            label_url = data.get("label_url")
            if label_url:
                # Download the actual PDF
                pdf_r = requests.get(label_url, timeout=30)
                if pdf_r.ok:
                    return {"success": True, "pdf": pdf_r.content, "url": label_url}
            return {"success": False, "error": "No label URL returned"}
        return {"success": False, "error": f"API error: {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# === HEADER ===
st.markdown("# 📥 Bulk AWB Download")
st.caption("Download shipping labels for any AWB numbers directly from Shiprocket")

# === INSTRUCTIONS ===
st.markdown("""
<div class="instructions">
    <div class="instructions-title">📋 How to use</div>
    <div class="instructions-text">
        1. Paste your AWB numbers below (one per line)<br>
        2. Click "Download Labels"<br>
        3. Wait for processing (may take a few seconds per AWB)<br>
        4. Download the combined PDF with all labels
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# === MAIN INPUT ===
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown('<div class="download-card">', unsafe_allow_html=True)
    st.markdown('<div class="download-title">📝 Enter AWB Numbers</div>', unsafe_allow_html=True)
    st.markdown('<div class="download-desc">Paste AWB numbers, one per line. Supports up to 100 AWBs at once.</div>', unsafe_allow_html=True)
    
    awb_input = st.text_area(
        "AWB Numbers",
        placeholder="284931134807362\n284931134807363\n284931134807364",
        height=200,
        label_visibility="collapsed"
    )
    
    # Parse AWBs
    awb_list = [awb.strip() for awb in awb_input.split("\n") if awb.strip()]
    
    if awb_list:
        st.caption(f"📦 {len(awb_list)} AWB(s) detected")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download button
    download_btn = st.button("🚀 Download Labels", type="primary", use_container_width=True, disabled=len(awb_list) == 0)

with col2:
    st.markdown('<div class="download-card">', unsafe_allow_html=True)
    st.markdown('<div class="download-title">ℹ️ Quick Info</div>', unsafe_allow_html=True)
    
    # Check API connection
    token = get_auth_token()
    if token:
        st.success("🟢 Connected to Shiprocket")
    else:
        st.error("🔴 Not connected")
        st.caption("Check credentials in settings")
    
    st.markdown("---")
    
    st.markdown("**Supported formats:**")
    st.code("284931134807362\nSR123456789\nDL987654321", language=None)
    
    st.markdown("**Tips:**")
    st.markdown("""
    - Copy AWBs from Excel/Sheets
    - Works with any courier
    - Labels combine into one PDF
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# === PROCESSING ===
if download_btn and awb_list:
    if not token:
        st.error("❌ Not authenticated. Please check API credentials.")
    else:
        st.markdown("---")
        st.markdown("### 🔄 Processing...")
        
        results = []
        shipment_ids = []
        
        # Progress bar
        progress = st.progress(0)
        status_text = st.empty()
        
        for i, awb in enumerate(awb_list):
            status_text.text(f"Tracking AWB: {awb} ({i+1}/{len(awb_list)})")
            progress.progress((i + 1) / len(awb_list))
            
            result = track_awb(token, awb)
            result["awb"] = awb
            results.append(result)
            
            if result["success"]:
                shipment_ids.append(result["shipment_id"])
        
        progress.empty()
        status_text.empty()
        
        # === RESULTS ===
        success_count = sum(1 for r in results if r["success"])
        error_count = len(results) - success_count
        
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-value blue">{len(awb_list)}</div>
                <div class="stat-label">Total AWBs</div>
            </div>
            <div class="stat-box">
                <div class="stat-value green">{success_count}</div>
                <div class="stat-label">Found</div>
            </div>
            <div class="stat-box">
                <div class="stat-value red">{error_count}</div>
                <div class="stat-label">Not Found</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show results
        with st.expander(f"📋 Results ({success_count} found, {error_count} not found)", expanded=True):
            for r in results:
                if r["success"]:
                    st.markdown(f"""
                    <div class="result-card success">
                        <span class="awb-text">✅ {r['awb']}</span>
                        <span class="status-badge success">Shipment #{r['shipment_id']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card error">
                        <span class="awb-text">❌ {r['awb']}</span>
                        <span class="status-badge error">{r.get('error', 'Not found')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # === DOWNLOAD LABELS ===
        if shipment_ids:
            st.markdown("---")
            st.markdown("### 📄 Download Labels")
            
            with st.spinner("Generating combined PDF..."):
                label_result = download_labels(token, shipment_ids)
            
            if label_result["success"]:
                st.success(f"✅ Labels ready! ({len(shipment_ids)} labels combined)")
                
                # Download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"labels_bulk_{timestamp}.pdf"
                
                st.download_button(
                    label="📥 Download Combined PDF",
                    data=label_result["pdf"],
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                # Also show direct link
                st.caption(f"Or open directly: [Label URL]({label_result['url']})")
            else:
                st.error(f"❌ Failed to generate labels: {label_result.get('error')}")
                
                # Try individual downloads
                st.warning("Trying individual label downloads...")
                for sid in shipment_ids[:5]:  # Limit to 5 for safety
                    single_result = download_labels(token, [sid])
                    if single_result["success"]:
                        st.download_button(
                            label=f"📄 Label #{sid}",
                            data=single_result["pdf"],
                            file_name=f"label_{sid}.pdf",
                            mime="application/pdf"
                        )
        else:
            st.warning("⚠️ No valid shipments found. Cannot generate labels.")

# === RECENT DOWNLOADS ===
st.markdown("---")
st.markdown("### 📜 Quick Tips")

tip1, tip2, tip3 = st.columns(3)

with tip1:
    st.info("**From Telegram**\n\nJust message me:\n`Download labels: AWB1, AWB2, AWB3`\n\nI'll send the PDFs directly! 📲")

with tip2:
    st.info("**Batch History**\n\nLabels from 'Ship them buddy' are saved in the Dashboard under Processing History. 📋")

with tip3:
    st.info("**Troubleshooting**\n\n• AWB not found? Check if it's shipped\n• Invalid format? Remove spaces\n• API error? Refresh token in Settings ⚙️")

# === FOOTER ===
st.markdown("---")
st.caption(f"📥 Bulk Download • Last updated: {datetime.now().strftime('%I:%M %p')} • Built by Kluzo 😎")
