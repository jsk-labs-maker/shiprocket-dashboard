"""
🎛️ JSK Labs Admin Dashboard - Claude Style v3.2
================================================
Using Streamlit components with custom CSS

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import requests
from datetime import datetime, timedelta

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Kluzo | Dashboard",
    page_icon="😎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === CONSTANTS ===
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jsk-labs-maker/shiprocket-dashboard/main/public"
SHIPROCKET_API = "https://apiv2.shiprocket.in/v1/external"

# === CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp { background: #0d1117 !important; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="stSidebar"] { background: #080b10 !important; }

/* Sidebar profile */
.profile-box {
    text-align: center;
    padding: 20px 10px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 20px;
}
.avatar { 
    width: 70px; height: 70px; 
    background: linear-gradient(135deg, #fbbf24, #f59e0b); 
    border-radius: 50%; 
    display: inline-flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 32px;
    position: relative;
}
.avatar::after {
    content: "✨";
    position: absolute;
    top: -8px;
    right: -8px;
    font-size: 16px;
}
.profile-name { color: #e6edf3; font-size: 1.1rem; font-weight: 600; margin-top: 12px; }
.profile-status { color: #8b949e; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 6px; }
.status-dot { width: 6px; height: 6px; background: #3fb950; border-radius: 50%; }

/* Header */
.header-bar {
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: -1rem -1rem 1rem -1rem;
}
.header-left { display: flex; align-items: center; gap: 20px; }
.header-title { color: #e6edf3; font-size: 1.2rem; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.online-dot { width: 8px; height: 8px; background: #3fb950; border-radius: 50%; box-shadow: 0 0 8px #3fb950; }
.tab-nav { display: flex; gap: 0; }
.tab { padding: 8px 14px; color: #8b949e; cursor: pointer; border-bottom: 2px solid transparent; }
.tab.active { color: #e6edf3; border-bottom-color: #58a6ff; }
.header-right { display: flex; align-items: center; gap: 16px; color: #8b949e; font-size: 0.8rem; }

/* Kanban */
.kanban-col { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 0; min-height: 380px; }
.kanban-header { 
    padding: 12px 14px; 
    border-bottom: 1px solid #21262d; 
    display: flex; 
    justify-content: space-between; 
    align-items: center;
}
.kanban-title { color: #8b949e; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; }
.k-dot { width: 8px; height: 8px; border-radius: 50%; }
.k-dot.orange { background: #f0883e; }
.k-dot.blue { background: #58a6ff; }
.k-dot.green { background: #3fb950; }
.k-dot.gray { background: #6e7681; }
.k-add { color: #6e7681; border: 1px solid #30363d; border-radius: 4px; padding: 2px 8px; font-size: 0.9rem; cursor: pointer; }
.k-add:hover { color: #8b949e; }

.task { background: #0d1117; border: 1px solid #21262d; border-radius: 6px; padding: 10px 12px; margin: 8px 10px; cursor: pointer; }
.task:hover { border-color: #58a6ff; }
.task-content { display: flex; gap: 10px; align-items: flex-start; }
.t-dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.t-dot.green { background: #3fb950; }
.t-dot.orange { background: #f0883e; }
.t-dot.blue { background: #58a6ff; }
.t-dot.gray { background: #6e7681; }
.t-text { color: #e6edf3; font-size: 0.85rem; line-height: 1.4; }
.t-text.muted { color: #6e7681; }

.show-btn { background: #1f6feb; color: white; border: none; border-radius: 6px; padding: 8px; font-size: 0.8rem; cursor: pointer; margin: 8px 10px; width: calc(100% - 20px); }

/* Stats */
.stat-box { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 14px; margin-bottom: 10px; }
.stat-val { font-size: 1.4rem; font-weight: 700; color: #3fb950; }
.stat-val.blue { color: #58a6ff; }
.stat-val.orange { color: #f0883e; }
.stat-label { color: #6e7681; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }

/* Bottom sections */
.section-box { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 14px; }
.section-title { color: #8b949e; font-size: 0.85rem; font-weight: 500; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.schedule { background: #0d1117; border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
.sched-name { color: #e6edf3; font-size: 0.85rem; font-weight: 500; }
.sched-meta { color: #6e7681; font-size: 0.75rem; }
.sched-badge { background: #238636; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; }
.note { background: #0d1117; border-left: 3px solid #58a6ff; border-radius: 0 6px 6px 0; padding: 10px 12px; margin-bottom: 8px; }
.note.ai { border-left-color: #a855f7; }
.note-text { color: #e6edf3; font-size: 0.85rem; line-height: 1.4; }
.note-time { color: #6e7681; font-size: 0.7rem; margin-top: 6px; }

/* Video widget */
.video-box { 
    position: fixed; 
    bottom: 16px; 
    left: 16px; 
    width: 160px; 
    height: 120px; 
    background: #0d1117; 
    border: 1px solid #21262d; 
    border-radius: 8px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 2rem;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)


# === DATA ===
@st.cache_data(ttl=30)
def get_tasks():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/tasks/tasks.json", timeout=5)
        return r.json().get("tasks", []) if r.ok else []
    except: return []

@st.cache_data(ttl=60)
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
                wr = requests.get(f"{SHIPROCKET_API}/account/details/wallet-balance", headers=headers, timeout=10)
                wallet = float(wr.json().get("data", {}).get("balance_amount", 0)) if wr.ok else 0
                return wallet
    except: pass
    return 0

# Load data
tasks = get_tasks()
batches = get_batches()
notes = get_notes()
schedules = get_schedules()
wallet = get_shiprocket_data()

todo = [t for t in tasks if t.get("status") == "open"]
doing = [t for t in tasks if t.get("status") == "in_progress"]
done = [t for t in tasks if t.get("status") == "done"]

archive_items = [
    "Dashboard UX overhaul - modernize kanban board",
    "Fix Kanban workflow - task tracking not happening", 
    "Validate task tracking workflow for Nate",
    "Tell nate a joke to lighten his spirits",
    "Investigate document editor 'failed to load' issue"
]

last_sync = datetime.now().strftime("%I:%M:%S %p")

# === SIDEBAR ===
with st.sidebar:
    st.markdown("""
    <div class="profile-box">
        <div class="avatar">😊</div>
        <div class="profile-name">Kluzo</div>
        <div class="profile-status"><span class="status-dot"></span> 😎 Idle</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Ready for tasks", use_container_width=True, type="primary"):
        st.toast("Ready! 😎")
    
    st.markdown(f"""
    <div class="stat-box"><div class="stat-val">₹{wallet:,.0f}</div><div class="stat-label">Wallet Balance</div></div>
    <div class="stat-box"><div class="stat-val blue">0</div><div class="stat-label">NEW Orders</div></div>
    <div class="stat-box"><div class="stat-val orange">{len(batches)}</div><div class="stat-label">Total Batches</div></div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# === HEADER ===
st.markdown(f"""
<div class="header-bar">
    <div class="header-left">
        <div class="header-title">Kluzo <span class="online-dot"></span></div>
        <div class="tab-nav">
            <span class="tab active">Dashboard</span>
            <span class="tab">Docs</span>
            <span class="tab">Log</span>
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

# === KANBAN ===
c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot orange"></span> TO DO ({len(todo)})</div>
            <span class="k-add">+</span>
        </div>
    """, unsafe_allow_html=True)
    for t in todo:
        st.markdown(f'<div class="task"><div class="task-content"><span class="t-dot orange"></span><span class="t-text">{t.get("title","")}</span></div></div>', unsafe_allow_html=True)
    if not todo:
        st.caption("No tasks")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot blue"></span> IN PROGRESS ({len(doing)})</div>
            <span class="k-add">+</span>
        </div>
    """, unsafe_allow_html=True)
    for t in doing:
        st.markdown(f'<div class="task"><div class="task-content"><span class="t-dot blue"></span><span class="t-text">{t.get("title","")}</span></div></div>', unsafe_allow_html=True)
    if not doing:
        st.caption("No tasks in progress")
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot green"></span> DONE ({len(done) + min(len(batches), 6)})</div>
            <span class="k-add">+</span>
        </div>
    """, unsafe_allow_html=True)
    for t in done:
        st.markdown(f'<div class="task"><div class="task-content"><span class="t-dot green"></span><span class="t-text">{t.get("title","")}</span></div></div>', unsafe_allow_html=True)
    for b in batches[:6]:
        st.markdown(f'<div class="task"><div class="task-content"><span class="t-dot green"></span><span class="t-text">Batch: {b.get("shipped",0)} orders shipped</span></div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="kanban-col">
        <div class="kanban-header">
            <div class="kanban-title"><span class="k-dot gray"></span> ARCHIVE</div>
        </div>
    """, unsafe_allow_html=True)
    for item in archive_items:
        st.markdown(f'<div class="task"><div class="task-content"><span class="t-dot gray"></span><span class="t-text muted">{item}</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<button class="show-btn">Show all {len(batches)} archived ▼</button></div>', unsafe_allow_html=True)

# === BOTTOM SECTIONS ===
st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns(2, gap="small")

with b1:
    st.markdown('<div class="section-box"><div class="section-title">📦 Scheduled Deliverables</div>', unsafe_allow_html=True)
    for s in schedules[:3]:
        st.markdown(f'''
        <div class="schedule">
            <div><div class="sched-name">{s.get("name","")}</div><div class="sched-meta">{s.get("time","")} • {", ".join(s.get("days",[])[:2])}</div></div>
            <span class="sched-badge">✓ Active</span>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown('<div class="section-box"><div class="section-title">📝 Notes</div>', unsafe_allow_html=True)
    for n in notes[:2]:
        cls = "ai" if n.get("type") == "ai" else ""
        st.markdown(f'''
        <div class="note {cls}">
            <div class="note-text">{n.get("content","")[:100]}...</div>
            <div class="note-time">{n.get("timestamp","")}</div>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# === SHIP NOW ===
st.markdown("<br>", unsafe_allow_html=True)
_, col_center, _ = st.columns([1, 2, 1])
with col_center:
    if st.button("🚀 Ship Orders Now", use_container_width=True, type="primary"):
        with st.spinner("Processing..."):
            try:
                from shiprocket_workflow import run_shipping_workflow
                result = run_shipping_workflow()
                if result.get("shipped", 0) > 0:
                    st.success(f"✅ Shipped {result['shipped']} orders!")
                else:
                    st.warning("No NEW orders")
            except Exception as e:
                st.error(str(e))

# Video widget
st.markdown('<div class="video-box">📹</div>', unsafe_allow_html=True)
