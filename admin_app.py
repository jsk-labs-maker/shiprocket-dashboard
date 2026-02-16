"""
🎛️ JSK Labs Admin Dashboard - Premium Edition
==============================================
Complete control panel for Shiprocket operations

Built by Kluzo 😎 for JSK Labs
Version: 2.0 (Premium)
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import time
import uuid

# === PAGE CONFIG ===
st.set_page_config(
    page_title="🎛️ JSK Labs Admin",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CONSTANTS ===
GITHUB_REPO = "jsk-labs-maker/shiprocket-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/public"
SHIPROCKET_API_BASE = "https://apiv2.shiprocket.in/v1/external"

# === CUSTOM CSS ===
st.markdown("""
<style>
    /* Premium Dark Theme */
    .stApp {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
    /* Status Cards */
    .status-card {
        background: linear-gradient(135deg, #1e1e30 0%, #2a2a40 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .status-working {
        border-left: 4px solid #00ff88;
    }
    
    .status-idle {
        border-left: 4px solid #4a9eff;
    }
    
    .status-offline {
        border-left: 4px solid #ff4757;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #252540 100%);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #fff;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #8888aa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Task Board */
    .kanban-column {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 12px;
        min-height: 300px;
    }
    
    .task-card {
        background: linear-gradient(135deg, #252540 0%, #2a2a45 100%);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 3px solid #4a9eff;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .task-card:hover {
        transform: translateX(4px);
    }
    
    .task-high {
        border-left-color: #ff4757;
    }
    
    .task-medium {
        border-left-color: #ffa502;
    }
    
    .task-low {
        border-left-color: #2ed573;
    }
    
    /* Action Buttons */
    .action-btn {
        background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
        border: none;
        border-radius: 12px;
        padding: 16px 24px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        text-align: center;
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(74, 158, 255, 0.3);
    }
    
    /* Log Entry */
    .log-entry {
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 3px solid #4a9eff;
    }
    
    .log-success {
        border-left-color: #2ed573;
    }
    
    .log-error {
        border-left-color: #ff4757;
    }
    
    .log-warning {
        border-left-color: #ffa502;
    }
    
    /* Connection Status */
    .connection-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .dot-online {
        background: #2ed573;
        box-shadow: 0 0 12px #2ed573;
    }
    
    .dot-offline {
        background: #ff4757;
        box-shadow: 0 0 12px #ff4757;
    }
    
    .dot-checking {
        background: #ffa502;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Alert Banner */
    .alert-banner {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Note Card */
    .note-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #252540 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .note-ai {
        border-left: 3px solid #9b59b6;
    }
    
    .note-user {
        border-left: 3px solid #3498db;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Search Box */
    .search-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 12px 20px;
        width: 100%;
        color: white;
    }
    
    /* Schedule Card */
    .schedule-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #252540 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Deliverable Card */
    .deliverable-card {
        background: linear-gradient(135deg, #252540 0%, #2a2a45 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# DATA FETCHING FUNCTIONS
# =====================================================

@st.cache_data(ttl=10)
def fetch_ai_status():
    """Fetch AI status from GitHub."""
    try:
        url = f"{GITHUB_RAW_BASE}/ai/status.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"status": "offline", "message": "Cannot connect to status server"}


@st.cache_data(ttl=30)
def fetch_sub_agents():
    """Fetch sub-agents list."""
    try:
        url = f"{GITHUB_RAW_BASE}/ai/sub_agents.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("agents", [])
    except:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_tasks():
    """Fetch tasks from GitHub."""
    try:
        url = f"{GITHUB_RAW_BASE}/tasks/tasks.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"tasks": [], "columns": ["open", "in_progress", "done"]}


@st.cache_data(ttl=30)
def fetch_activity_logs():
    """Fetch activity logs."""
    try:
        url = f"{GITHUB_RAW_BASE}/logs/activity.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("logs", [])
    except:
        pass
    return []


@st.cache_data(ttl=60)
def fetch_batches_history():
    """Fetch batches history (legacy compatibility)."""
    try:
        url = f"{GITHUB_RAW_BASE}/batches_history.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("batches", [])
    except:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_notes():
    """Fetch notes."""
    try:
        url = f"{GITHUB_RAW_BASE}/notes/notes.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("notes", [])
    except:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_schedules():
    """Fetch scheduled actions."""
    try:
        url = f"{GITHUB_RAW_BASE}/schedules/schedules.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("schedules", [])
    except:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_deliverables():
    """Fetch deliverables index."""
    try:
        url = f"{GITHUB_RAW_BASE}/deliverables/index.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("deliverables", [])
    except:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_connection_status():
    """Fetch connection status."""
    try:
        url = f"{GITHUB_RAW_BASE}/connections/status.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"shiprocket": {"status": "unknown"}, "github": {"status": "unknown"}}


# =====================================================
# SHIPROCKET API FUNCTIONS
# =====================================================

def get_shiprocket_token():
    """Get Shiprocket auth token."""
    try:
        # Try Streamlit secrets
        if hasattr(st, 'secrets') and 'shiprocket' in st.secrets:
            api_key = st.secrets['shiprocket'].get('api_key')
            if api_key:
                return api_key
            
            email = st.secrets['shiprocket'].get('email')
            password = st.secrets['shiprocket'].get('password')
            
            if email and password:
                url = f"{SHIPROCKET_API_BASE}/auth/login"
                response = requests.post(url, json={"email": email, "password": password}, timeout=10)
                if response.status_code == 200:
                    return response.json().get("token")
    except:
        pass
    
    # Fallback to env
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
        
        api_key = os.getenv('SHIPROCKET_API_KEY')
        if api_key:
            return api_key
        
        email = os.getenv('SHIPROCKET_EMAIL')
        password = os.getenv('SHIPROCKET_PASSWORD')
        
        if email and password:
            url = f"{SHIPROCKET_API_BASE}/auth/login"
            response = requests.post(url, json={"email": email, "password": password}, timeout=10)
            if response.status_code == 200:
                return response.json().get("token")
    except:
        pass
    
    return None


def check_shiprocket_health(token):
    """Check Shiprocket API health and get wallet balance."""
    if not token:
        return {"status": "offline", "error": "No token"}
    
    try:
        start = time.time()
        url = f"{SHIPROCKET_API_BASE}/account/details/wallet-balance"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=10)
        elapsed = int((time.time() - start) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get("data", {}).get("balance_amount", 0)
            return {
                "status": "online",
                "response_time_ms": elapsed,
                "wallet_balance": float(balance) if balance else 0
            }
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "offline", "error": str(e)}


def get_new_orders_count(token):
    """Get count of NEW orders."""
    if not token:
        return 0
    
    try:
        url = f"{SHIPROCKET_API_BASE}/orders"
        headers = {"Authorization": f"Bearer {token}"}
        today = datetime.now()
        from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")
        
        params = {"filter": "new", "per_page": 200, "from": from_date, "to": to_date}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            orders = response.json().get("data", [])
            # Filter truly NEW orders
            new_count = 0
            for order in orders:
                if order.get("status") == "NEW":
                    shipments = order.get("shipments", [])
                    if not shipments or not shipments[0].get("awb_code"):
                        new_count += 1
            return new_count
    except:
        pass
    return 0


def get_shipment_id_by_awb(awb, token):
    """Get shipment ID from AWB number."""
    try:
        url = f"{SHIPROCKET_API_BASE}/courier/track/awb/{awb}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("tracking_data", {}).get("shipment_id")
    except:
        pass
    return None


def download_labels_by_shipment_ids(shipment_ids, token):
    """Download labels for shipment IDs."""
    try:
        url = f"{SHIPROCKET_API_BASE}/courier/generate/label"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        response = requests.post(url, headers=headers, json={"shipment_id": shipment_ids}, timeout=30)
        
        if response.status_code == 200:
            label_url = response.json().get("label_url")
            if label_url:
                label_response = requests.get(label_url, timeout=30)
                if label_response.status_code == 200:
                    return label_response.content
    except:
        pass
    return None


# =====================================================
# UI COMPONENTS
# =====================================================

def render_ai_status_card(status_data):
    """Render AI status card."""
    status = status_data.get("status", "offline")
    message = status_data.get("message", "")
    current_task = status_data.get("current_task")
    progress = status_data.get("progress", 0)
    
    status_colors = {
        "working": ("#00ff88", "🔄"),
        "idle": ("#4a9eff", "😎"),
        "processing": ("#ffa502", "⚡"),
        "offline": ("#ff4757", "💤"),
        "error": ("#ff4757", "❌"),
        "complete": ("#2ed573", "✅")
    }
    
    color, emoji = status_colors.get(status, ("#888", "❓"))
    
    st.markdown(f"""
    <div class="status-card status-{status}" style="border-left-color: {color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 2rem;">{emoji}</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: {color}; margin-left: 12px;">
                    {status.upper()}
                </span>
            </div>
            <div style="text-align: right;">
                <div style="color: #888; font-size: 0.85rem;">Kluzo AI</div>
            </div>
        </div>
        <div style="margin-top: 12px; color: #aaa;">{message}</div>
        {f'<div style="margin-top: 8px; color: #fff;"><strong>Current Task:</strong> {current_task}</div>' if current_task else ''}
    </div>
    """, unsafe_allow_html=True)
    
    if status in ["processing", "working"] and progress > 0:
        st.progress(progress / 100)


def render_metric_card(label, value, icon="📊", color="#4a9eff"):
    """Render a metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">{icon}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_task_card(task):
    """Render a task card."""
    priority_colors = {"high": "#ff4757", "medium": "#ffa502", "low": "#2ed573"}
    priority_class = f"task-{task.get('priority', 'low')}"
    
    return f"""
    <div class="task-card {priority_class}">
        <div style="font-weight: 600; color: #fff;">{task.get('title', 'Untitled')}</div>
        <div style="color: #888; font-size: 0.85rem; margin-top: 4px;">
            {task.get('description', '')[:50]}...
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 8px;">
            <span style="color: {priority_colors.get(task.get('priority', 'low'), '#888')}; font-size: 0.75rem; text-transform: uppercase;">
                {task.get('priority', 'low')}
            </span>
            <span style="color: #666; font-size: 0.75rem;">
                {task.get('created_at', '')[:10] if task.get('created_at') else ''}
            </span>
        </div>
    </div>
    """


def render_log_entry(log):
    """Render a log entry."""
    log_type = log.get("type", "info")
    type_class = {
        "success": "log-success",
        "error": "log-error",
        "warning": "log-warning"
    }.get(log_type, "")
    
    icon = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(log_type, "📝")
    
    return f"""
    <div class="log-entry {type_class}">
        <div style="display: flex; justify-content: space-between;">
            <span>{icon} <strong>{log.get('action', '')}</strong></span>
            <span style="color: #666; font-size: 0.85rem;">{log.get('timestamp', '')}</span>
        </div>
        <div style="color: #aaa; margin-top: 4px;">{log.get('message', '')}</div>
    </div>
    """


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3rem;">🎛️</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #fff;">JSK Labs</div>
        <div style="color: #888;">Admin Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        [
            "🤖 AI Status",
            "⚡ Quick Actions",
            "📋 Task Board",
            "📜 Activity Logs",
            "📝 Notes",
            "📦 Deliverables",
            "📥 Bulk AWB Download",
            "⏰ Scheduled Actions",
            "🔌 Connections",
            "🔍 Search"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    
    token = get_shiprocket_token()
    if token:
        health = check_shiprocket_health(token)
        if health.get("status") == "online":
            st.success(f"💰 ₹{health.get('wallet_balance', 0):,.2f}")
            new_orders = get_new_orders_count(token)
            st.info(f"📦 {new_orders} NEW orders")
        else:
            st.error("API Offline")
    else:
        st.warning("Not connected")
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh All", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("Built with ❤️ by Kluzo 😎")


# =====================================================
# MAIN CONTENT
# =====================================================

# Check for alerts
conn_status = fetch_connection_status()
shiprocket_status = conn_status.get("shiprocket", {}).get("status", "unknown")

if shiprocket_status == "offline":
    st.markdown("""
    <div class="alert-banner">
        <span style="font-size: 1.5rem; margin-right: 12px;">⚠️</span>
        <div>
            <strong>Connection Alert</strong><br>
            Shiprocket API is currently offline. Some features may not work.
        </div>
    </div>
    """, unsafe_allow_html=True)


# === PAGE: AI STATUS ===
if page == "🤖 AI Status":
    st.markdown('<div class="section-header">🤖 AI Status</div>', unsafe_allow_html=True)
    
    ai_status = fetch_ai_status()
    render_ai_status_card(ai_status)
    
    st.markdown("---")
    
    # Sub-agents
    st.markdown("### 🤖 Sub-Agents")
    
    sub_agents = fetch_sub_agents()
    
    if sub_agents:
        for agent in sub_agents:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{agent.get('name', 'Unknown')}**")
            with col2:
                status = agent.get('status', 'idle')
                color = "#2ed573" if status == "active" else "#888"
                st.markdown(f"<span style='color: {color};'>● {status}</span>", unsafe_allow_html=True)
            with col3:
                st.caption(agent.get('task', ''))
    else:
        st.info("No sub-agents active")
    
    st.markdown("---")
    
    # Activity Summary
    st.markdown("### 📊 Today's Activity")
    
    batches = fetch_batches_history()
    today = datetime.now().strftime('%Y-%m-%d')
    today_batches = [b for b in batches if b.get("date") == today]
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_shipped = sum(b.get("shipped", 0) for b in today_batches)
    total_failed = sum(b.get("unshipped", 0) for b in today_batches)
    
    with col1:
        render_metric_card("Batches", len(today_batches), "📦", "#4a9eff")
    with col2:
        render_metric_card("Shipped", total_shipped, "✅", "#2ed573")
    with col3:
        render_metric_card("Failed", total_failed, "❌", "#ff4757")
    with col4:
        rate = (total_shipped / (total_shipped + total_failed) * 100) if (total_shipped + total_failed) > 0 else 100
        render_metric_card("Success", f"{rate:.0f}%", "📈", "#ffa502")


# === PAGE: QUICK ACTIONS ===
elif page == "⚡ Quick Actions":
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 Ship Orders Now")
        st.markdown("Process all NEW orders with automatic courier assignment.")
        
        if st.button("🚀 Ship Orders Now", type="primary", use_container_width=True, key="ship_now"):
            with st.spinner("🔄 Processing..."):
                try:
                    from shiprocket_workflow import run_shipping_workflow
                    
                    progress = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🔐 Authenticating...")
                    progress.progress(20)
                    
                    status_text.text("📋 Fetching orders...")
                    progress.progress(40)
                    
                    result = run_shipping_workflow()
                    
                    status_text.text("✅ Complete!")
                    progress.progress(100)
                    
                    time.sleep(0.5)
                    status_text.empty()
                    progress.empty()
                    
                    # Show results
                    st.markdown("### 📊 Results")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total", result.get("total_orders", 0))
                    c2.metric("Shipped", result.get("shipped", 0))
                    c3.metric("Failed", result.get("failed", 0))
                    c4.metric("Skipped", result.get("skipped", 0))
                    
                    if result.get("shipped", 0) > 0:
                        st.success(f"✅ Successfully shipped {result['shipped']} orders!")
                    else:
                        st.warning("No orders were shipped")
                        if result.get("errors"):
                            with st.expander("Error Details"):
                                for err in result["errors"]:
                                    st.error(err)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### 📄 Download Latest Labels")
        st.markdown("Download the most recent batch of labels.")
        
        batches = fetch_batches_history()
        
        if batches:
            latest = batches[0]
            zip_file = latest.get("zip_file", "")
            
            st.info(f"📦 Latest: {latest.get('date')} {latest.get('time')}")
            st.caption(f"Shipped: {latest.get('shipped', 0)} | SKUs: {latest.get('sku_count', 0)}")
            
            if zip_file:
                zip_url = f"https://github.com/{GITHUB_REPO}/raw/{GITHUB_BRANCH}/{zip_file}"
                st.markdown(f"[📥 Download ZIP]({zip_url})", unsafe_allow_html=True)
            else:
                st.warning("No ZIP file available")
        else:
            st.info("No batches available yet")
    
    st.markdown("---")
    
    # Additional quick actions
    st.markdown("### 🛠️ More Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Check API Status", use_container_width=True):
            token = get_shiprocket_token()
            if token:
                health = check_shiprocket_health(token)
                if health.get("status") == "online":
                    st.success(f"✅ API Online ({health.get('response_time_ms')}ms)")
                    st.info(f"💰 Balance: ₹{health.get('wallet_balance', 0):,.2f}")
                else:
                    st.error(f"❌ API Error: {health.get('error', 'Unknown')}")
            else:
                st.error("❌ No credentials configured")
    
    with col2:
        if st.button("📊 View Order Stats", use_container_width=True):
            token = get_shiprocket_token()
            if token:
                new_orders = get_new_orders_count(token)
                st.info(f"📦 NEW orders ready to ship: {new_orders}")
            else:
                st.error("❌ No credentials configured")
    
    with col3:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
            st.rerun()


# === PAGE: TASK BOARD ===
elif page == "📋 Task Board":
    st.markdown('<div class="section-header">📋 Task Board</div>', unsafe_allow_html=True)
    
    tasks_data = fetch_tasks()
    tasks = tasks_data.get("tasks", [])
    
    # Add new task
    with st.expander("➕ Add New Task"):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_title = st.text_input("Task Title", placeholder="Enter task title...")
            new_desc = st.text_area("Description", placeholder="Task description...", height=100)
        with col2:
            new_priority = st.selectbox("Priority", ["low", "medium", "high"])
            new_status = st.selectbox("Status", ["open", "in_progress", "done"])
        
        if st.button("➕ Add Task", type="primary"):
            st.info("💡 Task creation requires GitHub API. Coming soon!")
    
    st.markdown("---")
    
    # Kanban Board
    col1, col2, col3 = st.columns(3)
    
    open_tasks = [t for t in tasks if t.get("status") == "open"]
    in_progress_tasks = [t for t in tasks if t.get("status") == "in_progress"]
    done_tasks = [t for t in tasks if t.get("status") == "done"]
    
    with col1:
        st.markdown("### 📬 Open")
        st.markdown(f'<div class="kanban-column">', unsafe_allow_html=True)
        if open_tasks:
            for task in open_tasks:
                st.markdown(render_task_card(task), unsafe_allow_html=True)
        else:
            st.caption("No open tasks")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔄 In Progress")
        st.markdown(f'<div class="kanban-column">', unsafe_allow_html=True)
        if in_progress_tasks:
            for task in in_progress_tasks:
                st.markdown(render_task_card(task), unsafe_allow_html=True)
        else:
            st.caption("No tasks in progress")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("### ✅ Done")
        st.markdown(f'<div class="kanban-column">', unsafe_allow_html=True)
        if done_tasks:
            for task in done_tasks[:5]:  # Show last 5
                st.markdown(render_task_card(task), unsafe_allow_html=True)
        else:
            st.caption("No completed tasks")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("💡 Drag-and-drop coming in next update!")


# === PAGE: ACTIVITY LOGS ===
elif page == "📜 Activity Logs":
    st.markdown('<div class="section-header">📜 Activity Logs</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search logs", placeholder="Search...")
    with col2:
        log_type_filter = st.selectbox("Type", ["All", "Success", "Error", "Warning", "Info"])
    with col3:
        date_filter = st.date_input("Date", value=datetime.now())
    
    st.markdown("---")
    
    # Get logs (combine activity logs with batch history)
    activity_logs = fetch_activity_logs()
    batches = fetch_batches_history()
    
    # Convert batches to log format
    all_logs = []
    
    for batch in batches:
        shipped = batch.get("shipped", 0)
        failed = batch.get("unshipped", 0)
        log_type = "success" if failed == 0 else ("warning" if shipped > 0 else "error")
        
        all_logs.append({
            "timestamp": f"{batch.get('date', '')} {batch.get('time', '')}",
            "action": "Batch Processed",
            "message": f"Shipped: {shipped}, Failed: {failed}, SKUs: {batch.get('sku_count', 0)}",
            "type": log_type
        })
    
    all_logs.extend(activity_logs)
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Filter logs
    if search_query:
        all_logs = [l for l in all_logs if search_query.lower() in str(l).lower()]
    
    if log_type_filter != "All":
        all_logs = [l for l in all_logs if l.get("type", "info") == log_type_filter.lower()]
    
    # Display logs
    if all_logs:
        for log in all_logs[:50]:  # Show last 50
            st.markdown(render_log_entry(log), unsafe_allow_html=True)
        
        # Export options
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export CSV"):
                df = pd.DataFrame(all_logs)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"logs_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    "text/csv"
                )
        with col2:
            st.button("📥 Export PDF", disabled=True)
            st.caption("Coming soon")
    else:
        st.info("No logs found")


# === PAGE: NOTES ===
elif page == "📝 Notes":
    st.markdown('<div class="section-header">📝 Notes Panel</div>', unsafe_allow_html=True)
    
    # Add new note
    with st.expander("➕ Add New Note", expanded=True):
        note_content = st.text_area("Note", placeholder="Write your note here...", height=150)
        note_type = st.radio("Type", ["User Note", "AI Response"], horizontal=True)
        
        if st.button("💾 Save Note", type="primary"):
            st.info("💡 Note saving requires GitHub API. Coming soon!")
    
    st.markdown("---")
    
    # Display notes
    notes = fetch_notes()
    
    if notes:
        for note in notes:
            note_class = "note-ai" if note.get("type") == "ai" else "note-user"
            icon = "🤖" if note.get("type") == "ai" else "📝"
            
            st.markdown(f"""
            <div class="note-card {note_class}">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>{icon} <strong>{note.get('type', 'user').title()} Note</strong></span>
                    <span style="color: #666; font-size: 0.85rem;">{note.get('timestamp', '')}</span>
                </div>
                <div style="color: #ddd;">{note.get('content', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No notes yet. Add your first note above!")


# === PAGE: DELIVERABLES ===
elif page == "📦 Deliverables":
    st.markdown('<div class="section-header">📦 Deliverables</div>', unsafe_allow_html=True)
    
    # Quick download
    st.markdown("### 📥 Quick Download")
    
    batches = fetch_batches_history()
    
    if batches:
        # Group by date
        dates = sorted(set(b.get("date", "") for b in batches), reverse=True)
        
        selected_date = st.selectbox("Select Date", dates)
        
        date_batches = [b for b in batches if b.get("date") == selected_date]
        
        st.markdown("---")
        
        for batch in date_batches:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**🕐 {batch.get('time', '')}**")
                st.caption(f"Shipped: {batch.get('shipped', 0)} | Failed: {batch.get('unshipped', 0)}")
            
            with col2:
                skus = batch.get("skus", [])
                if skus:
                    st.caption(f"SKUs: {', '.join(skus[:3])}{'...' if len(skus) > 3 else ''}")
            
            with col3:
                zip_file = batch.get("zip_file", "")
                if zip_file:
                    zip_url = f"https://github.com/{GITHUB_REPO}/raw/{GITHUB_BRANCH}/{zip_file}"
                    st.markdown(f"[📥 ZIP]({zip_url})")
            
            st.markdown("---")
    else:
        st.info("No deliverables available yet")
    
    # XLSM Report (placeholder)
    st.markdown("### 📊 Reports")
    st.info("📊 XLSM report generation coming soon!")


# === PAGE: BULK AWB DOWNLOAD ===
elif page == "📥 Bulk AWB Download":
    st.markdown('<div class="section-header">📥 Bulk AWB Download</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Download labels for any AWB numbers. Paste one AWB per line.
    """)
    
    awb_input = st.text_area(
        "AWB Numbers",
        height=200,
        placeholder="284931134807362\n284931134821395\n284931134821922\n...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        download_btn = st.button("📥 Download Labels", type="primary", use_container_width=True)
    
    with col2:
        st.caption("💡 Works for ANY order, not just batches from this system")
    
    if download_btn:
        if not awb_input.strip():
            st.error("Please enter at least one AWB number")
        else:
            awb_list = [line.strip() for line in awb_input.strip().split('\n') if line.strip()]
            
            st.info(f"🔍 Processing {len(awb_list)} AWB numbers...")
            
            token = get_shiprocket_token()
            
            if not token:
                st.error("❌ Authentication failed. Configure credentials in Streamlit Secrets.")
            else:
                progress = st.progress(0)
                status = st.empty()
                
                found = []
                not_found = []
                shipment_ids = []
                
                for i, awb in enumerate(awb_list):
                    status.text(f"🔍 Checking {awb}...")
                    progress.progress((i + 1) / len(awb_list))
                    
                    sid = get_shipment_id_by_awb(awb, token)
                    if sid:
                        found.append(awb)
                        shipment_ids.append(sid)
                    else:
                        not_found.append(awb)
                
                status.empty()
                progress.empty()
                
                # Show results
                st.markdown("### 📋 Results")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ Found: {len(found)}")
                with col2:
                    if not_found:
                        st.warning(f"⚠️ Not found: {len(not_found)}")
                
                if not_found:
                    with st.expander("Show not found AWBs"):
                        for awb in not_found:
                            st.text(f"❌ {awb}")
                
                # Download labels
                if shipment_ids:
                    status.text("📥 Downloading labels...")
                    
                    pdf_data = download_labels_by_shipment_ids(shipment_ids, token)
                    
                    status.empty()
                    
                    if pdf_data:
                        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                        
                        st.download_button(
                            f"📥 Download All Labels ({len(found)} labels)",
                            pdf_data,
                            f"labels_{timestamp}.pdf",
                            "application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Failed to generate labels PDF")
                else:
                    st.error("❌ No valid AWBs found")


# === PAGE: SCHEDULED ACTIONS ===
elif page == "⏰ Scheduled Actions":
    st.markdown('<div class="section-header">⏰ Scheduled Actions</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Schedule automatic shipping runs. The system will process orders at the specified times.
    """)
    
    # Add new schedule
    with st.expander("➕ Add Schedule"):
        col1, col2 = st.columns(2)
        with col1:
            schedule_name = st.text_input("Schedule Name", placeholder="Morning Batch")
            schedule_time = st.time_input("Time", value=datetime.now().replace(hour=9, minute=0))
        with col2:
            schedule_days = st.multiselect(
                "Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            )
            schedule_action = st.selectbox("Action", ["Ship All Orders", "Download Labels Only"])
        
        if st.button("➕ Add Schedule", type="primary"):
            st.info("💡 Schedule saving requires GitHub API. Coming soon!")
    
    st.markdown("---")
    
    # Display schedules
    schedules = fetch_schedules()
    
    if schedules:
        for sched in schedules:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{sched.get('name', 'Unnamed')}**")
                st.caption(f"{sched.get('time', '')} | {', '.join(sched.get('days', []))}")
            
            with col2:
                st.caption(sched.get('action', ''))
            
            with col3:
                enabled = sched.get('enabled', True)
                st.toggle("Enabled", value=enabled, key=f"sched_{sched.get('id', '')}")
    else:
        st.info("No schedules configured")
        
        # Default schedule suggestions
        st.markdown("### 💡 Suggested Schedules")
        
        suggestions = [
            ("Morning Batch", "09:00 AM", "Process early orders"),
            ("Afternoon Batch", "02:00 PM", "Mid-day processing"),
            ("Evening Batch", "06:00 PM", "End of day processing")
        ]
        
        for name, time, desc in suggestions:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{name}** - {time}")
                st.caption(desc)
            with col2:
                st.button(f"Add", key=f"add_{name}", disabled=True)


# === PAGE: CONNECTIONS ===
elif page == "🔌 Connections":
    st.markdown('<div class="section-header">🔌 Connection Status</div>', unsafe_allow_html=True)
    
    # Real-time check
    if st.button("🔄 Check All Connections", type="primary"):
        st.cache_data.clear()
    
    st.markdown("---")
    
    # Shiprocket Status
    st.markdown("### 🚀 Shiprocket API")
    
    token = get_shiprocket_token()
    
    if token:
        health = check_shiprocket_health(token)
        
        if health.get("status") == "online":
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="connection-dot dot-online"></span>
                <span style="color: #2ed573; font-weight: 600;">ONLINE</span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Response Time", f"{health.get('response_time_ms', 0)}ms")
            col2.metric("Wallet Balance", f"₹{health.get('wallet_balance', 0):,.2f}")
            col3.metric("Status", "Healthy")
        else:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="connection-dot dot-offline"></span>
                <span style="color: #ff4757; font-weight: 600;">OFFLINE</span>
            </div>
            """, unsafe_allow_html=True)
            st.error(f"Error: {health.get('error', 'Unknown')}")
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="connection-dot dot-offline"></span>
            <span style="color: #888; font-weight: 600;">NOT CONFIGURED</span>
        </div>
        """, unsafe_allow_html=True)
        st.warning("No credentials configured. Add them in Streamlit Secrets.")
    
    st.markdown("---")
    
    # GitHub Status
    st.markdown("### 📦 GitHub Storage")
    
    try:
        start = time.time()
        response = requests.get(f"{GITHUB_RAW_BASE}/ai/status.json", timeout=5)
        elapsed = int((time.time() - start) * 1000)
        
        if response.status_code == 200:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="connection-dot dot-online"></span>
                <span style="color: #2ed573; font-weight: 600;">ONLINE</span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            col1.metric("Response Time", f"{elapsed}ms")
            col2.metric("Repository", GITHUB_REPO)
        else:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="connection-dot dot-offline"></span>
                <span style="color: #ff4757; font-weight: 600;">ERROR</span>
            </div>
            """, unsafe_allow_html=True)
            st.error(f"HTTP {response.status_code}")
    except Exception as e:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="connection-dot dot-offline"></span>
            <span style="color: #ff4757; font-weight: 600;">OFFLINE</span>
        </div>
        """, unsafe_allow_html=True)
        st.error(str(e))


# === PAGE: SEARCH ===
elif page == "🔍 Search":
    st.markdown('<div class="section-header">🔍 Global Search</div>', unsafe_allow_html=True)
    
    search_query = st.text_input(
        "Search",
        placeholder="Search tasks, logs, notes, deliverables...",
        label_visibility="collapsed"
    )
    
    search_types = st.multiselect(
        "Search in",
        ["Tasks", "Logs", "Notes", "Deliverables"],
        default=["Tasks", "Logs", "Notes", "Deliverables"]
    )
    
    if search_query:
        st.markdown("---")
        st.markdown(f"### 🔍 Results for '{search_query}'")
        
        results_found = False
        
        # Search tasks
        if "Tasks" in search_types:
            tasks = fetch_tasks().get("tasks", [])
            matching_tasks = [t for t in tasks if search_query.lower() in str(t).lower()]
            
            if matching_tasks:
                results_found = True
                st.markdown("#### 📋 Tasks")
                for task in matching_tasks[:5]:
                    st.markdown(render_task_card(task), unsafe_allow_html=True)
        
        # Search logs
        if "Logs" in search_types:
            batches = fetch_batches_history()
            matching_logs = [b for b in batches if search_query.lower() in str(b).lower()]
            
            if matching_logs:
                results_found = True
                st.markdown("#### 📜 Logs")
                for log in matching_logs[:5]:
                    st.markdown(f"- {log.get('date')} {log.get('time')}: Shipped {log.get('shipped', 0)}")
        
        # Search notes
        if "Notes" in search_types:
            notes = fetch_notes()
            matching_notes = [n for n in notes if search_query.lower() in str(n).lower()]
            
            if matching_notes:
                results_found = True
                st.markdown("#### 📝 Notes")
                for note in matching_notes[:5]:
                    st.markdown(f"- {note.get('content', '')[:100]}...")
        
        # Search deliverables
        if "Deliverables" in search_types:
            batches = fetch_batches_history()
            matching_deliverables = []
            
            for batch in batches:
                skus = batch.get("skus", [])
                if any(search_query.lower() in sku.lower() for sku in skus):
                    matching_deliverables.append(batch)
            
            if matching_deliverables:
                results_found = True
                st.markdown("#### 📦 Deliverables")
                for d in matching_deliverables[:5]:
                    st.markdown(f"- {d.get('date')} {d.get('time')}: {', '.join(d.get('skus', []))}")
        
        if not results_found:
            st.info("No results found")
    else:
        st.info("Enter a search query to find tasks, logs, notes, and deliverables")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <div>🎛️ JSK Labs Admin Dashboard v2.0</div>
    <div style="font-size: 0.85rem; margin-top: 8px;">Built with ❤️ by Kluzo 😎</div>
</div>
""", unsafe_allow_html=True)
