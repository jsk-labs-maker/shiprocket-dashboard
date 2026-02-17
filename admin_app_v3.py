"""
🎛️ JSK Labs Admin Dashboard - Claude Style v3.0
================================================
Inspired by Claude AI Agent Dashboard design

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Kluzo | Dashboard",
    page_icon="😎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === CONSTANTS ===
GITHUB_REPO = "jsk-labs-maker/shiprocket-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/public"
SHIPROCKET_API_BASE = "https://apiv2.shiprocket.in/v1/external"

# === CLAUDE-STYLE CSS ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Dark Theme */
    .stApp {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    }
    
    /* Hide defaults */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    
    /* Header */
    .header-container {
        background: #161b22;
        border-bottom: 1px solid #30363d;
        padding: 12px 24px;
        margin: -1rem -1rem 1rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .header-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e6edf3;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .online-dot {
        width: 10px;
        height: 10px;
        background: #3fb950;
        border-radius: 50%;
        box-shadow: 0 0 8px #3fb950;
    }
    
    .tab-nav {
        display: flex;
        gap: 4px;
    }
    
    .tab-btn {
        padding: 8px 16px;
        background: transparent;
        color: #8b949e;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
    }
    
    .tab-btn.active {
        background: #21262d;
        color: #e6edf3;
    }
    
    .header-right {
        display: flex;
        align-items: center;
        gap: 16px;
        color: #8b949e;
        font-size: 0.85rem;
    }
    
    /* Profile Card */
    .profile-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }
    
    .avatar-wrapper {
        position: relative;
        display: inline-block;
        margin-bottom: 16px;
    }
    
    .avatar-circle {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #ffd93d 0%, #ff9500 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        margin: 0 auto;
    }
    
    .avatar-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        font-size: 20px;
    }
    
    .profile-name {
        font-size: 1.25rem;
        font-weight: 600;
        color: #e6edf3;
        margin: 12px 0 8px 0;
    }
    
    .profile-status {
        color: #8b949e;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .status-dot-small {
        width: 8px;
        height: 8px;
        background: #3fb950;
        border-radius: 50%;
    }
    
    /* Stats Card */
    .stat-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        margin-top: 12px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #3fb950;
    }
    
    .stat-value.blue { color: #58a6ff; }
    .stat-value.orange { color: #f0883e; }
    
    .stat-label {
        color: #6e7681;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    
    /* Kanban */
    .kanban-col {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        min-height: 400px;
    }
    
    .kanban-header {
        font-size: 0.75rem;
        font-weight: 600;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding-bottom: 12px;
        border-bottom: 1px solid #30363d;
        margin-bottom: 12px;
    }
    
    .task-item {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    
    .task-item:hover {
        border-color: #58a6ff;
        background: #161b22;
    }
    
    .task-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-top: 5px;
        flex-shrink: 0;
    }
    
    .task-dot.green { background: #3fb950; }
    .task-dot.orange { background: #f0883e; }
    .task-dot.blue { background: #58a6ff; }
    .task-dot.gray { background: #6e7681; }
    
    .task-text {
        color: #e6edf3;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    .task-meta {
        color: #6e7681;
        font-size: 0.75rem;
        margin-top: 4px;
    }
    
    .archive-btn {
        background: #238636;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 0.8rem;
        cursor: pointer;
        width: 100%;
        margin-top: 12px;
    }
    
    /* Bottom Sections */
    .section-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
    }
    
    .section-title {
        color: #8b949e;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .schedule-item {
        background: #0d1117;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .schedule-name {
        color: #e6edf3;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .schedule-meta {
        color: #6e7681;
        font-size: 0.75rem;
    }
    
    .schedule-badge {
        background: #238636;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
    }
    
    .schedule-badge.disabled {
        background: #6e7681;
    }
    
    .note-item {
        background: #0d1117;
        border-left: 3px solid #58a6ff;
        border-radius: 0 8px 8px 0;
        padding: 12px;
        margin-bottom: 8px;
    }
    
    .note-item.ai {
        border-left-color: #a855f7;
    }
    
    .note-text {
        color: #e6edf3;
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    .note-time {
        color: #6e7681;
        font-size: 0.75rem;
        margin-top: 6px;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: #6e7681;
        font-size: 0.8rem;
        padding: 24px 0;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# DATA FUNCTIONS
# =====================================================

@st.cache_data(ttl=30)
def fetch_ai_status():
    try:
        url = f"{GITHUB_RAW_BASE}/ai/status.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"status": "idle", "message": "Ready for tasks"}


@st.cache_data(ttl=30)
def fetch_tasks():
    try:
        url = f"{GITHUB_RAW_BASE}/tasks/tasks.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"tasks": []}


@st.cache_data(ttl=60)
def fetch_batches():
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
    try:
        url = f"{GITHUB_RAW_BASE}/schedules/schedules.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("schedules", [])
    except:
        pass
    return []


def get_shiprocket_token():
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
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


def get_wallet_balance(token):
    if not token:
        return 0
    try:
        url = f"{SHIPROCKET_API_BASE}/account/details/wallet-balance"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return float(response.json().get("data", {}).get("balance_amount", 0))
    except:
        pass
    return 0


def get_new_orders_count(token):
    if not token:
        return 0
    try:
        url = f"{SHIPROCKET_API_BASE}/orders"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"filter": "new", "per_page": 200}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            orders = response.json().get("data", [])
            return sum(1 for o in orders if o.get("status") == "NEW")
    except:
        pass
    return 0


# =====================================================
# MAIN UI
# =====================================================

# Fetch data
ai_status = fetch_ai_status()
tasks_data = fetch_tasks()
tasks = tasks_data.get("tasks", [])
batches = fetch_batches()
notes = fetch_notes()
schedules = fetch_schedules()

token = get_shiprocket_token()
wallet = get_wallet_balance(token) if token else 0
new_orders = get_new_orders_count(token) if token else 0
last_sync = datetime.now().strftime("%I:%M:%S %p")

# === HEADER ===
st.markdown(f"""
<div class="header-container">
    <div class="header-left">
        <div class="header-title">
            Kluzo <span class="online-dot"></span>
        </div>
        <div class="tab-nav">
            <button class="tab-btn active">Dashboard</button>
            <button class="tab-btn">Docs</button>
            <button class="tab-btn">Log</button>
        </div>
    </div>
    <div class="header-right">
        <span>Last sync: {last_sync}</span>
        <span>😎</span>
        <span>logout</span>
        <span>☐ Expand</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === MAIN LAYOUT ===
col_sidebar, col_main = st.columns([1, 4])

with col_sidebar:
    # Profile Card
    status_emoji = "😎" if ai_status.get("status") == "idle" else "🔄"
    st.markdown(f"""
    <div class="profile-card">
        <div class="avatar-wrapper">
            <div class="avatar-circle">😎</div>
            <span class="avatar-badge">✨</span>
        </div>
        <div class="profile-name">Kluzo</div>
        <div class="profile-status">
            <span class="status-dot-small"></span>
            {status_emoji} {ai_status.get("status", "idle").capitalize()}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ready button
    if st.button("🚀 Ready for tasks", use_container_width=True, type="primary"):
        st.toast("Ready to work! 😎")
    
    # Stats
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">₹{wallet:,.0f}</div>
        <div class="stat-label">Wallet Balance</div>
    </div>
    <div class="stat-card">
        <div class="stat-value blue">{new_orders}</div>
        <div class="stat-label">NEW Orders</div>
    </div>
    <div class="stat-card">
        <div class="stat-value orange">{len(batches)}</div>
        <div class="stat-label">Total Batches</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_main:
    # === KANBAN BOARD ===
    k1, k2, k3, k4 = st.columns(4)
    
    # Separate tasks
    todo = [t for t in tasks if t.get("status") == "open"]
    doing = [t for t in tasks if t.get("status") == "in_progress"]
    done = [t for t in tasks if t.get("status") == "done"]
    
    with k1:
        st.markdown(f'<div class="kanban-header">● TO DO <span style="opacity:0.5">({len(todo)})</span></div>', unsafe_allow_html=True)
        for t in todo:
            st.markdown(f"""
            <div class="task-item">
                <span class="task-dot orange"></span>
                <div>
                    <div class="task-text">{t.get('title', '')}</div>
                    <div class="task-meta">{t.get('created_at', '')[:10] if t.get('created_at') else ''}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if not todo:
            st.caption("No tasks")
    
    with k2:
        st.markdown(f'<div class="kanban-header">● IN PROGRESS <span style="opacity:0.5">({len(doing)})</span></div>', unsafe_allow_html=True)
        for t in doing:
            st.markdown(f"""
            <div class="task-item">
                <span class="task-dot blue"></span>
                <div>
                    <div class="task-text">{t.get('title', '')}</div>
                    <div class="task-meta">{t.get('created_at', '')[:10] if t.get('created_at') else ''}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if not doing:
            st.caption("No tasks in progress")
    
    with k3:
        st.markdown(f'<div class="kanban-header">● DONE <span style="opacity:0.5">({len(done) + len(batches[:5])})</span></div>', unsafe_allow_html=True)
        for t in done:
            st.markdown(f"""
            <div class="task-item">
                <span class="task-dot green"></span>
                <div>
                    <div class="task-text">{t.get('title', '')}</div>
                    <div class="task-meta">{t.get('created_at', '')[:10] if t.get('created_at') else ''}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show recent batches
        for b in batches[:5]:
            st.markdown(f"""
            <div class="task-item">
                <span class="task-dot green"></span>
                <div>
                    <div class="task-text">Batch: {b.get('shipped', 0)} orders shipped</div>
                    <div class="task-meta">{b.get('date', '')} {b.get('time', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with k4:
        st.markdown('<div class="kanban-header">● ARCHIVE</div>', unsafe_allow_html=True)
        archived_items = [
            "Dashboard UX overhaul",
            "Fix Kanban workflow",
            "Validate task tracking",
            "Update courier priorities"
        ]
        for item in archived_items:
            st.markdown(f"""
            <div class="task-item" style="opacity: 0.6;">
                <span class="task-dot gray"></span>
                <div class="task-text" style="color: #6e7681;">{item}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f'<button class="archive-btn">Show all {len(batches)} archived ▼</button>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === BOTTOM SECTIONS ===
    b1, b2 = st.columns(2)
    
    with b1:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">📦 Scheduled Deliverables</div>
        """, unsafe_allow_html=True)
        
        for sched in schedules[:3]:
            badge_class = "" if sched.get('enabled') else "disabled"
            badge_text = "✓ Active" if sched.get('enabled') else "○ Disabled"
            st.markdown(f"""
            <div class="schedule-item">
                <div>
                    <div class="schedule-name">{sched.get('name', '')}</div>
                    <div class="schedule-meta">{sched.get('time', '')} • {', '.join(sched.get('days', [])[:2])}</div>
                </div>
                <span class="schedule-badge {badge_class}">{badge_text}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if not schedules:
            st.caption("No scheduled deliverables")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with b2:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">📝 Notes</div>
        """, unsafe_allow_html=True)
        
        for note in notes[:3]:
            note_class = "ai" if note.get("type") == "ai" else ""
            content = note.get('content', '')[:100]
            st.markdown(f"""
            <div class="note-item {note_class}">
                <div class="note-text">{content}{'...' if len(note.get('content', '')) > 100 else ''}</div>
                <div class="note-time">{note.get('timestamp', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if not notes:
            st.caption("No notes yet")
        
        st.markdown("</div>", unsafe_allow_html=True)

# === SHIP NOW BUTTON ===
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Ship Orders Now", type="primary", use_container_width=True):
        with st.spinner("Processing orders..."):
            try:
                from shiprocket_workflow import run_shipping_workflow
                result = run_shipping_workflow()
                
                if result.get("shipped", 0) > 0:
                    st.success(f"✅ Shipped {result['shipped']} orders!")
                else:
                    st.warning("No orders to ship")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown('<div class="footer-text">Built with ❤️ by Kluzo 😎 • JSK Labs Admin Dashboard v3.0</div>', unsafe_allow_html=True)
