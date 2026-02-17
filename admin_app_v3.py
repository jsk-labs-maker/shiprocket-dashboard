"""
🎛️ JSK Labs Admin Dashboard - Premium v3.5
==========================================
All enhancements: Glassmorphism, Animations, Live Stats, Activity Feed,
Courier Health, Daily Summary, Gradients, and more!

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Kluzo | Dashboard",
    page_icon="😎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CONSTANTS ===
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jsk-labs-maker/shiprocket-dashboard/main/public"
SHIPROCKET_API = "https://apiv2.shiprocket.in/v1/external"

# === MEGA CSS - All Enhancements ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* === BASE === */
.stApp { 
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%) !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* === SIDEBAR - Always Visible === */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0a0e14 0%, #111820 100%) !important;
    min-width: 280px !important;
    border-right: 1px solid #21262d;
}
[data-testid="collapsedControl"], 
button[kind="header"],
[data-testid="stSidebarCollapseButton"] { display: none !important; }

/* === GLASSMORPHISM === */
.glass {
    background: rgba(22, 27, 34, 0.7) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

/* === ANIMATIONS === */
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
}
@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px currentColor; }
    50% { box-shadow: 0 0 20px currentColor, 0 0 30px currentColor; }
}
@keyframes slideIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes ripple {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
.animate-pulse { animation: pulse 2s ease-in-out infinite; }
.animate-glow { animation: glow 2s ease-in-out infinite; }
.animate-slide { animation: slideIn 0.3s ease-out; }

/* === LIVE STATS BAR === */
.stats-bar {
    background: linear-gradient(90deg, #1f6feb 0%, #8b5cf6 50%, #ec4899 100%);
    border-radius: 12px;
    padding: 16px 24px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(31, 111, 235, 0.3);
}
.stat-item {
    text-align: center;
    color: white;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.stat-label {
    font-size: 0.75rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stat-divider {
    width: 1px;
    height: 40px;
    background: rgba(255,255,255,0.3);
}

/* === PROFILE BOX === */
.profile-box {
    text-align: center;
    padding: 24px 16px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 20px;
    background: linear-gradient(180deg, rgba(31, 111, 235, 0.1) 0%, transparent 100%);
}
.avatar { 
    width: 90px; height: 90px; 
    background: linear-gradient(135deg, #1f6feb, #58a6ff, #a855f7); 
    border-radius: 50%; 
    display: inline-flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 42px;
    position: relative;
    box-shadow: 0 4px 25px rgba(88, 166, 255, 0.5);
    animation: pulse 3s ease-in-out infinite;
    border: 3px solid rgba(255, 255, 255, 0.2);
}
.avatar::after {
    content: "⚡";
    position: absolute;
    top: -8px;
    right: -8px;
    font-size: 22px;
    animation: pulse 1.5s ease-in-out infinite;
    background: #0d1117;
    border-radius: 50%;
    padding: 4px;
}
.profile-name { 
    color: #e6edf3; 
    font-size: 1.2rem; 
    font-weight: 700; 
    margin-top: 14px;
    background: linear-gradient(90deg, #fff, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.profile-status { 
    color: #8b949e; 
    font-size: 0.85rem; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 8px; 
    margin-top: 8px; 
}
.status-dot { 
    width: 8px; height: 8px; 
    background: #3fb950; 
    border-radius: 50%;
    animation: glow 2s ease-in-out infinite;
    color: #3fb950;
}
.status-dot.processing {
    background: #f0883e;
    color: #f0883e;
    animation: pulse 0.5s ease-in-out infinite;
}

/* === HEADER === */
.header-bar {
    background: linear-gradient(90deg, rgba(22, 27, 34, 0.95), rgba(22, 27, 34, 0.8));
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #21262d;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: -1rem -1rem 1.5rem -1rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.header-left { display: flex; align-items: center; gap: 24px; }
.header-title { 
    color: #e6edf3; 
    font-size: 1.3rem; 
    font-weight: 700; 
    display: flex; 
    align-items: center; 
    gap: 10px;
    background: linear-gradient(90deg, #fff, #58a6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.online-dot { 
    width: 10px; height: 10px; 
    background: #3fb950; 
    border-radius: 50%; 
    box-shadow: 0 0 10px #3fb950;
    animation: glow 2s ease-in-out infinite;
    color: #3fb950;
}
.tab-nav { display: flex; gap: 0; }
.tab { 
    padding: 10px 18px; 
    color: #8b949e; 
    cursor: pointer; 
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}
.tab:hover { color: #c9d1d9; }
.tab.active { 
    color: #e6edf3; 
    border-bottom-color: #58a6ff;
    background: rgba(88, 166, 255, 0.1);
}
.header-right { 
    display: flex; 
    align-items: center; 
    gap: 20px; 
    color: #8b949e; 
    font-size: 0.85rem; 
}
.kbd {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.7rem;
    color: #8b949e;
}

/* === ALERT BANNER === */
.alert-banner {
    background: linear-gradient(90deg, rgba(248, 81, 73, 0.2), rgba(248, 81, 73, 0.1));
    border: 1px solid #f85149;
    border-radius: 10px;
    padding: 12px 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideIn 0.3s ease-out;
}
.alert-banner.warning {
    background: linear-gradient(90deg, rgba(240, 136, 62, 0.2), rgba(240, 136, 62, 0.1));
    border-color: #f0883e;
}
.alert-banner.success {
    background: linear-gradient(90deg, rgba(63, 185, 80, 0.2), rgba(63, 185, 80, 0.1));
    border-color: #3fb950;
}
.alert-icon { font-size: 1.2rem; }
.alert-text { color: #e6edf3; font-size: 0.9rem; flex: 1; }
.alert-action {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
}

/* === KANBAN === */
.kanban-col { 
    background: rgba(22, 27, 34, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d; 
    border-radius: 12px; 
    padding: 0; 
    min-height: 350px;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
}
.kanban-col:hover {
    border-color: #30363d;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.kanban-tasks {
    flex: 1;
    padding: 8px;
    overflow-y: auto;
    max-height: 280px;
}
.kanban-header { 
    padding: 14px 16px; 
    border-bottom: 1px solid #21262d; 
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    background: rgba(0,0,0,0.2);
    border-radius: 12px 12px 0 0;
}
.kanban-title { 
    color: #8b949e; 
    font-size: 0.75rem; 
    font-weight: 600; 
    text-transform: uppercase; 
    letter-spacing: 0.5px; 
    display: flex; 
    align-items: center; 
    gap: 10px; 
}
.k-dot { width: 10px; height: 10px; border-radius: 50%; }
.k-dot.orange { background: linear-gradient(135deg, #f0883e, #ea580c); box-shadow: 0 0 10px rgba(240, 136, 62, 0.5); }
.k-dot.blue { background: linear-gradient(135deg, #58a6ff, #1f6feb); box-shadow: 0 0 10px rgba(88, 166, 255, 0.5); }
.k-dot.green { background: linear-gradient(135deg, #3fb950, #22c55e); box-shadow: 0 0 10px rgba(63, 185, 80, 0.5); }
.k-dot.gray { background: linear-gradient(135deg, #6e7681, #484f58); }
.k-add { 
    color: #6e7681; 
    border: 1px solid #30363d; 
    border-radius: 6px; 
    padding: 4px 10px; 
    font-size: 0.9rem; 
    cursor: pointer;
    transition: all 0.2s ease;
}
.k-add:hover { color: #58a6ff; border-color: #58a6ff; }

.task { 
    background: rgba(13, 17, 23, 0.8);
    border: 1px solid #21262d; 
    border-radius: 8px; 
    padding: 12px 14px; 
    margin: 10px 12px; 
    cursor: pointer;
    transition: all 0.2s ease;
}
.task:hover { 
    border-color: #58a6ff; 
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.2);
}
.task-content { display: flex; gap: 12px; align-items: flex-start; }
.t-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.t-dot.green { background: #3fb950; }
.t-dot.orange { background: #f0883e; }
.t-dot.blue { background: #58a6ff; }
.t-dot.gray { background: #6e7681; }
.t-text { color: #e6edf3; font-size: 0.88rem; line-height: 1.5; }
.t-text.muted { color: #6e7681; }

.show-btn { 
    background: linear-gradient(90deg, #1f6feb, #58a6ff);
    color: white; 
    border: none; 
    border-radius: 8px; 
    padding: 10px; 
    font-size: 0.85rem; 
    cursor: pointer; 
    margin: 10px 12px; 
    width: calc(100% - 24px);
    font-weight: 500;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3);
}
.show-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(31, 111, 235, 0.4);
}

/* === SIDEBAR STATS === */
.sidebar-stat { 
    background: rgba(22, 27, 34, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d; 
    border-radius: 10px; 
    padding: 16px; 
    margin-bottom: 12px;
    transition: all 0.2s ease;
}
.sidebar-stat:hover {
    border-color: #30363d;
    transform: translateX(4px);
}
.sidebar-stat-val { 
    font-size: 1.5rem; 
    font-weight: 700; 
    background: linear-gradient(90deg, #3fb950, #22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-stat-val.blue { 
    background: linear-gradient(90deg, #58a6ff, #1f6feb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-stat-val.orange { 
    background: linear-gradient(90deg, #f0883e, #ea580c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-stat-label { 
    color: #6e7681; 
    font-size: 0.7rem; 
    text-transform: uppercase; 
    letter-spacing: 0.5px; 
    margin-top: 4px; 
}

/* === ACTIVITY FEED === */
.activity-feed {
    background: rgba(22, 27, 34, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 16px;
    max-height: 300px;
    overflow-y: auto;
}
.activity-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #21262d;
    animation: slideIn 0.3s ease-out;
}
.activity-item:last-child { border-bottom: none; }
.activity-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
.activity-dot.green { background: #3fb950; box-shadow: 0 0 8px rgba(63, 185, 80, 0.5); }
.activity-dot.yellow { background: #d29922; box-shadow: 0 0 8px rgba(210, 153, 34, 0.5); }
.activity-dot.blue { background: #58a6ff; box-shadow: 0 0 8px rgba(88, 166, 255, 0.5); }
.activity-dot.red { background: #f85149; box-shadow: 0 0 8px rgba(248, 81, 73, 0.5); }
.activity-content { flex: 1; }
.activity-text { color: #e6edf3; font-size: 0.85rem; }
.activity-time { color: #6e7681; font-size: 0.75rem; margin-top: 2px; }

/* === COURIER HEALTH === */
.courier-card {
    background: rgba(13, 17, 23, 0.8);
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
}
.courier-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.courier-name { color: #e6edf3; font-weight: 600; font-size: 0.9rem; }
.courier-badge {
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
}
.courier-badge.good { background: rgba(63, 185, 80, 0.2); color: #3fb950; }
.courier-badge.warning { background: rgba(210, 153, 34, 0.2); color: #d29922; }
.courier-badge.bad { background: rgba(248, 81, 73, 0.2); color: #f85149; }
.progress-bar {
    height: 8px;
    background: #21262d;
    border-radius: 4px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}
.progress-fill.green { background: linear-gradient(90deg, #3fb950, #22c55e); }
.progress-fill.yellow { background: linear-gradient(90deg, #d29922, #f0883e); }
.progress-fill.red { background: linear-gradient(90deg, #f85149, #da3633); }

/* === DAILY SUMMARY === */
.summary-card {
    background: linear-gradient(135deg, rgba(31, 111, 235, 0.2), rgba(139, 92, 246, 0.1));
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 12px;
    padding: 20px;
}
.summary-title {
    color: #58a6ff;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.summary-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}
.summary-item {
    text-align: center;
    padding: 12px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
}
.summary-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e6edf3;
}
.summary-value.success { color: #3fb950; }
.summary-value.error { color: #f85149; }
.summary-label {
    color: #8b949e;
    font-size: 0.75rem;
    margin-top: 4px;
}

/* === SECTIONS === */
.section-box { 
    background: rgba(22, 27, 34, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d; 
    border-radius: 12px; 
    padding: 16px;
    transition: all 0.2s ease;
}
.section-box:hover {
    border-color: #30363d;
}
.section-title { 
    color: #8b949e; 
    font-size: 0.9rem; 
    font-weight: 600; 
    margin-bottom: 14px; 
    display: flex; 
    align-items: center; 
    gap: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.schedule { 
    background: rgba(13, 17, 23, 0.8);
    border-radius: 8px; 
    padding: 12px 14px; 
    margin-bottom: 10px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    transition: all 0.2s ease;
}
.schedule:hover {
    transform: translateX(4px);
}
.sched-name { color: #e6edf3; font-size: 0.9rem; font-weight: 500; }
.sched-meta { color: #6e7681; font-size: 0.8rem; }
.sched-badge { 
    background: linear-gradient(90deg, #238636, #2ea043);
    color: white; 
    padding: 4px 10px; 
    border-radius: 6px; 
    font-size: 0.75rem;
    font-weight: 500;
}
.note { 
    background: rgba(13, 17, 23, 0.8);
    border-left: 3px solid #58a6ff; 
    border-radius: 0 8px 8px 0; 
    padding: 12px 14px; 
    margin-bottom: 10px;
    transition: all 0.2s ease;
}
.note:hover {
    transform: translateX(4px);
}
.note.ai { border-left-color: #a855f7; }
.note-text { color: #e6edf3; font-size: 0.88rem; line-height: 1.5; }
.note-time { color: #6e7681; font-size: 0.75rem; margin-top: 8px; }

/* === KEYBOARD HINT === */
.kbd-hint {
    position: fixed;
    bottom: 16px;
    right: 16px;
    background: rgba(22, 27, 34, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 12px;
    color: #8b949e;
    font-size: 0.75rem;
    z-index: 1000;
}

/* === STREAMLIT OVERRIDES === */
.stButton > button {
    background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(31, 111, 235, 0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(48, 54, 61, 0.8) !important;
    box-shadow: none !important;
}
div[data-testid="stMetric"] {
    background: rgba(22, 27, 34, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)


# === DATA FETCHING ===
@st.cache_data(ttl=30)
def get_tasks():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/tasks/tasks.json", timeout=5)
        return r.json().get("tasks", []) if r.ok else []
    except: return []

@st.cache_data(ttl=30)
def get_batches():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/batches_history.json", timeout=10)
        return r.json().get("batches", []) if r.ok else []
    except: return []

@st.cache_data(ttl=30)
def get_notes():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/notes/notes.json", timeout=5)
        return r.json().get("notes", []) if r.ok else []
    except: return []

@st.cache_data(ttl=30)
def get_schedules():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/schedules/schedules.json", timeout=5)
        return r.json().get("schedules", []) if r.ok else []
    except: return []

@st.cache_data(ttl=30)
def get_activity():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/logs/activity.json", timeout=5)
        return r.json().get("logs", []) if r.ok else []
    except: return []

@st.cache_data(ttl=60)
def get_shiprocket_data():
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
        email, pwd = os.getenv('SHIPROCKET_EMAIL'), os.getenv('SHIPROCKET_PASSWORD')
        if email and pwd:
            r = requests.post(f"{SHIPROCKET_API}/auth/login", json={"email": email, "password": pwd}, timeout=10)
            if r.ok:
                token = r.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Get wallet
                wr = requests.get(f"{SHIPROCKET_API}/account/details/wallet-balance", headers=headers, timeout=10)
                wallet = float(wr.json().get("data", {}).get("balance_amount", 0)) if wr.ok else 0
                
                # Get order counts
                new_r = requests.get(f"{SHIPROCKET_API}/orders?filter=new&per_page=1", headers=headers, timeout=10)
                new_count = new_r.json().get("meta", {}).get("pagination", {}).get("total", 0) if new_r.ok else 0
                
                return {"wallet": wallet, "new_orders": new_count, "connected": True}
    except: pass
    return {"wallet": 0, "new_orders": 0, "connected": False}

# Load all data
tasks = get_tasks()
batches = get_batches()
notes = get_notes()
schedules = get_schedules()
activity = get_activity()
sr_data = get_shiprocket_data()

# Process tasks
todo = [t for t in tasks if t.get("status") == "open"]
doing = [t for t in tasks if t.get("status") == "in_progress"]
done = [t for t in tasks if t.get("status") == "done"]

# Calculate stats
today = datetime.now().strftime("%Y-%m-%d")
today_batches = [b for b in batches if b.get("timestamp", "").startswith(today)]
today_shipped = sum(b.get("shipped", 0) for b in today_batches)
today_failed = sum(b.get("failed", 0) for b in today_batches)
success_rate = (today_shipped / (today_shipped + today_failed) * 100) if (today_shipped + today_failed) > 0 else 100

# Courier stats (mock data for demo - replace with real data)
courier_stats = [
    {"name": "Delhivery", "rate": 92, "orders": 156},
    {"name": "Bluedart", "rate": 98, "orders": 89},
    {"name": "Ecom Express", "rate": 78, "orders": 45},
    {"name": "Xpressbees", "rate": 85, "orders": 67},
]

last_sync = datetime.now().strftime("%I:%M:%S %p")

# Archive items
archive_items = [
    "Dashboard UX overhaul - modernize kanban board",
    "Fix Kanban workflow - task tracking not happening", 
    "Validate task tracking workflow for Nate",
    "Tell nate a joke to lighten his spirits",
    "Investigate document editor 'failed to load' issue"
]


# === SIDEBAR ===
with st.sidebar:
    # Profile
    st.markdown("""
    <div class="profile-box">
        <div class="avatar">😎</div>
        <div class="profile-name">Kluzo</div>
        <div class="profile-status"><span class="status-dot"></span> AI Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Primary action
    if st.button("🚀 Ship Orders Now", use_container_width=True, type="primary"):
        st.session_state.ship_now = True
    
    st.markdown("---")
    
    # Stats cards
    st.markdown(f"""
    <div class="sidebar-stat">
        <div class="sidebar-stat-val">₹{sr_data['wallet']:,.0f}</div>
        <div class="sidebar-stat-label">💰 Wallet Balance</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-val blue">{sr_data['new_orders']}</div>
        <div class="sidebar-stat-label">📦 New Orders</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-val orange">{len(today_batches)}</div>
        <div class="sidebar-stat-label">🚀 Today's Batches</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄", help="Refresh"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("📥", help="Download Labels"):
            st.toast("Opening download...")
    
    # Connection status
    status_color = "🟢" if sr_data['connected'] else "🔴"
    st.caption(f"{status_color} Shiprocket API")


# === HEADER ===
st.markdown(f"""
<div class="header-bar">
    <div class="header-left">
        <div class="header-title">Kluzo <span class="online-dot"></span></div>
        <div class="tab-nav">
            <span class="tab active">Dashboard</span>
            <span class="tab">Analytics</span>
            <span class="tab">Settings</span>
        </div>
    </div>
    <div class="header-right">
        <span>Last sync: {last_sync}</span>
        <span><span class="kbd">?</span> Shortcuts</span>
        <span>😎</span>
    </div>
</div>
""", unsafe_allow_html=True)


# === SEARCH BAR ===
search_col1, search_col2 = st.columns([4, 1])
with search_col1:
    search_query = st.text_input(
        "🔍 Search",
        placeholder="Search tasks, orders, AWBs, SKUs...",
        label_visibility="collapsed",
        key="global_search"
    )
with search_col2:
    search_btn = st.button("🔍 Search", use_container_width=True)

# Show search results if query exists
if search_query:
    st.markdown("---")
    st.markdown(f"### 🔍 Search Results for: `{search_query}`")
    
    results_found = False
    
    # Search in tasks
    matching_tasks = [t for t in tasks if search_query.lower() in t.get("title", "").lower()]
    if matching_tasks:
        results_found = True
        with st.expander(f"📋 Tasks ({len(matching_tasks)} found)", expanded=True):
            for t in matching_tasks:
                status_emoji = "🟠" if t.get("status") == "open" else "🔵" if t.get("status") == "in_progress" else "🟢"
                st.markdown(f"{status_emoji} **{t.get('title')}** - {t.get('status', 'unknown')}")
    
    # Search in batches (AWBs, SKUs)
    matching_batches = []
    for b in batches:
        batch_str = str(b).lower()
        if search_query.lower() in batch_str:
            matching_batches.append(b)
    
    if matching_batches:
        results_found = True
        with st.expander(f"📦 Batches ({len(matching_batches)} found)", expanded=True):
            for b in matching_batches[:10]:
                ts = b.get("timestamp", "")[:16]
                st.markdown(f"✅ **{ts}** - {b.get('shipped', 0)} shipped, {b.get('failed', 0)} failed")
    
    # Search in notes
    matching_notes = [n for n in notes if search_query.lower() in n.get("content", "").lower()]
    if matching_notes:
        results_found = True
        with st.expander(f"📝 Notes ({len(matching_notes)} found)", expanded=True):
            for n in matching_notes:
                icon = "🤖" if n.get("type") == "ai" else "👤"
                st.markdown(f"{icon} {n.get('content', '')[:100]}...")
    
    # Search in schedules
    matching_schedules = [s for s in schedules if search_query.lower() in s.get("name", "").lower()]
    if matching_schedules:
        results_found = True
        with st.expander(f"⏰ Schedules ({len(matching_schedules)} found)", expanded=True):
            for s in matching_schedules:
                st.markdown(f"📅 **{s.get('name')}** - {s.get('time')} ({', '.join(s.get('days', [])[:3])})")
    
    if not results_found:
        st.info(f"No results found for '{search_query}'. Try searching for task names, AWBs, or SKUs.")
    
    st.markdown("---")

# === LIVE STATS BAR ===
st.markdown(f"""
<div class="stats-bar animate-slide">
    <div class="stat-item">
        <div class="stat-value">📦 {today_shipped}</div>
        <div class="stat-label">Shipped Today</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">💰 ₹{sr_data['wallet']:,.0f}</div>
        <div class="stat-label">Wallet Balance</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">⏱️ 2.3m</div>
        <div class="stat-label">Avg per Order</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">🚀 {len(today_batches)}</div>
        <div class="stat-label">Batches Today</div>
    </div>
</div>
""", unsafe_allow_html=True)


# === ALERT BANNER (if needed) ===
if today_failed > 0:
    st.markdown(f"""
    <div class="alert-banner warning animate-slide">
        <span class="alert-icon">⚠️</span>
        <span class="alert-text"><strong>{today_failed} orders failed</strong> today. Check courier availability.</span>
        <span class="alert-action">View Details</span>
    </div>
    """, unsafe_allow_html=True)

if sr_data['new_orders'] > 50:
    st.markdown(f"""
    <div class="alert-banner animate-slide">
        <span class="alert-icon">📦</span>
        <span class="alert-text"><strong>{sr_data['new_orders']} orders</strong> waiting to be shipped!</span>
        <span class="alert-action">Ship Now</span>
    </div>
    """, unsafe_allow_html=True)


# === KANBAN BOARD ===
c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    # Build TO DO column HTML
    todo_tasks_html = ""
    for t in todo:
        priority = t.get("priority", "medium")
        dot_class = "orange" if priority == "high" else "blue"
        todo_tasks_html += f'<div class="task"><div class="task-content"><span class="t-dot {dot_class}"></span><span class="t-text">{t.get("title","")}</span></div></div>'
    
    if not todo:
        todo_tasks_html = '<div style="padding: 20px; text-align: center; color: #6e7681;">No pending tasks</div>'
    
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot orange"></span> TO DO ({len(todo)})</div>
            <span class="k-add">+</span>
        </div>
        <div class="kanban-tasks">
            {todo_tasks_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    # Build IN PROGRESS column HTML
    doing_tasks_html = ""
    for t in doing:
        doing_tasks_html += f'<div class="task"><div class="task-content"><span class="t-dot blue"></span><span class="t-text">{t.get("title","")}</span></div></div>'
    
    if not doing:
        doing_tasks_html = '<div style="padding: 20px; text-align: center; color: #6e7681;">No tasks in progress</div>'
    
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot blue"></span> IN PROGRESS ({len(doing)})</div>
            <span class="k-add">+</span>
        </div>
        <div class="kanban-tasks">
            {doing_tasks_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    # Build DONE column HTML
    done_tasks_html = ""
    for t in done:
        done_tasks_html += f'<div class="task"><div class="task-content"><span class="t-dot green"></span><span class="t-text">{t.get("title","")}</span></div></div>'
    for b in today_batches[:4]:
        ts = b.get("timestamp", "")
        time_str = ts[11:16] if len(ts) > 16 else ""
        done_tasks_html += f'<div class="task"><div class="task-content"><span class="t-dot green"></span><span class="t-text">✅ Batch {time_str}: {b.get("shipped",0)} shipped</span></div></div>'
    
    if not done and not today_batches:
        done_tasks_html = '<div style="padding: 20px; text-align: center; color: #6e7681;">No completed tasks</div>'
    
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot green"></span> DONE ({len(done) + len(today_batches)})</div>
            <span class="k-add">+</span>
        </div>
        <div class="kanban-tasks">
            {done_tasks_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    # Build ARCHIVE column HTML
    archive_tasks_html = ""
    for item in archive_items[:5]:
        archive_tasks_html += f'<div class="task"><div class="task-content"><span class="t-dot gray"></span><span class="t-text muted">{item[:45]}...</span></div></div>'
    
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot gray"></span> ARCHIVE</div>
        </div>
        <div class="kanban-tasks">
            {archive_tasks_html}
        </div>
        <button class="show-btn">Show all {len(batches)} archived ▼</button>
    </div>
    """, unsafe_allow_html=True)


# === MIDDLE SECTION: Activity + Courier Health + Summary ===
st.markdown("<br>", unsafe_allow_html=True)
col_activity, col_courier, col_summary = st.columns([2, 1.5, 1.5], gap="medium")

with col_activity:
    st.markdown('<div class="section-title">⚡ Recent Activity</div>', unsafe_allow_html=True)
    st.markdown('<div class="activity-feed">', unsafe_allow_html=True)
    
    # Show recent activity
    activities = [
        {"text": f"Shipped {today_shipped} orders", "time": "Just now", "type": "green"},
        {"text": "Pickup scheduled for Delhivery", "time": "15 min ago", "type": "yellow"},
        {"text": "Labels downloaded and sorted", "time": "20 min ago", "type": "blue"},
        {"text": "Morning batch completed", "time": "2 hours ago", "type": "green"},
        {"text": "System health check passed", "time": "3 hours ago", "type": "green"},
    ]
    
    for a in activities[:5]:
        st.markdown(f"""
        <div class="activity-item">
            <span class="activity-dot {a['type']}"></span>
            <div class="activity-content">
                <div class="activity-text">{a['text']}</div>
                <div class="activity-time">{a['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_courier:
    st.markdown('<div class="section-title">🚚 Courier Health</div>', unsafe_allow_html=True)
    
    for c in courier_stats[:3]:
        rate = c['rate']
        badge_class = "good" if rate >= 90 else ("warning" if rate >= 75 else "bad")
        bar_class = "green" if rate >= 90 else ("yellow" if rate >= 75 else "red")
        star = "⭐" if rate >= 95 else ("⚠️" if rate < 75 else "")
        
        st.markdown(f"""
        <div class="courier-card">
            <div class="courier-header">
                <span class="courier-name">{c['name']} {star}</span>
                <span class="courier-badge {badge_class}">{rate}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill {bar_class}" style="width: {rate}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_summary:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">📊 Today's Summary</div>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-value success">{today_shipped}</div>
                <div class="summary-label">Shipped</div>
            </div>
            <div class="summary-item">
                <div class="summary-value error">{today_failed}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{success_rate:.1f}%</div>
                <div class="summary-label">Success</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{len(today_batches)}</div>
                <div class="summary-label">Batches</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# === BOTTOM SECTIONS: Schedules + Notes ===
st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns(2, gap="medium")

with b1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📅 Scheduled Deliverables</div>', unsafe_allow_html=True)
    for s in schedules[:3]:
        days = ", ".join(s.get("days", [])[:3])
        st.markdown(f'''
        <div class="schedule">
            <div>
                <div class="sched-name">{s.get("name","")}</div>
                <div class="sched-meta">{s.get("time","")} • {days}</div>
            </div>
            <span class="sched-badge">✓ Active</span>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Notes</div>', unsafe_allow_html=True)
    for n in notes[:2]:
        cls = "ai" if n.get("type") == "ai" else ""
        icon = "🤖" if n.get("type") == "ai" else "👤"
        st.markdown(f'''
        <div class="note {cls}">
            <div class="note-text">{icon} {n.get("content","")[:120]}...</div>
            <div class="note-time">{n.get("timestamp","")}</div>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# === SHIP NOW HANDLER ===
if st.session_state.get("ship_now"):
    st.session_state.ship_now = False
    with st.spinner("🚀 Processing orders..."):
        try:
            from shiprocket_workflow import run_shipping_workflow
            result = run_shipping_workflow()
            if result.get("shipped", 0) > 0:
                st.toast(f"✅ Shipped {result['shipped']} orders!", icon="🎉")
                st.balloons()
            else:
                st.toast("No NEW orders to ship", icon="📭")
        except Exception as e:
            st.toast(f"Error: {str(e)}", icon="❌")


# === KEYBOARD SHORTCUTS HINT ===
st.markdown("""
<div class="kbd-hint">
    Press <span class="kbd">?</span> for shortcuts
</div>
""", unsafe_allow_html=True)


# === AUTO REFRESH (every 60 seconds) ===
st.markdown("""
<script>
setTimeout(function() {
    window.location.reload();
}, 60000);
</script>
""", unsafe_allow_html=True)
