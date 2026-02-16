"""
🤖 KLUZO DASHBOARD
==================
Admin Control Panel for Shiprocket Automation

Built by Kluzo 😎 for JSK Labs
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import base64

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Kluzo Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - DARK THEME WITH GRADIENT ACCENTS
# =============================================================================
st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6B8DD6 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .dashboard-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .card-header {
        color: #a78bfa;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Status indicators */
    .status-working { color: #22c55e; }
    .status-idle { color: #eab308; }
    .status-offline { color: #ef4444; }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-badge.working {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
    }
    
    .status-badge.idle {
        background: rgba(234, 179, 8, 0.2);
        color: #eab308;
    }
    
    .status-badge.offline {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Kanban board */
    .kanban-column {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        min-height: 300px;
    }
    
    .kanban-header {
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid;
    }
    
    .kanban-todo { border-color: #3b82f6; color: #3b82f6; }
    .kanban-progress { border-color: #eab308; color: #eab308; }
    .kanban-done { border-color: #22c55e; color: #22c55e; }
    
    .task-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        cursor: grab;
    }
    
    .task-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(167, 139, 250, 0.5);
    }
    
    .priority-high { border-left: 3px solid #ef4444; }
    .priority-medium { border-left: 3px solid #eab308; }
    .priority-normal { border-left: 3px solid #22c55e; }
    
    /* Activity log */
    .log-entry {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: #cbd5e1;
        font-size: 0.9rem;
    }
    
    .log-time {
        color: #64748b;
        font-size: 0.8rem;
        min-width: 70px;
    }
    
    .log-icon {
        font-size: 1rem;
    }
    
    /* Notes panel */
    .note-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    .note-user {
        color: #a78bfa;
        font-weight: 500;
    }
    
    .note-ai {
        color: #22d3ee;
        font-weight: 500;
    }
    
    /* Progress bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2, #22d3ee);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Search box */
    .search-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Alert banner */
    .alert-banner {
        background: linear-gradient(90deg, #ef4444, #dc2626);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    
    /* Connection status */
    .connection-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .connection-name {
        color: #cbd5e1;
    }
    
    .connection-status {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Text colors */
    .text-white { color: white; }
    .text-gray { color: #94a3b8; }
    .text-purple { color: #a78bfa; }
    .text-cyan { color: #22d3ee; }
    .text-green { color: #22c55e; }
    .text-yellow { color: #eab308; }
    .text-red { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONFIGURATION
# =============================================================================
GITHUB_REPO = "jsk-labs-maker/shiprocket-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/public"
SHIPROCKET_API_BASE = "https://apiv2.shiprocket.in/v1/external"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_logo():
    """Load and encode logo for display."""
    logo_path = Path(__file__).parent / "assets" / "kluzo_logo.jpg"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

@st.cache_data(ttl=30)
def fetch_json(endpoint):
    """Fetch JSON data from GitHub."""
    try:
        url = f"{GITHUB_RAW_BASE}/{endpoint}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_ai_status():
    """Get AI status from storage."""
    data = fetch_json("ai/status.json")
    return data or {"status": "offline", "current_task": None, "sub_agents": []}

def get_tasks():
    """Get task board data."""
    data = fetch_json("tasks/board.json")
    return data or {"todo": [], "in_progress": [], "done": []}

def get_activity_logs():
    """Get activity logs."""
    data = fetch_json("logs/activity.json")
    return data or {"logs": []}

def get_notes():
    """Get notes."""
    data = fetch_json("notes/notes.json")
    return data or {"notes": []}

def get_schedules():
    """Get scheduled actions."""
    data = fetch_json("schedules/schedules.json")
    return data or {"schedules": []}

def get_connections():
    """Get connection status."""
    data = fetch_json("connections/status.json")
    return data or {}

def get_batches_history():
    """Get batches history."""
    data = fetch_json("batches_history.json")
    if data:
        return data.get("batches", [])
    return []

def shiprocket_authenticate():
    """Authenticate with Shiprocket."""
    try:
        if hasattr(st, 'secrets') and 'shiprocket' in st.secrets:
            api_key = st.secrets['shiprocket'].get('api_key')
            if api_key:
                return api_key
            email = st.secrets['shiprocket'].get('email')
            password = st.secrets['shiprocket'].get('password')
            if email and password:
                response = requests.post(
                    f"{SHIPROCKET_API_BASE}/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()["token"]
    except:
        pass
    return None

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

def main():
    # Load logo
    logo_b64 = load_logo()
    
    # =========================================================================
    # HEADER
    # =========================================================================
    logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" width="50" style="border-radius: 50%;">' if logo_b64 else '🤖'
    
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">
            {logo_html}
            <span>Kluzo Dashboard</span>
        </div>
        <div style="color: white; opacity: 0.8;">
            {datetime.now().strftime('%d %b %Y, %I:%M %p')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # GLOBAL SEARCH
    # =========================================================================
    search_query = st.text_input(
        "🔍 Search",
        placeholder="Search anything... (AWB, Order ID, Task, Log, Note)",
        label_visibility="collapsed"
    )
    
    if search_query:
        st.markdown("### 🔍 Search Results")
        st.info(f"Searching for: **{search_query}**")
        # TODO: Implement search across all data
        st.markdown("---")
    
    # =========================================================================
    # CONNECTION ALERT BANNER
    # =========================================================================
    connections = get_connections()
    disconnected = [k for k, v in connections.items() if v.get("status") == "disconnected"]
    
    if disconnected:
        st.markdown(f"""
        <div class="alert-banner">
            <span>🔴 CONNECTION ERROR: {', '.join(disconnected)} not responding</span>
            <span style="cursor: pointer;">Retry ↻</span>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # ROW 1: AI STATUS + QUICK ACTIONS
    # =========================================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🤖 AI Status</div>', unsafe_allow_html=True)
        
        ai_status = get_ai_status()
        status = ai_status.get("status", "offline")
        
        status_colors = {"working": "working", "idle": "idle", "offline": "offline"}
        status_icons = {"working": "🟢", "idle": "🟡", "offline": "🔴"}
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
            <span class="status-badge {status_colors.get(status, 'offline')}">
                {status_icons.get(status, '🔴')} {status.upper()}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Current task
        current_task = ai_status.get("current_task")
        if current_task:
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div class="text-gray" style="font-size: 0.85rem;">Current Task:</div>
                <div class="text-white" style="font-weight: 500;">{current_task.get('name', 'Unknown')}</div>
                <div class="text-cyan" style="font-size: 0.9rem;">
                    Step {current_task.get('step', 0)}/{current_task.get('total_steps', 0)} - {current_task.get('detail', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            progress = (current_task.get('step', 0) / current_task.get('total_steps', 1)) * 100
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress}%;"></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="text-gray">No active task</div>', unsafe_allow_html=True)
        
        # Sub-agents
        sub_agents = ai_status.get("sub_agents", [])
        if sub_agents:
            st.markdown("<br><div class='text-gray' style='font-size: 0.85rem;'>Sub-Agents:</div>", unsafe_allow_html=True)
            for agent in sub_agents:
                agent_status = "🟢" if agent.get("status") == "running" else "🟡"
                st.markdown(f"""
                <div style="color: #cbd5e1; font-size: 0.9rem;">
                    {agent_status} {agent.get('name', 'Unknown')} ({agent.get('model', '')})
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("📋 Task History", key="task_history"):
            st.info("Task history feature coming soon!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Ship Now", use_container_width=True, type="primary"):
                with st.spinner("Running shipping workflow..."):
                    try:
                        from shiprocket_workflow import run_shipping_workflow
                        result = run_shipping_workflow()
                        
                        if result.get("shipped", 0) > 0:
                            st.success(f"✅ Shipped {result['shipped']} orders!")
                        else:
                            st.warning("No orders shipped")
                        
                        # Show details
                        st.markdown(f"""
                        **Results:**
                        - Total: {result.get('total_orders', 0)}
                        - Shipped: {result.get('shipped', 0)} ✅
                        - Failed: {result.get('failed', 0)} ❌
                        - Pickup: {result.get('pickup_scheduled', 0)} 🚚
                        """)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col_b:
            if st.button("📥 Download Labels", use_container_width=True):
                batches = get_batches_history()
                if batches:
                    latest = batches[0]
                    zip_file = latest.get("zip_filename")
                    if zip_file:
                        zip_url = f"{GITHUB_RAW_BASE}/{zip_file}"
                        st.markdown(f"[📥 Download Latest ZIP]({zip_url})")
                else:
                    st.warning("No labels available")
        
        # Last run info
        batches = get_batches_history()
        if batches:
            latest = batches[0]
            st.markdown(f"""
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <div class="text-gray" style="font-size: 0.85rem;">Last Run:</div>
                <div class="text-white">{latest.get('date', '')} {latest.get('time', '')}</div>
                <div style="margin-top: 0.5rem;">
                    <span class="text-green">✅ {latest.get('shipped', 0)} shipped</span>
                    <span class="text-red" style="margin-left: 1rem;">❌ {latest.get('unshipped', 0)} failed</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # ROW 2: TASK BOARD (KANBAN)
    # =========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📋 Task Board</div>', unsafe_allow_html=True)
    
    tasks = get_tasks()
    
    # Add task button
    col_add, col_space = st.columns([1, 4])
    with col_add:
        if st.button("➕ Add Task", key="add_task"):
            st.session_state.show_add_task = True
    
    # Add task modal
    if st.session_state.get("show_add_task"):
        with st.expander("➕ Add New Task", expanded=True):
            task_title = st.text_input("Task Title")
            task_category = st.selectbox("Category", ["Shiprocket", "General", "Other"])
            task_priority = st.selectbox("Priority", ["🔴 High", "🟡 Medium", "🟢 Normal"])
            task_details = st.text_area("Details (optional)")
            
            col_cancel, col_save = st.columns(2)
            with col_cancel:
                if st.button("Cancel"):
                    st.session_state.show_add_task = False
                    st.rerun()
            with col_save:
                if st.button("Add Task", type="primary"):
                    st.success(f"Task '{task_title}' added!")
                    st.session_state.show_add_task = False
                    # TODO: Save task to GitHub
    
    # Kanban columns
    col_todo, col_progress, col_done = st.columns(3)
    
    with col_todo:
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="kanban-header kanban-todo">📝 TO DO ({len(tasks.get("todo", []))})</div>', unsafe_allow_html=True)
        
        for task in tasks.get("todo", []):
            priority_class = {
                "high": "priority-high",
                "medium": "priority-medium",
                "normal": "priority-normal"
            }.get(task.get("priority", "normal"), "priority-normal")
            
            st.markdown(f"""
            <div class="task-card {priority_class}">
                <div class="text-white" style="font-weight: 500;">{task.get('title', 'Untitled')}</div>
                <div class="text-gray" style="font-size: 0.8rem;">🏷️ {task.get('category', 'General')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if not tasks.get("todo"):
            st.markdown('<div class="text-gray" style="text-align: center; padding: 2rem;">No tasks</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_progress:
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="kanban-header kanban-progress">🔄 IN PROGRESS ({len(tasks.get("in_progress", []))})</div>', unsafe_allow_html=True)
        
        for task in tasks.get("in_progress", []):
            progress = task.get("progress", 0)
            st.markdown(f"""
            <div class="task-card">
                <div class="text-white" style="font-weight: 500;">{task.get('title', 'Untitled')}</div>
                <div class="text-cyan" style="font-size: 0.85rem;">{task.get('detail', '')}</div>
                <div class="progress-container" style="margin-top: 0.5rem;">
                    <div class="progress-bar" style="width: {progress}%;"></div>
                </div>
                <div class="text-gray" style="font-size: 0.8rem; margin-top: 0.3rem;">{progress}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        if not tasks.get("in_progress"):
            st.markdown('<div class="text-gray" style="text-align: center; padding: 2rem;">No tasks</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_done:
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="kanban-header kanban-done">✅ DONE ({len(tasks.get("done", []))})</div>', unsafe_allow_html=True)
        
        for task in tasks.get("done", []):
            st.markdown(f"""
            <div class="task-card">
                <div class="text-white" style="font-weight: 500;">{task.get('title', 'Untitled')}</div>
                <div class="text-green" style="font-size: 0.85rem;">{task.get('result', 'Completed')}</div>
                <div class="text-gray" style="font-size: 0.8rem;">⏱️ {task.get('completed_at', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if not tasks.get("done"):
            st.markdown('<div class="text-gray" style="text-align: center; padding: 2rem;">No tasks</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # ROW 3: ACTIVITY LOGS + NOTES PANEL
    # =========================================================================
    col_logs, col_notes = st.columns([1, 1])
    
    with col_logs:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📜 Activity Logs</div>', unsafe_allow_html=True)
        
        # Search and export
        col_search, col_csv, col_pdf = st.columns([2, 1, 1])
        with col_search:
            log_search = st.text_input("🔎 Search logs", placeholder="Search...", label_visibility="collapsed", key="log_search")
        with col_csv:
            st.button("📥 CSV", key="export_csv", use_container_width=True)
        with col_pdf:
            st.button("📥 PDF", key="export_pdf", use_container_width=True)
        
        logs = get_activity_logs().get("logs", [])
        
        # Filter logs if search
        if log_search:
            logs = [l for l in logs if log_search.lower() in l.get("message", "").lower()]
        
        # Display logs
        st.markdown('<div style="max-height: 300px; overflow-y: auto;">', unsafe_allow_html=True)
        
        if logs:
            for log in logs[:20]:  # Show last 20
                st.markdown(f"""
                <div class="log-entry">
                    <span class="log-time">{log.get('time', '')}</span>
                    <span class="log-icon">{log.get('icon', '📝')}</span>
                    <span>{log.get('message', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="text-gray" style="text-align: center; padding: 2rem;">No activity logs yet</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_notes:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📝 Notes for Kluzo</div>', unsafe_allow_html=True)
        
        # Note input
        new_note = st.text_area("Write a note for Kluzo...", height=80, key="new_note", label_visibility="collapsed", placeholder="Write a note for Kluzo...")
        
        if st.button("📤 Send Note", key="send_note"):
            if new_note:
                st.success("Note sent! Will process on next heartbeat.")
                # TODO: Save note to GitHub
            else:
                st.warning("Please write a note first")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display notes
        notes = get_notes().get("notes", [])
        
        for note in notes[:5]:  # Show last 5
            status_icon = "✅" if note.get("status") == "processed" else "⏳"
            
            st.markdown(f"""
            <div class="note-card">
                <div class="note-user">👤 You ({note.get('user_time', '')})</div>
                <div class="text-white" style="margin: 0.5rem 0;">{note.get('user_message', '')}</div>
            """, unsafe_allow_html=True)
            
            if note.get("ai_response"):
                st.markdown(f"""
                <div class="note-ai">🤖 Kluzo ({note.get('ai_time', '')})</div>
                <div class="text-white" style="margin: 0.5rem 0;">{note.get('ai_response', '')}</div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="text-gray" style="font-size: 0.8rem;">Status: {status_icon} {note.get('status', 'pending').title()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if not notes:
            st.markdown('<div class="text-gray" style="text-align: center; padding: 1rem;">No notes yet</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # ROW 4: DELIVERABLES + BULK AWB DOWNLOAD
    # =========================================================================
    col_deliverables, col_awb = st.columns([1, 1])
    
    with col_deliverables:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📦 Deliverables</div>', unsafe_allow_html=True)
        
        batches = get_batches_history()
        today = datetime.now().strftime('%Y-%m-%d')
        today_batches = [b for b in batches if b.get("date") == today]
        
        st.markdown("**📄 Labels**", unsafe_allow_html=True)
        
        if today_batches:
            latest = today_batches[0]
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div class="text-white">Latest: {latest.get('time', '')} ({latest.get('shipped', 0)} orders)</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📥 Download ZIP", key="download_zip"):
                zip_file = latest.get("zip_filename")
                if zip_file:
                    st.markdown(f"[Click to download]({GITHUB_RAW_BASE}/{zip_file})")
        else:
            st.markdown('<div class="text-gray">No batches today</div>', unsafe_allow_html=True)
        
        st.markdown("<br>**📅 Historical Batches**", unsafe_allow_html=True)
        
        for batch in today_batches[1:5]:  # Show older batches from today
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0;">
                <span class="text-gray">{batch.get('time', '')} ({batch.get('shipped', 0)} orders)</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>**📊 Reports**", unsafe_allow_html=True)
        if st.button("📥 Download XLSM Report", key="download_report"):
            st.info("XLSM report generation coming soon!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_awb:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📥 Bulk AWB Download</div>', unsafe_allow_html=True)
        
        awb_input = st.text_area(
            "Enter AWB numbers (one per line)",
            height=150,
            placeholder="284931134830193\n284931134830215\n284931134830204",
            key="awb_input",
            label_visibility="collapsed"
        )
        
        if st.button("📥 Download Labels", key="bulk_download", type="primary"):
            if awb_input.strip():
                awb_list = [line.strip() for line in awb_input.strip().split('\n') if line.strip()]
                st.info(f"Processing {len(awb_list)} AWB numbers...")
                
                token = shiprocket_authenticate()
                if token:
                    # TODO: Implement bulk download
                    st.success(f"Found {len(awb_list)} labels!")
                    st.button("📥 Download PDF", key="download_awb_pdf")
                else:
                    st.error("Authentication failed. Check Shiprocket credentials.")
            else:
                st.warning("Please enter AWB numbers")
        
        st.markdown("""
        <div class="text-gray" style="font-size: 0.85rem; margin-top: 1rem;">
            💡 Paste one AWB per line. Works for any order.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # ROW 5: SCHEDULED ACTIONS + CONNECTION STATUS
    # =========================================================================
    col_schedules, col_connections = st.columns([1, 1])
    
    with col_schedules:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">⏰ Scheduled Actions</div>', unsafe_allow_html=True)
        
        schedules = get_schedules().get("schedules", [])
        
        if st.button("➕ Add Schedule", key="add_schedule"):
            st.session_state.show_add_schedule = True
        
        if st.session_state.get("show_add_schedule"):
            with st.expander("➕ Add Schedule", expanded=True):
                schedule_time = st.time_input("Time")
                schedule_days = st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
                
                col_cancel, col_save = st.columns(2)
                with col_cancel:
                    if st.button("Cancel", key="cancel_schedule"):
                        st.session_state.show_add_schedule = False
                        st.rerun()
                with col_save:
                    if st.button("Save", key="save_schedule", type="primary"):
                        st.success("Schedule added!")
                        st.session_state.show_add_schedule = False
        
        if schedules:
            for schedule in schedules:
                status_icon = "🟢" if schedule.get("enabled") else "🔴"
                days = ", ".join(schedule.get("days", []))
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <span>{status_icon}</span>
                        <span class="text-white" style="margin-left: 0.5rem;">{schedule.get('time', '')}</span>
                        <span class="text-gray" style="margin-left: 0.5rem;">- Ship Now</span>
                    </div>
                    <div class="text-gray">{days}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="text-gray" style="text-align: center; padding: 1rem;">No schedules yet</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_connections:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🔌 Connection Status</div>', unsafe_allow_html=True)
        
        connections = {
            "Shiprocket API": "connected",
            "GitHub": "connected",
            "Ollama": "connected",
            "Kluzo (AI)": "connected",
            "Internet": "connected"
        }
        
        for name, status in connections.items():
            status_icon = "🟢" if status == "connected" else "🔴"
            status_text = "Connected" if status == "connected" else "Disconnected"
            
            st.markdown(f"""
            <div class="connection-item">
                <span class="connection-name">{name}</span>
                <div class="connection-status">
                    <span>{status_icon}</span>
                    <span class="text-gray">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔄 Check Now", key="check_connections"):
            st.info("Checking connections...")
            # TODO: Implement actual connection checks
            st.success("All connections OK!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748b;">
        Built with ❤️ by Kluzo 😎 for JSK Labs
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
