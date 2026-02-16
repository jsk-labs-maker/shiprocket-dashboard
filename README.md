# 📊 Shiprocket Analytics Dashboard

View-only analytics dashboard for shipping operations. All actions triggered via Telegram.

## Features

### 📈 Quick Stats
- Wallet balance
- New orders count
- Ready to ship count
- Delivered count

### 📋 Shipping History
- Date/time of each batch
- Total orders processed
- Shipped vs unshipped count
- Download sorted labels (by courier)

### 🤖 Telegram Integration
This dashboard is **view-only**. To process orders:

1. Message Kluzo on Telegram: **"Ship them buddy"**
2. Kluzo automatically:
   - Ships all NEW orders
   - Downloads & sorts labels
   - Schedules pickup
   - Generates manifest
3. Replies **"Done Boss"** with summary
4. View results here in the dashboard

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## Architecture

```
┌─────────────────┐      ┌──────────────┐
│    Telegram     │ ──── │    Kluzo     │
│ "Ship them      │      │  (executes   │
│   buddy"        │      │   workflow)  │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Shiprocket API       │
                    │  - Ship orders        │
                    │  - Download labels    │
                    │  - Schedule pickup    │
                    │  - Generate manifest  │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Analytics Dashboard  │
                    │  - View history       │
                    │  - Download labels    │
                    │  - See stats          │
                    └───────────────────────┘
```

---

Built with ❤️ by Kluzo 😎 for JSK Labs
