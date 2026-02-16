"""
Shiprocket Analytics Dashboard
==============================
View-only dashboard for shipping history and label downloads.

Built by Kluzo 😎 for Dhruv
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import os

st.set_page_config(
    page_title="Shipping Analytics | JSK Labs",
    page_icon="📊",
    layout="wide"
)

# Configuration
BASE_URL = "https://apiv2.shiprocket.in/v1/external"
DATA_DIR = Path("data")
HISTORY_FILE = DATA_DIR / "shipping_history.json"

# --- Session State ---
if 'api_token' not in st.session_state:
    st.session_state.api_token = None
if 'api_email' not in st.session_state:
    st.session_state.api_email = None


# --- API Functions ---
def api_authenticate(email: str, password: str) -> dict:
    """Authenticate with Shiprocket API."""
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json={"email": email, "password": password})
    
    if response.status_code == 403:
        error_msg = response.json().get('message', 'Account blocked')
        if 'blocked' in error_msg.lower() or 'failed login' in error_msg.lower():
            raise requests.exceptions.HTTPError(f"403 Blocked: {error_msg}")
        raise requests.exceptions.HTTPError(f"403: {error_msg}")
    elif response.status_code == 401:
        raise requests.exceptions.HTTPError("401 Unauthorized: Invalid credentials")
    
    response.raise_for_status()
    return response.json()


def get_orders_count(token: str, status: str, days: int = 30) -> int:
    """Get count of orders by status."""
    url = f"{BASE_URL}/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    params = {
        "filter": status,
        "per_page": 1,
        "from": from_date,
        "to": to_date
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("meta", {}).get("pagination", {}).get("total", 0)
    return 0


def get_wallet_balance(token: str) -> float:
    """Get wallet balance."""
    url = f"{BASE_URL}/account/details/wallet-balance"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", {}).get("balance_amount", 0)
    return 0


def load_shipping_history():
    """Load shipping history from JSON file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


# --- UI ---
st.title("📊 Shipping Analytics Dashboard")
st.markdown("**View shipping history • Download sorted labels**")

# --- Login Section ---
if not st.session_state.api_token:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Connect to Shiprocket")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Connect", use_container_width=True)
            
            if submit and email and password:
                try:
                    with st.spinner("Authenticating..."):
                        auth_data = api_authenticate(email, password)
                        st.session_state.api_token = auth_data.get("token")
                        st.session_state.api_email = email
                        st.success("✅ Connected!")
                        st.rerun()
                except requests.exceptions.HTTPError as e:
                    error_msg = str(e)
                    if "403" in error_msg and "blocked" in error_msg.lower():
                        st.error("🔒 **Account Temporarily Blocked**")
                        st.warning("""
                        Too many failed login attempts. To fix:
                        1. Wait 15-30 minutes and try again
                        2. Or reset password on Shiprocket
                        """)
                    elif "401" in error_msg or "Invalid" in error_msg:
                        st.error("❌ **Invalid Credentials**")
                    else:
                        st.error(f"❌ {error_msg}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

else:
    # --- Connected Dashboard ---
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ Connected as **{st.session_state.api_email}**")
    with col2:
        if st.button("🔓 Disconnect"):
            st.session_state.api_token = None
            st.session_state.api_email = None
            st.rerun()
    
    # --- Quick Stats ---
    st.markdown("---")
    st.markdown("### 📈 Quick Stats (Last 30 Days)")
    
    try:
        token = st.session_state.api_token
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            balance = get_wallet_balance(token)
            st.metric("💰 Wallet", f"₹{balance:,.2f}")
        
        with col2:
            new_count = get_orders_count(token, "new", days=30)
            st.metric("🆕 New Orders", new_count)
        
        with col3:
            rts_count = get_orders_count(token, "ready_to_ship", days=30)
            st.metric("📦 Ready To Ship", rts_count)
        
        with col4:
            delivered_count = get_orders_count(token, "delivered", days=30)
            st.metric("✅ Delivered", delivered_count)
    
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")
    
    # --- Shipping History ---
    st.markdown("---")
    st.markdown("### 📋 Shipping History")
    st.caption("Orders processed via Telegram command")
    
    history = load_shipping_history()
    
    if not history:
        st.info("No shipping history yet. Use **'Ship them buddy'** in Telegram to process orders.")
    else:
        for i, record in enumerate(history[:20]):  # Show last 20
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                
                with col1:
                    st.markdown(f"**{record.get('date_display', 'Unknown')}**")
                
                with col2:
                    total = record.get('total_orders', 0)
                    st.markdown(f"📦 **{total}** total")
                
                with col3:
                    shipped = record.get('shipped', 0)
                    st.markdown(f"✅ **{shipped}** shipped")
                
                with col4:
                    unshipped = record.get('unshipped', 0)
                    if unshipped > 0:
                        st.markdown(f"❌ **{unshipped}** failed")
                    else:
                        st.markdown(f"✓ All shipped")
                
                with col5:
                    # Download sorted labels
                    labels_sorted = record.get('labels_sorted', {})
                    if labels_sorted:
                        for courier, info in labels_sorted.items():
                            label_path = info.get('path', '')
                            if label_path and os.path.exists(label_path):
                                with open(label_path, 'rb') as f:
                                    st.download_button(
                                        f"📥 {courier} ({info['count']})",
                                        data=f.read(),
                                        file_name=os.path.basename(label_path),
                                        mime="application/pdf",
                                        key=f"dl_{i}_{courier}"
                                    )
                
                # Show unshipped orders if any
                unshipped_orders = record.get('unshipped_orders', [])
                if unshipped_orders:
                    with st.expander(f"⚠️ View {len(unshipped_orders)} unshipped orders"):
                        for uo in unshipped_orders:
                            st.caption(f"Order #{uo.get('order_id')}: {uo.get('reason', 'Unknown reason')}")
                
                st.divider()
    
    # --- Info Section ---
    st.markdown("---")
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        ### Telegram Integration
        
        To process orders, message Kluzo on Telegram:
        
        > **"Ship them buddy"**
        
        Kluzo will automatically:
        1. ✅ Ship all NEW orders (auto courier assignment)
        2. 📄 Download & sort labels by courier
        3. 🚚 Schedule pickup for tomorrow
        4. 📋 Generate manifest
        
        Then reply **"Done Boss"** with summary.
        
        ### This Dashboard
        
        - View shipping history
        - See order volumes
        - Download sorted labels (by courier)
        - Track shipped vs unshipped orders
        
        **No action buttons** — all actions are triggered via Telegram.
        """)

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ by Kluzo 😎 for JSK Labs")
