"""
🎛️ JSK Labs Admin Dashboard - Premium v3.5
==========================================
All enhancements: Glassmorphism, Animations, Live Stats, Activity Feed,
Courier Health, Daily Summary, Gradients, and more!

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
from datetime import datetime, timedelta
import json
import os
import base64

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Kluzo | Dashboard",
    page_icon="😎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 60 seconds (60000 ms)
st_autorefresh(interval=60000, limit=None, key="auto_refresh")

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
.avatar-img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 4px 30px rgba(88, 166, 255, 0.6);
    animation: pulse 3s ease-in-out infinite;
    border: 3px solid rgba(255, 255, 255, 0.1);
}
.header-logo {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    vertical-align: middle;
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
/* Kanban Column Base */
.kanban-col { 
    border-radius: 12px; 
    padding: 0; 
    height: 450px;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
/* TO DO - Orange */
.kanban-col.todo {
    border: 2px solid #f0883e;
    background: linear-gradient(180deg, rgba(240, 136, 62, 0.15) 0%, rgba(13, 17, 23, 0.95) 100%);
}
/* IN PROGRESS - Blue */
.kanban-col.doing {
    border: 2px solid #58a6ff;
    background: linear-gradient(180deg, rgba(88, 166, 255, 0.15) 0%, rgba(13, 17, 23, 0.95) 100%);
}
/* DONE - Green */
.kanban-col.done {
    border: 2px solid #3fb950;
    background: linear-gradient(180deg, rgba(63, 185, 80, 0.15) 0%, rgba(13, 17, 23, 0.95) 100%);
}
.kanban-tasks {
    flex: 1;
    padding: 12px;
    overflow-y: auto;
    max-height: 380px;
}
.kanban-tasks::-webkit-scrollbar { width: 6px; }
.kanban-tasks::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); border-radius: 3px; }
.kanban-tasks::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
.kanban-tasks::-webkit-scrollbar-thumb:hover { background: #58a6ff; }
.kanban-header { 
    padding: 12px 16px; 
    display: flex; 
    justify-content: center; 
    align-items: center;
}
.kanban-header-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kanban-header-pill.todo { background: rgba(240, 136, 62, 0.2); border: 1px solid #f0883e; color: #f0883e; }
.kanban-header-pill.doing { background: rgba(88, 166, 255, 0.2); border: 1px solid #58a6ff; color: #58a6ff; }
.kanban-header-pill.done { background: rgba(63, 185, 80, 0.2); border: 1px solid #3fb950; color: #3fb950; }
.kanban-header-pill.archive { background: rgba(110, 118, 129, 0.2); border: 1px solid #6e7681; color: #8b949e; }
.k-dot { width: 12px; height: 12px; border-radius: 50%; }
.k-dot.orange { background: #f0883e; box-shadow: 0 0 8px rgba(240, 136, 62, 0.6); }
.k-dot.blue { background: #58a6ff; box-shadow: 0 0 8px rgba(88, 166, 255, 0.6); }
.k-dot.green { background: #3fb950; box-shadow: 0 0 8px rgba(63, 185, 80, 0.6); }
.k-dot.gray { background: #6e7681; }

/* Task Card */
.task { 
    background: rgba(13, 17, 23, 0.9);
    border: 1px solid #30363d; 
    border-radius: 10px; 
    padding: 14px 16px; 
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.task:hover { 
    border-color: #58a6ff; 
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.task-left { display: flex; gap: 12px; align-items: center; flex: 1; }
.task-right { display: flex; gap: 6px; align-items: center; }
.task-btn {
    background: rgba(110, 118, 129, 0.3);
    border: none;
    border-radius: 6px;
    padding: 6px 8px;
    cursor: pointer;
    font-size: 0.75rem;
    transition: all 0.2s ease;
}
.task-btn:hover { background: rgba(110, 118, 129, 0.5); }
.task-btn.delete { color: #f85149; }
.task-btn.delete:hover { background: rgba(248, 81, 73, 0.2); }
.t-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.t-dot.red { background: #f85149; box-shadow: 0 0 6px rgba(248, 81, 73, 0.5); }
.t-dot.orange { background: #f0883e; box-shadow: 0 0 6px rgba(240, 136, 62, 0.5); }
.t-dot.green { background: #3fb950; box-shadow: 0 0 6px rgba(63, 185, 80, 0.5); }
.t-text { color: #e6edf3; font-size: 0.9rem; line-height: 1.4; }
.empty-state { color: #6e7681; font-size: 0.85rem; padding: 20px; text-align: center; }

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
    background: rgba(22, 27, 34, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid #30363d; 
    border-radius: 12px; 
    padding: 20px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
    height: 350px;
    display: flex;
    flex-direction: column;
}
.section-box:hover {
    border-color: #58a6ff;
    box-shadow: 0 0 10px rgba(88, 166, 255, 0.1);
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
    flex-shrink: 0;
}
.section-content {
    flex: 1;
    overflow-y: auto;
    padding-right: 5px;
}
.section-content::-webkit-scrollbar { width: 6px; }
.section-content::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); border-radius: 3px; }
.section-content::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
.section-content::-webkit-scrollbar-thumb:hover { background: #58a6ff; }
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
    flex-shrink: 0;
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
.note-text { color: #e6edf3; font-size: 0.88rem; line-height: 1.5; word-wrap: break-word; }
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
# === DOCUMENT MANAGEMENT ===
def get_documents():
    """Load documents list from local file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_file = os.path.join(script_dir, "public", "documents", "index.json")
    
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as f:
                data = json.load(f)
                docs = data.get("documents", [])
                # Filter out documents older than 7 days
                cutoff = datetime.now() - timedelta(days=7)
                fresh_docs = []
                for d in docs:
                    try:
                        doc_date = datetime.fromisoformat(d.get("created_at", ""))
                        if doc_date >= cutoff:
                            fresh_docs.append(d)
                    except:
                        fresh_docs.append(d)
                # Save cleaned list if any removed
                if len(fresh_docs) < len(docs):
                    save_documents_index(fresh_docs)
                return fresh_docs
        except:
            pass
    return []

def save_documents_index(documents):
    """Save documents index to local file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_file = os.path.join(script_dir, "public", "documents", "index.json")
    os.makedirs(os.path.dirname(index_file), exist_ok=True)
    with open(index_file, "w") as f:
        json.dump({"documents": documents, "updated_at": datetime.now().isoformat()}, f, indent=2)

def save_document(filename, content, doc_type="labels"):
    """Save a document to the documents folder and update index."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "public", "documents")
    os.makedirs(docs_dir, exist_ok=True)
    
    # Save file
    filepath = os.path.join(docs_dir, filename)
    if isinstance(content, bytes):
        with open(filepath, "wb") as f:
            f.write(content)
    else:
        with open(filepath, "w") as f:
            f.write(content)
    
    # Update index
    docs = get_documents()
    docs.insert(0, {
        "filename": filename,
        "type": doc_type,
        "created_at": datetime.now().isoformat(),
        "size": len(content)
    })
    save_documents_index(docs)
    return filepath

def delete_old_documents():
    """Delete documents older than 7 days."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "public", "documents")
    cutoff = datetime.now() - timedelta(days=7)
    
    docs = get_documents()
    fresh_docs = []
    for d in docs:
        try:
            doc_date = datetime.fromisoformat(d.get("created_at", ""))
            if doc_date >= cutoff:
                fresh_docs.append(d)
            else:
                # Delete the file
                filepath = os.path.join(docs_dir, d.get("filename", ""))
                if os.path.exists(filepath):
                    os.remove(filepath)
        except:
            fresh_docs.append(d)
    save_documents_index(fresh_docs)

@st.cache_data(ttl=30)
def get_tasks():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/tasks/tasks.json", timeout=5)
        return r.json().get("tasks", []) if r.ok else []
    except: return []

@st.cache_data(ttl=15)  # Refresh every 15 seconds
def get_batches():
    """Load batches from local file first, fallback to GitHub."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_file = os.path.join(script_dir, "public", "batches_history.json")
    
    # Try local file first (faster, real-time)
    if os.path.exists(local_file):
        try:
            with open(local_file, "r") as f:
                return json.load(f).get("batches", [])
        except:
            pass
    
    # Fallback to GitHub
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/batches_history.json", timeout=10)
        return r.json().get("batches", []) if r.ok else []
    except: return []

@st.cache_data(ttl=10)  # Short TTL to see new notes quickly
def get_notes():
    all_notes = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    notes_file = os.path.join(script_dir, "local_notes.json")
    
    # 1. Load from local file first (user-added notes)
    try:
        if os.path.exists(notes_file):
            with open(notes_file, "r") as f:
                local_notes = json.load(f)
            
            # Filter: keep only notes from last 2 days
            cutoff = datetime.now() - timedelta(days=2)
            fresh_notes = []
            for n in local_notes:
                try:
                    note_time = datetime.strptime(n.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                    if note_time >= cutoff:
                        fresh_notes.append(n)
                except:
                    fresh_notes.append(n)  # Keep if can't parse date
            
            # Save cleaned notes back if any were removed
            if len(fresh_notes) < len(local_notes):
                with open(notes_file, "w") as f:
                    json.dump(fresh_notes, f, indent=2)
            
            all_notes.extend(fresh_notes)
    except Exception as e:
        pass
    
    # 2. Load from GitHub (only if no local notes)
    if not all_notes:
        try:
            r = requests.get(f"{GITHUB_RAW_BASE}/notes/notes.json", timeout=5)
            if r.ok:
                all_notes.extend(r.json().get("notes", []))
        except: pass
    return all_notes

@st.cache_data(ttl=30)
def get_schedules():
    try:
        r = requests.get(f"{GITHUB_RAW_BASE}/schedules/schedules.json", timeout=5)
        return r.json().get("schedules", []) if r.ok else []
    except: return []

@st.cache_data(ttl=30)
def get_activity():
    """Load activity from local file with real-time timestamps."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    activity_file = os.path.join(script_dir, "local_activity.json")
    
    try:
        if os.path.exists(activity_file):
            with open(activity_file, "r") as f:
                activities = json.load(f)
            
            # Convert timestamps to "time ago" format
            now = datetime.now()
            for a in activities:
                try:
                    ts = datetime.fromisoformat(a.get("timestamp", ""))
                    diff = now - ts
                    mins = int(diff.total_seconds() / 60)
                    if mins < 1:
                        a["time"] = "Just now"
                    elif mins < 60:
                        a["time"] = f"{mins} min ago"
                    elif mins < 1440:
                        hrs = mins // 60
                        a["time"] = f"{hrs} hour{'s' if hrs > 1 else ''} ago"
                    else:
                        days = mins // 1440
                        a["time"] = f"{days} day{'s' if days > 1 else ''} ago"
                except:
                    a["time"] = "Recently"
            return activities
    except:
        pass
    return []

def add_activity(text, activity_type="green"):
    """Add a new activity entry (called by AI during automation)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    activity_file = os.path.join(script_dir, "local_activity.json")
    
    activities = []
    if os.path.exists(activity_file):
        try:
            with open(activity_file, "r") as f:
                activities = json.load(f)
        except:
            pass
    
    # Add new activity at the start
    activities.insert(0, {
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "type": activity_type
    })
    
    # Keep only last 20 activities
    activities = activities[:20]
    
    with open(activity_file, "w") as f:
        json.dump(activities, f, indent=2)

def get_shiprocket_credentials():
    """Get Shiprocket credentials - Streamlit secrets or hardcoded fallback."""
    # 1. Try Streamlit secrets (for Streamlit Cloud deployment)
    try:
        if "SHIPROCKET_EMAIL" in st.secrets and "SHIPROCKET_PASSWORD" in st.secrets:
            return st.secrets["SHIPROCKET_EMAIL"], st.secrets["SHIPROCKET_PASSWORD"]
    except:
        pass
    
    # 2. Fallback: hardcoded for internal use
    return "openclawd12@gmail.com", "Kluzo@1212"

def _load_cached_sr_data():
    """Load cached Shiprocket data from local file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_file = os.path.join(script_dir, "sr_cache.json")
    try:
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return json.load(f)
    except:
        pass
    return None

def _save_cached_sr_data(data):
    """Save Shiprocket data to local cache file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_file = os.path.join(script_dir, "sr_cache.json")
    try:
        with open(cache_file, "w") as f:
            json.dump(data, f)
    except:
        pass

@st.cache_data(ttl=60)  # Refresh every 60 seconds (sync with auto-refresh)
def get_shiprocket_data():
    """Fetch wallet balance and new order count from Shiprocket API."""
    email, pwd = get_shiprocket_credentials()
    
    # Try to load cached data first (for fast initial load)
    cached = _load_cached_sr_data()
    
    try:
        # Login to Shiprocket (shorter timeout)
        r = requests.post(f"{SHIPROCKET_API}/auth/login", json={"email": email, "password": pwd}, timeout=5)
        if not r.ok:
            return cached or {"wallet": 0, "new_orders": 0, "connected": False, "error": f"Login failed"}
        
        token = r.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get wallet balance (shorter timeout)
        wr = requests.get(f"{SHIPROCKET_API}/account/details/wallet-balance", headers=headers, timeout=5)
        wallet = float(wr.json().get("data", {}).get("balance_amount", 0)) if wr.ok else 0
        
        # Get actual NEW orders (shorter timeout)
        new_r = requests.get(f"{SHIPROCKET_API}/orders?filter=new&per_page=100", headers=headers, timeout=5)
        new_count = 0
        if new_r.ok:
            orders = new_r.json().get("data", [])
            new_count = sum(1 for o in orders if o.get("status") == "NEW")
        
        result = {"wallet": wallet, "new_orders": new_count, "connected": True}
        _save_cached_sr_data(result)  # Save for next time
        return result
    except Exception as e:
        # Return cached data if API fails
        return cached or {"wallet": 0, "new_orders": 0, "connected": False, "error": str(e)}

def download_latest_batch_labels():
    """Download labels from latest batch, sort by Courier+SKU, return ZIP."""
    import zipfile
    import tempfile
    import re
    from io import BytesIO
    from pypdf import PdfReader, PdfWriter
    
    with st.spinner("📥 Downloading and sorting labels..."):
        try:
            email, pwd = get_shiprocket_credentials()
            
            # Login
            auth_r = requests.post(f"{SHIPROCKET_API}/auth/login", json={"email": email, "password": pwd}, timeout=10)
            if not auth_r.ok:
                st.error("❌ Login failed")
                return
            
            token = auth_r.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get today's shipments (latest batch)
            today = datetime.now().strftime("%Y-%m-%d")
            ship_r = requests.get(f"{SHIPROCKET_API}/shipments", headers=headers, params={"per_page": 100}, timeout=30)
            
            if not ship_r.ok:
                st.error("❌ Failed to fetch shipments")
                return
            
            shipments = ship_r.json().get("data", [])
            today_shipments = [s for s in shipments if s.get("created_at", "")[:10] == today or today in str(s.get("created_at", ""))]
            
            if not today_shipments:
                st.warning("⚠️ No shipments found for today")
                return
            
            st.info(f"📦 Found {len(today_shipments)} shipments from today")
            
            # Get shipment IDs
            shipment_ids = [str(s.get("id")) for s in today_shipments if s.get("id")]
            
            # Generate combined label PDF
            label_r = requests.post(
                f"{SHIPROCKET_API}/courier/generate/label",
                headers=headers,
                json={"shipment_id": shipment_ids},
                timeout=60
            )
            
            if not label_r.ok:
                st.error(f"❌ Label generation failed: {label_r.status_code}")
                return
            
            label_url = label_r.json().get("label_url", "")
            if not label_url:
                st.error("❌ No label URL returned")
                return
            
            # Download the PDF
            pdf_r = requests.get(label_url, timeout=60)
            if not pdf_r.ok:
                st.error("❌ Failed to download PDF")
                return
            
            # Sort labels by Courier + SKU
            pdf_data = BytesIO(pdf_r.content)
            reader = PdfReader(pdf_data)
            
            # Group pages by courier
            courier_pages = {}
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                
                # Extract courier
                courier = "Unknown"
                for c in ["Ekart", "Delhivery", "Xpressbees", "BlueDart", "DTDC", "Shadowfax", "Ecom"]:
                    if c.lower() in text.lower():
                        courier = c
                        break
                
                # Extract SKU
                sku_match = re.search(r'SKU[:\s]*([A-Za-z0-9\-_]+)', text, re.IGNORECASE)
                sku = sku_match.group(1) if sku_match else "Unknown"
                
                key = f"{courier}_{sku}"
                if key not in courier_pages:
                    courier_pages[key] = []
                courier_pages[key].append(page)
            
            # Create ZIP with sorted PDFs
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for key, pages in courier_pages.items():
                    writer = PdfWriter()
                    for p in pages:
                        writer.add_page(p)
                    
                    pdf_buffer = BytesIO()
                    writer.write(pdf_buffer)
                    pdf_buffer.seek(0)
                    
                    filename = f"{today}_{key}.pdf"
                    zf.writestr(filename, pdf_buffer.read())
            
            zip_buffer.seek(0)
            zip_content = zip_buffer.getvalue()
            
            # Auto-save to Documents
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            zip_filename = f"{timestamp}_labels_sorted.zip"
            save_document(zip_filename, zip_content, doc_type="labels")
            
            # Provide download
            st.download_button(
                label=f"📥 Download Labels ZIP ({len(courier_pages)} files)",
                data=zip_content,
                file_name=zip_filename,
                mime="application/zip"
            )
            
            st.success(f"✅ Sorted {len(reader.pages)} labels into {len(courier_pages)} groups!")
            st.info(f"📁 Saved to Documents: {zip_filename}")
            
            # Show breakdown
            for key in sorted(courier_pages.keys()):
                st.caption(f"  • {key}: {len(courier_pages[key])} labels")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

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

# === LOAD KLUZO LOGO ===
import base64
import os

logo_b64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "assets", "kluzo-logo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" class="avatar-img" alt="Kluzo">'
else:
    logo_html = '<div class="avatar">😎</div>'


# === SIDEBAR ===
with st.sidebar:
    # Profile with actual Kluzo logo
    st.markdown(f"""
    <div class="profile-box">
        {logo_html}
        <div class="profile-name">Kluzo</div>
        <div class="profile-status"><span class="status-dot"></span> AI Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Primary action
    if st.button("🚀 Ship Orders Now", use_container_width=True, type="primary"):
        st.session_state.ship_now = True
    
    st.markdown("---")
    
    # Debug: Show connection status
    if sr_data.get('error'):
        st.error(f"⚠️ {sr_data['error']}")
    elif not sr_data.get('connected'):
        st.warning("⚠️ Not connected to Shiprocket")
    
    # Stats cards
    st.markdown(f"""
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
        if st.button("📥", help="Download Latest Batch Labels (Sorted by Courier+SKU)"):
            download_latest_batch_labels()
    
    # Connection status
    status_color = "🟢" if sr_data['connected'] else "🔴"
    st.caption(f"{status_color} Shiprocket API")
    
    st.markdown("---")
    
    # === QUICK AWB LOOKUP ===
    st.markdown("**🔍 Quick AWB Lookup**")
    awb_lookup = st.text_input(
        "AWB",
        placeholder="Enter AWB number...",
        label_visibility="collapsed",
        key="quick_awb"
    )
    
    if awb_lookup:
        with st.spinner("Tracking..."):
            try:
                # Get token
                from dotenv import load_dotenv
                load_dotenv("/Users/klaus/.openclaw/workspace/shiprocket-credentials.env")
                import os
                email = os.getenv('SHIPROCKET_EMAIL')
                pwd = os.getenv('SHIPROCKET_PASSWORD')
                
                auth_r = requests.post(
                    f"{SHIPROCKET_API}/auth/login",
                    json={"email": email, "password": pwd},
                    timeout=10
                )
                
                if auth_r.ok:
                    token = auth_r.json().get("token")
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Track AWB
                    track_r = requests.get(
                        f"{SHIPROCKET_API}/courier/track/awb/{awb_lookup}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if track_r.ok:
                        data = track_r.json()
                        tracking = data.get("tracking_data", {})
                        
                        # Get status
                        current_status = tracking.get("shipment_status_id", 0)
                        status_text = tracking.get("shipment_status", "Unknown")
                        
                        # Status colors
                        if current_status >= 7:  # Delivered
                            st.success(f"✅ **{status_text}**")
                        elif current_status >= 4:  # In transit
                            st.info(f"🚚 **{status_text}**")
                        elif current_status >= 1:  # Picked up
                            st.warning(f"📦 **{status_text}**")
                        else:
                            st.info(f"📋 **{status_text}**")
                        
                        # Show details
                        courier = tracking.get("courier_name", "N/A")
                        etd = tracking.get("etd", "N/A")
                        
                        st.caption(f"🚚 {courier}")
                        if etd and etd != "N/A":
                            st.caption(f"📅 ETA: {etd}")
                        
                        # Show latest activity
                        activities = tracking.get("shipment_track_activities", [])
                        if activities:
                            latest = activities[0]
                            st.caption(f"📍 {latest.get('activity', 'N/A')[:50]}")
                    else:
                        st.error("❌ AWB not found")
                else:
                    st.error("❌ Auth failed")
            except Exception as e:
                st.error(f"❌ Error: {str(e)[:30]}")


# === HEADER ===
st.markdown(f"""
<div class="header-bar">
    <div class="header-left">
        <div class="header-title">Kluzo <span class="online-dot"></span></div>
        <div class="tab-nav" id="tabs"></div>
    </div>
    <div class="header-right">
        <span>Last sync: {last_sync}</span>
        <span><span class="kbd">?</span> Shortcuts</span>
        <img src="data:image/jpeg;base64,{logo_b64 if 'logo_b64' in dir() else ''}" class="header-logo" alt="K">
    </div>
</div>
""", unsafe_allow_html=True)

# === PAGE SELECTOR ===
# Check if redirected from Ship workflow
default_page = "📁 Documents" if st.session_state.get("go_to_documents") else "🏠 Dashboard"
if st.session_state.get("go_to_documents"):
    st.session_state.go_to_documents = False

page = st.radio("", ["🏠 Dashboard", "📁 Documents", "⚙️ Settings"], horizontal=True, label_visibility="collapsed", index=0 if default_page == "🏠 Dashboard" else 1)

if page == "📁 Documents":
    # === DOCUMENTS PAGE ===
    st.markdown("### 📁 Documents (Last 7 Days)")
    st.markdown("All your downloaded labels, manifests, and files are stored here.")
    st.markdown("---")
    
    # Load and display documents
    all_docs = get_documents()
    
    if all_docs:
        for i, doc in enumerate(all_docs):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                doc_type = doc.get("type", "file")
                icon = "🏷️" if doc_type == "labels" else "📄" if doc_type == "manifest" else "📁"
                st.markdown(f"**{icon} {doc.get('filename', 'Unknown')}**")
                size_kb = doc.get("size", 0) / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                created = doc.get("created_at", "")[:16].replace("T", " ")
                st.caption(f"📅 {created} • 💾 {size_str}")
            with col2:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                filepath = os.path.join(script_dir, "public", "documents", doc.get("filename", ""))
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        st.download_button(
                            label="📥 Download",
                            data=f.read(),
                            file_name=doc.get("filename", "download"),
                            mime="application/octet-stream",
                            key=f"doc_download_{i}",
                            use_container_width=True
                        )
            with col3:
                if st.button("🗑️", key=f"doc_delete_{i}", help="Delete this document"):
                    # Delete document
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    docs = get_documents()
                    docs = [d for d in docs if d.get("filename") != doc.get("filename")]
                    save_documents_index(docs)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No documents yet. Run 'Ship them buddy' or download labels to see files here!")
    
    # Manual cleanup button
    if st.button("🧹 Clean up old files", help="Delete files older than 7 days"):
        delete_old_documents()
        st.success("✅ Cleanup complete!")
        st.rerun()
    
    st.stop()  # Stop here for Documents page

if page == "⚙️ Settings":
    # === SETTINGS PAGE ===
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    
    # Load schedules
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sched_file = os.path.join(script_dir, "public", "schedules", "schedules.json")
    
    if os.path.exists(sched_file):
        with open(sched_file, "r") as f:
            sched_data = json.load(f)
    else:
        sched_data = {"schedules": [], "updated_at": ""}
    
    st.markdown("#### 📅 Scheduled Batches")
    st.caption("Configure automatic shipping schedules. When triggered, orders will be shipped, labels sorted, and you'll be notified.")
    
    for i, sched in enumerate(sched_data.get("schedules", [])):
        with st.expander(f"{'🟢' if sched.get('enabled') else '🔴'} {sched.get('name', 'Schedule')}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=sched.get("name", ""), key=f"sched_name_{i}")
                new_time = st.time_input("Time", value=datetime.strptime(sched.get("time", "09:00"), "%H:%M").time(), key=f"sched_time_{i}")
            with col2:
                new_enabled = st.checkbox("Enabled", value=sched.get("enabled", True), key=f"sched_enabled_{i}")
                days_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                new_days = st.multiselect("Days", options=days_options, default=sched.get("days", []), key=f"sched_days_{i}")
            
            if st.button("💾 Save", key=f"save_sched_{i}", use_container_width=True):
                sched_data["schedules"][i]["name"] = new_name
                sched_data["schedules"][i]["time"] = new_time.strftime("%H:%M")
                sched_data["schedules"][i]["days"] = new_days
                sched_data["schedules"][i]["enabled"] = new_enabled
                sched_data["updated_at"] = datetime.now().isoformat()
                
                with open(sched_file, "w") as f:
                    json.dump(sched_data, f, indent=2)
                st.success(f"✅ {new_name} saved!")
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### ➕ Add New Schedule")
    with st.form("new_schedule"):
        col1, col2 = st.columns(2)
        with col1:
            add_name = st.text_input("Schedule Name", placeholder="e.g., Night Batch")
            add_time = st.time_input("Time", value=datetime.strptime("21:00", "%H:%M").time())
        with col2:
            add_enabled = st.checkbox("Enabled", value=True)
            add_days = st.multiselect("Days", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        if st.form_submit_button("➕ Add Schedule", use_container_width=True):
            if add_name:
                new_sched = {
                    "id": f"sched-{len(sched_data.get('schedules', [])) + 1:03d}",
                    "name": add_name,
                    "time": add_time.strftime("%H:%M"),
                    "days": add_days,
                    "action": "Ship All Orders",
                    "enabled": add_enabled,
                    "last_run": None
                }
                sched_data["schedules"].append(new_sched)
                sched_data["updated_at"] = datetime.now().isoformat()
                
                with open(sched_file, "w") as f:
                    json.dump(sched_data, f, indent=2)
                st.success(f"✅ {add_name} added!")
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### 📱 WhatsApp Notifications")
    st.info("🔜 Coming soon! Connect your WhatsApp group to receive batch notifications.")
    
    st.stop()  # Stop here for Settings page

# === DASHBOARD PAGE ===
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
total_today = sum(b.get("total_orders", 0) for b in today_batches)
st.markdown(f"""
<div class="stats-bar animate-slide">
    <div class="stat-item">
        <div class="stat-value">📦 {today_shipped}</div>
        <div class="stat-label">Shipped Today</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">📋 {sr_data['new_orders']}</div>
        <div class="stat-label">New Orders</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">✅ {success_rate:.0f}%</div>
        <div class="stat-label">Success Rate</div>
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


# === KANBAN BOARD (Functional) ===

# Task management functions
def load_local_tasks():
    """Load tasks from local file first, then GitHub as fallback.
    Returns None if no file exists (first run), returns [] if user deleted all tasks."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tasks_file = os.path.join(script_dir, "local_tasks.json")
    
    # 1. Try local file first - this is authoritative if it exists
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            pass
    
    # 2. No local file = first run, return None to trigger defaults
    return None

def save_local_tasks(tasks):
    """Save tasks to local file and GitHub public folder."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save to local file
    local_file = os.path.join(script_dir, "local_tasks.json")
    with open(local_file, "w") as f:
        json.dump(tasks, f, indent=2)
    
    # Also save to public/tasks/tasks.json (for GitHub sync)
    public_file = os.path.join(script_dir, "public", "tasks", "tasks.json")
    os.makedirs(os.path.dirname(public_file), exist_ok=True)
    with open(public_file, "w") as f:
        json.dump({"tasks": tasks}, f, indent=2)

# Load tasks
if 'kanban_tasks' not in st.session_state:
    loaded_tasks = load_local_tasks()
    # Only add defaults if NO local file exists (None = first run)
    # Empty list [] means user deleted all tasks - respect that!
    if loaded_tasks is None:
        st.session_state.kanban_tasks = [
            {"id": 1, "title": "Check inventory levels", "status": "todo", "priority": "medium", "category": "shiprocket", "desc": ""},
            {"id": 2, "title": "Update courier priorities", "status": "todo", "priority": "low", "category": "other", "desc": ""},
            {"id": 3, "title": "Ship morning batch", "status": "done", "priority": "high", "category": "shiprocket", "desc": ""},
        ]
        save_local_tasks(st.session_state.kanban_tasks)  # Create the file
    else:
        st.session_state.kanban_tasks = loaded_tasks

# Priority colors
PRIORITY_COLORS = {"high": "🔴", "medium": "🟡", "low": "🟢"}
PRIORITY_DOTS = {"high": "red", "medium": "orange", "low": "green"}
STATUS_NAMES = {"todo": "TO DO", "in_progress": "IN PROGRESS", "done": "DONE", "archive": "ARCHIVE"}

# Filter tasks by status
kanban_todo = [t for t in st.session_state.kanban_tasks if t.get("status") == "todo"]
kanban_doing = [t for t in st.session_state.kanban_tasks if t.get("status") == "in_progress"]
kanban_done = [t for t in st.session_state.kanban_tasks if t.get("status") == "done"]
kanban_archive = [t for t in st.session_state.kanban_tasks if t.get("status") == "archive"]

# Add Task Button
add_col, spacer = st.columns([1, 4])
with add_col:
    if st.button("➕ Add Task", use_container_width=True, type="primary"):
        st.session_state.show_add_task = True

# Add Task Form
if st.session_state.get("show_add_task"):
    with st.container():
        st.markdown("### ➕ New Task")
        new_title = st.text_input("Title", key="new_task_title", placeholder="Task title...")
        col_p, col_c = st.columns(2)
        with col_p:
            new_priority = st.selectbox("Priority", ["high", "medium", "low"], index=1, format_func=lambda x: f"{PRIORITY_COLORS[x]} {x.title()}", key="new_task_priority")
        with col_c:
            new_category = st.selectbox("Category", ["shiprocket", "other"], key="new_task_category")
        new_desc = st.text_area("Description (optional)", key="new_task_desc", placeholder="Task details...")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("💾 Save Task", use_container_width=True, type="primary"):
                if new_title:
                    new_id = max([t.get("id", 0) for t in st.session_state.kanban_tasks] + [0]) + 1
                    st.session_state.kanban_tasks.append({
                        "id": new_id, "title": new_title, "status": "todo",
                        "priority": new_priority, "category": new_category, "desc": new_desc
                    })
                    save_local_tasks(st.session_state.kanban_tasks)
                    st.session_state.show_add_task = False
                    st.toast("✅ Task added!", icon="📋")
                    st.rerun()
        with btn_col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_add_task = False
                st.rerun()
        st.markdown("---")

# Kanban Columns with custom styling
st.markdown("""
<style>
.kanban-header-custom {
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.kanban-todo { background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(234, 88, 12, 0.1)); border: 1px solid #f97316; color: #fb923c; }
.kanban-progress { background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.1)); border: 1px solid #3b82f6; color: #60a5fa; }
.kanban-done { background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.1)); border: 1px solid #22c55e; color: #4ade80; }
.kanban-archive { background: linear-gradient(135deg, rgba(107, 114, 128, 0.2), rgba(75, 85, 99, 0.1)); border: 1px solid #6b7280; color: #9ca3af; }
.task-card {
    background: rgba(15, 20, 25, 0.9);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}
.task-card:hover {
    border-color: #58a6ff;
    box-shadow: 0 4px 15px rgba(88, 166, 255, 0.15);
}
.task-title { color: #e6edf3; font-size: 0.95rem; font-weight: 500; margin-bottom: 8px; }
.task-meta { display: flex; gap: 10px; align-items: center; }
.task-category { font-size: 0.75rem; padding: 3px 8px; border-radius: 12px; }
.cat-shiprocket { background: rgba(147, 51, 234, 0.2); color: #a78bfa; }
.cat-other { background: rgba(107, 114, 128, 0.2); color: #9ca3af; }
.priority-dot { width: 10px; height: 10px; border-radius: 50%; }
.pri-high { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.5); }
.pri-medium { background: #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.5); }
.pri-low { background: #22c55e; box-shadow: 0 0 8px rgba(34, 197, 94, 0.5); }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")

def build_task_html(task):
    """Build HTML for a single task card."""
    priority = task.get("priority", "medium")
    pri_dot = {"high": "red", "medium": "orange", "low": "green"}.get(priority, "orange")
    return f'<div class="task"><div class="task-left"><div class="t-dot {pri_dot}"></div><span class="t-text">{task.get("title", "Task")}</span></div><div class="task-right"><span class="task-btn">📁</span><span class="task-btn delete">●</span></div></div>'

def build_kanban_column(col_type, title, tasks, dot_class, empty_msg):
    """Build complete HTML for a kanban column."""
    tasks_html = ""
    if tasks:
        for t in tasks[:10]:
            tasks_html += build_task_html(t)
        if len(tasks) > 10:
            tasks_html += f'<div class="empty-state">+ {len(tasks) - 10} more</div>'
    else:
        tasks_html = f'<div class="empty-state">{empty_msg}</div>'
    
    return f'<div class="kanban-col {col_type}"><div class="kanban-header"><span class="kanban-header-pill {col_type}"><span class="k-dot {dot_class}"></span> {title} ({len(tasks)})</span></div><div class="kanban-tasks">{tasks_html}</div></div>'

with c1:
    st.markdown(build_kanban_column("todo", "TO DO", kanban_todo, "orange", "✨ No pending tasks"), unsafe_allow_html=True)

with c2:
    st.markdown(build_kanban_column("doing", "IN PROGRESS", kanban_doing, "blue", "🎯 No tasks in progress"), unsafe_allow_html=True)

with c3:
    st.markdown(build_kanban_column("done", "DONE", kanban_done, "green", "No completed tasks"), unsafe_allow_html=True)

# === ACTIVITY + DOWNLOADS SECTION ===
st.markdown("<br>", unsafe_allow_html=True)
act_col, dl_col = st.columns(2, gap="medium")

with act_col:
    # Build activity HTML
    real_activities = get_activity()
    if not real_activities:
        real_activities = [{"text": "No recent activity", "time": "—", "type": "blue"}]
    
    activity_items = ""
    for a in real_activities[:8]:
        activity_items += f'<div class="activity-item"><span class="activity-dot {a.get("type", "blue")}"></span><div class="activity-content"><div class="activity-text">{a.get("text", "")}</div><div class="activity-time">{a.get("time", "")}</div></div></div>'
    
    activity_html = f'<div class="section-box"><div class="section-title">⚡ Recent Activity</div><div class="section-content">{activity_items}</div></div>'
    st.markdown(activity_html, unsafe_allow_html=True)

with dl_col:
    # Build downloads history HTML
    all_docs = get_documents()
    
    download_items = ""
    if all_docs:
        for d in all_docs[:8]:
            doc_type = d.get("type", "file")
            icon = "🏷️" if doc_type == "labels" else "📄" if doc_type == "manifest" else "📁"
            size_kb = d.get("size", 0) / 1024
            size_str = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb/1024:.1f}MB"
            created = d.get("created_at", "")[:16].replace("T", " ")
            download_items += f'<div class="activity-item"><span class="activity-dot green"></span><div class="activity-content"><div class="activity-text">{icon} {d.get("filename", "Unknown")}</div><div class="activity-time">{created} • {size_str}</div></div></div>'
    else:
        download_items = '<div class="empty-state">No downloads yet</div>'
    
    downloads_html = f'<div class="section-box"><div class="section-title">📥 Downloads History</div><div class="section-content">{download_items}</div></div>'
    st.markdown(downloads_html, unsafe_allow_html=True)


# === BOTTOM SECTIONS: Schedules + Notes ===
st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns(2, gap="medium")

with b1:
    # Scheduled Deliverables with toggles
    st.markdown('<div class="section-box"><div class="section-title">📅 Scheduled Deliverables</div></div>', unsafe_allow_html=True)
    
    # Load local schedules file for editing
    sched_dir = os.path.dirname(os.path.abspath(__file__))
    sched_file = os.path.join(sched_dir, "public", "schedules", "schedules.json")
    try:
        with open(sched_file, "r") as f:
            local_schedules = json.load(f)
    except:
        local_schedules = {"schedules": schedules, "updated_at": ""}
    
    schedule_changed = False
    for i, s in enumerate(local_schedules.get("schedules", [])[:5]):
        days = ", ".join(s.get("days", [])[:3])
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"""
                <div style="padding: 8px 0;">
                    <div style="font-weight: 600; color: #fff;">{s.get("name","")}</div>
                    <div style="font-size: 12px; color: #888;">{s.get("time","")} • {days}</div>
                </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            new_state = st.toggle("", value=s.get("active", True), key=f"sched_toggle_{i}", label_visibility="collapsed")
            if new_state != s.get("active", True):
                local_schedules["schedules"][i]["active"] = new_state
                schedule_changed = True
    
    # Save if changed
    if schedule_changed:
        local_schedules["updated_at"] = datetime.now().isoformat()
        with open(sched_file, "w") as f:
            json.dump(local_schedules, f, indent=2)
        st.rerun()

with b2:
    # Build notes HTML in one block with scrollable content
    note_items = ""
    for n in notes[:10]:  # Show more notes (scrollable)
        cls = "ai" if n.get("type") == "ai" else ""
        icon = "🤖" if n.get("type") == "ai" else "👤"
        content = n.get("content", "")[:100]
        note_items += f'<div class="note {cls}"><div class="note-text">{icon} {content}...</div><div class="note-time">{n.get("timestamp","")}</div></div>'
    
    notes_html = f'<div class="section-box"><div class="section-title">📝 Notes</div><div class="section-content">{note_items}</div></div>'
    st.markdown(notes_html, unsafe_allow_html=True)
    
    # Add Note button
    if st.button("➕ Add Note", use_container_width=True):
        st.session_state.show_add_note = True
    
    # Add Note form
    if st.session_state.get("show_add_note"):
        new_note = st.text_area("New Note", placeholder="Type your note here...", key="new_note_input")
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("💾 Save", use_container_width=True, type="primary"):
                if new_note:
                    # Save note to local file
                    try:
                        import os
                        notes_file = os.path.join(os.path.dirname(__file__), "local_notes.json")
                        existing = []
                        if os.path.exists(notes_file):
                            with open(notes_file, "r") as f:
                                existing = json.load(f)
                        new_entry = {
                            "content": new_note,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "type": "user"
                        }
                        existing.insert(0, new_entry)  # Add to top
                        with open(notes_file, "w") as f:
                            json.dump(existing, f, indent=2)
                        st.toast("✅ Note saved!", icon="📝")
                        st.cache_data.clear()  # Clear cache to reload notes
                    except Exception as e:
                        st.error(f"Failed to save: {e}")
                    st.session_state.show_add_note = False
                    st.rerun()
        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_add_note = False
                st.rerun()


# === SHIP NOW HANDLER (Full Workflow) ===
if st.session_state.get("ship_now"):
    st.session_state.ship_now = False
    
    import zipfile
    import re
    from io import BytesIO
    from pypdf import PdfReader, PdfWriter
    
    progress = st.progress(0, text="🚀 Starting shipping workflow...")
    status = st.empty()
    
    try:
        email, pwd = get_shiprocket_credentials()
        
        # Step 1: Login
        status.info("🔐 Logging in to Shiprocket...")
        progress.progress(10, text="🔐 Logging in...")
        auth_r = requests.post(f"{SHIPROCKET_API}/auth/login", json={"email": email, "password": pwd}, timeout=15)
        if not auth_r.ok:
            st.error("❌ Login failed")
            st.stop()
        token = auth_r.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get NEW orders
        status.info("📦 Fetching NEW orders...")
        progress.progress(20, text="📦 Fetching orders...")
        orders_r = requests.get(f"{SHIPROCKET_API}/orders", headers=headers, params={"per_page": 200}, timeout=30)
        orders = orders_r.json().get("data", [])
        new_orders = [o for o in orders if o.get("status") == "NEW"]
        
        if not new_orders:
            status.warning("📭 No NEW orders to ship!")
            progress.progress(100, text="✅ Complete - No orders")
            st.stop()
        
        status.info(f"📦 Found {len(new_orders)} NEW orders")
        
        # Step 3: Ship each order
        shipped_ids = []
        shipped_awbs = []
        progress.progress(30, text=f"🚚 Shipping {len(new_orders)} orders...")
        
        for i, order in enumerate(new_orders):
            try:
                shipments = order.get("shipments", [])
                if shipments:
                    shipment_id = shipments[0].get("id")
                    if shipment_id:
                        awb_r = requests.post(
                            f"{SHIPROCKET_API}/courier/assign/awb",
                            headers=headers,
                            json={"shipment_id": shipment_id},
                            timeout=15
                        )
                        if awb_r.ok and awb_r.json().get("awb_assign_status") == 1:
                            awb = awb_r.json().get("response", {}).get("data", {}).get("awb_code", "")
                            shipped_ids.append(shipment_id)
                            shipped_awbs.append(awb)
            except:
                pass
            progress.progress(30 + int((i+1)/len(new_orders)*20), text=f"🚚 Shipped {i+1}/{len(new_orders)}...")
        
        status.info(f"✅ Shipped {len(shipped_ids)} orders!")
        
        if not shipped_ids:
            status.warning("⚠️ No orders were shipped")
            progress.progress(100, text="✅ Complete")
            st.stop()
        
        # Step 4: Generate labels
        progress.progress(55, text="🏷️ Generating labels...")
        status.info("🏷️ Generating labels...")
        label_r = requests.post(
            f"{SHIPROCKET_API}/courier/generate/label",
            headers=headers,
            json={"shipment_id": [str(sid) for sid in shipped_ids]},
            timeout=60
        )
        
        label_url = label_r.json().get("label_url", "") if label_r.ok else ""
        
        # Step 5: Download and sort labels
        progress.progress(65, text="📥 Downloading labels...")
        if label_url:
            pdf_r = requests.get(label_url, timeout=60)
            if pdf_r.ok:
                status.info("🔄 Sorting labels by Courier + SKU...")
                progress.progress(75, text="🔄 Sorting labels...")
                
                pdf_data = BytesIO(pdf_r.content)
                reader = PdfReader(pdf_data)
                
                # Group by Courier + SKU
                courier_pages = {}
                for page in reader.pages:
                    text = page.extract_text() or ""
                    courier = "Unknown"
                    for c in ["Ekart", "Delhivery", "Xpressbees", "BlueDart", "DTDC", "Shadowfax", "Ecom"]:
                        if c.lower() in text.lower():
                            courier = c
                            break
                    sku_match = re.search(r'SKU[:\s]*([A-Za-z0-9\-_]+)', text, re.IGNORECASE)
                    sku = sku_match.group(1) if sku_match else "Unknown"
                    key = f"{courier}_{sku}"
                    if key not in courier_pages:
                        courier_pages[key] = []
                    courier_pages[key].append(page)
                
                # Create ZIP
                zip_buffer = BytesIO()
                today = datetime.now().strftime("%Y-%m-%d")
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for key, pages in courier_pages.items():
                        writer = PdfWriter()
                        for p in pages:
                            writer.add_page(p)
                        pdf_buffer = BytesIO()
                        writer.write(pdf_buffer)
                        pdf_buffer.seek(0)
                        zf.writestr(f"{today}_{key}.pdf", pdf_buffer.read())
                
                zip_buffer.seek(0)
                zip_content = zip_buffer.getvalue()
                
                # Save to Documents
                progress.progress(85, text="💾 Saving to Documents...")
                zip_filename = f"{timestamp}_labels_sorted.zip"
                save_document(zip_filename, zip_content, doc_type="labels")
        
        # Step 6: Schedule Pickup (one by one for reliability)
        progress.progress(87, text="📅 Scheduling pickup...")
        status.info("📅 Scheduling pickup for shipments...")
        pickup_success = 0
        for sid in shipped_ids:
            try:
                pickup_r = requests.post(
                    f"{SHIPROCKET_API}/courier/generate/pickup",
                    headers=headers,
                    json={"shipment_id": [str(sid)]},
                    timeout=15
                )
                if pickup_r.ok:
                    pickup_success += 1
            except:
                pass
        status.info(f"📅 Pickup scheduled for {pickup_success}/{len(shipped_ids)} shipments")
        
        # Step 7: Generate manifest
        progress.progress(92, text="📄 Generating manifest...")
        status.info("📄 Generating manifest...")
        manifest_r = requests.post(
            f"{SHIPROCKET_API}/manifests/generate",
            headers=headers,
            json={"shipment_id": [str(sid) for sid in shipped_ids]},
            timeout=30
        )
        
        manifest_saved = False
        if manifest_r.ok:
            manifest_url = manifest_r.json().get("manifest_url", "")
            if manifest_url:
                manifest_pdf = requests.get(manifest_url, timeout=30)
                if manifest_pdf.ok:
                    manifest_filename = f"{timestamp}_manifest.pdf"
                    save_document(manifest_filename, manifest_pdf.content, doc_type="manifest")
        
        # Step 7: Update batch history
        progress.progress(95, text="📊 Updating records...")
        batch_data = {
            "timestamp": datetime.now().isoformat(),
            "date": today,
            "time": datetime.now().strftime("%I:%M %p"),
            "display_time": datetime.now().strftime("%I:%M %p"),
            "total_orders": len(new_orders),
            "shipped": len(shipped_ids),
            "failed": len(new_orders) - len(shipped_ids),
            "awbs": shipped_awbs[:10],
            "source": "ship_orders_now"
        }
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file = os.path.join(script_dir, "public", "batches_history.json")
        with open(batch_file, "r") as f:
            batches_data = json.load(f)
        batches_data["batches"].insert(0, batch_data)
        with open(batch_file, "w") as f:
            json.dump(batches_data, f, indent=2)
        
        # Step 8: Add activity
        with open(os.path.join(script_dir, "local_activity.json"), "r") as f:
            activities = json.load(f)
        activities.insert(0, {
            "text": f"🚀 Shipped {len(shipped_ids)} orders, pickup scheduled, labels sorted!",
            "timestamp": datetime.now().isoformat(),
            "type": "green"
        })
        with open(os.path.join(script_dir, "local_activity.json"), "w") as f:
            json.dump(activities[:20], f, indent=2)
        
        # Complete!
        progress.progress(100, text="✅ Complete!")
        status.success(f"🎉 Shipped {len(shipped_ids)} orders! Pickup scheduled, manifest generated, labels sorted!")
        st.balloons()
        
        # Redirect to Documents page
        st.session_state.go_to_documents = True
        st.cache_data.clear()
        st.rerun()
        
    except Exception as e:
        status.error(f"❌ Error: {str(e)}")
        progress.progress(100, text="❌ Failed")


# === KEYBOARD SHORTCUTS HINT ===
st.markdown("""
<div class="kbd-hint">
    Press <span class="kbd">?</span> for shortcuts
</div>
""", unsafe_allow_html=True)


# === AUTO REFRESH (every 60 seconds) ===
# Using meta refresh tag (works in Streamlit)
st.markdown(
    '<meta http-equiv="refresh" content="60">',
    unsafe_allow_html=True
)
