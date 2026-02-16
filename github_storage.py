"""
GitHub Storage Module
=====================
Read/Write JSON data to GitHub repository

For write operations, requires GITHUB_TOKEN in environment.
"""

import os
import json
import base64
import requests
from datetime import datetime

# Configuration
GITHUB_REPO = "jsk-labs-maker/shiprocket-dashboard"
GITHUB_BRANCH = "main"
GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/public"


def get_github_token():
    """Get GitHub token from environment or Streamlit secrets."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'github' in st.secrets:
            return st.secrets['github'].get('token')
    except:
        pass
    
    return os.getenv('GITHUB_TOKEN')


def read_json(path: str) -> dict:
    """
    Read JSON file from GitHub public folder.
    
    Args:
        path: Path relative to public/ (e.g., 'ai/status.json')
    
    Returns:
        Parsed JSON data or empty dict on error
    """
    try:
        url = f"{GITHUB_RAW_BASE}/{path}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return {}


def write_json(path: str, data: dict) -> bool:
    """
    Write JSON file to GitHub repository.
    
    Requires GITHUB_TOKEN to be set.
    
    Args:
        path: Path relative to public/ (e.g., 'ai/status.json')
        data: Data to write
    
    Returns:
        True on success, False on error
    """
    token = get_github_token()
    if not token:
        print("No GitHub token configured")
        return False
    
    try:
        # Get current file SHA (needed for update)
        file_path = f"public/{path}"
        url = f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/contents/{file_path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check if file exists
        response = requests.get(url, headers=headers, timeout=10)
        sha = None
        if response.status_code == 200:
            sha = response.json().get("sha")
        
        # Prepare content
        content = json.dumps(data, indent=2)
        encoded = base64.b64encode(content.encode()).decode()
        
        # Update or create file
        payload = {
            "message": f"Update {path}",
            "content": encoded,
            "branch": GITHUB_BRANCH
        }
        if sha:
            payload["sha"] = sha
        
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        
        return response.status_code in [200, 201]
        
    except Exception as e:
        print(f"Error writing {path}: {e}")
        return False


def append_to_list(path: str, item: dict, list_key: str = "items", max_items: int = 100) -> bool:
    """
    Append an item to a list in a JSON file.
    
    Args:
        path: Path relative to public/
        item: Item to append
        list_key: Key of the list in the JSON
        max_items: Maximum items to keep (oldest removed)
    
    Returns:
        True on success
    """
    data = read_json(path)
    
    if list_key not in data:
        data[list_key] = []
    
    # Add item to beginning of list
    data[list_key].insert(0, item)
    
    # Trim to max items
    data[list_key] = data[list_key][:max_items]
    
    # Update timestamp
    data["updated_at"] = datetime.now().isoformat()
    
    return write_json(path, data)


def update_status(status: str, message: str, current_task: str = None, progress: int = 0) -> bool:
    """
    Update AI status.
    
    Args:
        status: Status string (idle, working, processing, complete, error)
        message: Status message
        current_task: Current task description (optional)
        progress: Progress percentage 0-100
    
    Returns:
        True on success
    """
    data = {
        "status": status,
        "message": message,
        "current_task": current_task,
        "progress": progress,
        "updated_at": datetime.now().isoformat()
    }
    
    if status in ["working", "processing"]:
        data["started_at"] = datetime.now().isoformat()
    
    return write_json("ai/status.json", data)


def add_log(action: str, message: str, log_type: str = "info") -> bool:
    """
    Add activity log entry.
    
    Args:
        action: Action name
        message: Log message
        log_type: Type (info, success, warning, error)
    
    Returns:
        True on success
    """
    import uuid
    
    item = {
        "id": f"log-{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "message": message,
        "type": log_type
    }
    
    return append_to_list("logs/activity.json", item, "logs", 500)


def add_task(title: str, description: str = "", priority: str = "medium", status: str = "open") -> bool:
    """
    Add a new task.
    
    Args:
        title: Task title
        description: Task description
        priority: Priority (low, medium, high)
        status: Status (open, in_progress, done)
    
    Returns:
        True on success
    """
    import uuid
    
    item = {
        "id": f"task-{uuid.uuid4().hex[:8]}",
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "created_at": datetime.now().isoformat()
    }
    
    return append_to_list("tasks/tasks.json", item, "tasks", 200)


def add_note(content: str, note_type: str = "user") -> bool:
    """
    Add a new note.
    
    Args:
        content: Note content
        note_type: Type (user, ai)
    
    Returns:
        True on success
    """
    import uuid
    
    item = {
        "id": f"note-{uuid.uuid4().hex[:8]}",
        "type": note_type,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return append_to_list("notes/notes.json", item, "notes", 200)


# Convenience functions for common operations
def set_idle():
    """Set status to idle."""
    return update_status("idle", "Ready for tasks")


def set_working(task: str, progress: int = 0):
    """Set status to working on a task."""
    return update_status("working", f"Working on: {task}", task, progress)


def set_complete(message: str = "Task completed successfully"):
    """Set status to complete."""
    return update_status("complete", message)


def set_error(message: str):
    """Set status to error."""
    return update_status("error", message)


if __name__ == "__main__":
    # Test reading
    print("Testing read operations...")
    
    status = read_json("ai/status.json")
    print(f"AI Status: {status.get('status', 'unknown')}")
    
    tasks = read_json("tasks/tasks.json")
    print(f"Tasks: {len(tasks.get('tasks', []))}")
    
    notes = read_json("notes/notes.json")
    print(f"Notes: {len(notes.get('notes', []))}")
    
    print("\n✅ Read operations working!")
