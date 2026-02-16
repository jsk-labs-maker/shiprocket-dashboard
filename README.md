# 📊 Shiprocket Dashboard Suite

Complete dashboard and automation system for Shiprocket shipping operations.

## 🎯 Components

### 1. Staff Dashboard (`app.py`)
**View-only interface for warehouse staff**

Features:
- 📦 Latest batch labels (organized by SKU + Courier)
- 📋 Processing history (all batches, downloadable)
- 🔄 Live processing status
- 📱 Mobile-friendly, Hindi + English
- 🎨 Visual-first design (big buttons, color-coded couriers)

**Deployment:** Streamlit Cloud (no secrets needed)

### 2. Admin Control Panel (`admin_app.py`)
**Management interface with bulk operations**

Features:
- 🟢 System status monitoring (processing/idle/complete)
- 📊 Today's overview (batches, shipped, failed, success rate)
- 📥 **Bulk AWB label download** (paste AWBs → get labels)
- 📝 Processing logs & recent activity
- ⚡ Quick actions

**Deployment:** Streamlit Cloud + Streamlit Secrets required

### 3. Automation Scripts

**`ship_orders.py`** - "Ship them buddy" workflow
- Ships all NEW orders
- Downloads labels
- Sorts by Date + Courier + SKU
- Schedules pickup
- Generates manifest
- Uploads to GitHub

**`download_awb_labels.py`** - CLI tool for AWB downloads
- Download labels by AWB number
- Supports multiple AWBs
- Saves to local directory

## 🚀 Deployment Guide

### Staff Dashboard

1. **Deploy to Streamlit Cloud:**
   - App file: `app.py`
   - Repo: `github.com/jsk-labs-maker/shiprocket-dashboard`
   
2. **No secrets needed** (reads from GitHub public/ folder)

3. **Done!** Dashboard shows latest batches automatically.

### Admin Panel

1. **Deploy to Streamlit Cloud:**
   - App file: `admin_app.py`
   - Repo: `github.com/jsk-labs-maker/shiprocket-dashboard`

2. **Configure Streamlit Secrets:**
   - Go to app settings → Secrets
   - Add:
   ```toml
   [shiprocket]
   email = "openclawd12@gmail.com"
   password = "Kluzo@1212"
   ```

3. **Done!** Bulk AWB download will work automatically.

## 📥 Bulk AWB Label Download

### Option 1: Admin Panel (Recommended ⭐)

1. Open admin dashboard
2. Paste AWB numbers (one per line):
   ```
   284931134807362
   284931134821395
   284931134821922
   ```
3. Click "📥 Download Labels"
4. Get combined PDF with all labels

### Option 2: Telegram

Message Kluzo:
```
Download labels:
284931134807362
284931134821395
```

### Option 3: Command Line

```bash
python3 download_awb_labels.py AWB1 AWB2 AWB3
```

## 🤖 Telegram Automation

Say **"Ship them buddy"** and Kluzo automatically:

1. ✅ Ships all NEW orders (auto courier assignment)
2. 📄 Downloads labels
3. 🗂️ Sorts by Date + Courier + SKU
4. 🚚 Schedules pickup (one by one)
5. 📋 Generates manifest
6. ☁️ Uploads to GitHub (public/ folder)
7. 💬 Replies "Done Boss ✅" with summary

Dashboard auto-updates after processing!

## 📁 File Structure

```
shiprocket-dashboard/
├── app.py                          # Staff dashboard
├── admin_app.py                    # Admin control panel
├── ship_orders.py                  # "Ship them buddy" automation
├── download_awb_labels.py          # CLI AWB download tool
├── requirements.txt                # Python dependencies
├── public/                         # GitHub-hosted files
│   ├── status.json                 # Live processing status
│   ├── latest_labels.json          # Latest batch metadata
│   ├── batches_history.json        # All batches (last 100)
│   ├── batch_YYYY-MM-DD_HHMMSS.zip # Individual batch ZIPs
│   └── manifest_*.pdf              # Manifests
└── .streamlit/
    └── secrets.toml.example        # Secrets template
```

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run staff dashboard
streamlit run app.py

# Run admin panel
streamlit run admin_app.py

# Test AWB download
python3 download_awb_labels.py 284931134807362
```

## 🔑 Credentials

Stored in `/Users/klaus/.openclaw/workspace/shiprocket-credentials.env`:
- **Email:** openclawd12@gmail.com
- **Password:** Kluzo@1212

## 📊 Architecture

```
Telegram                   Kluzo (OpenClaw Agent)
   │                              │
   │  "Ship them buddy"           │
   └─────────────────────────────►│
                                  ▼
                       ┌──────────────────────┐
                       │   ship_orders.py     │
                       │  - Fetch NEW orders  │
                       │  - Ship orders       │
                       │  - Download labels   │
                       │  - Schedule pickup   │
                       │  - Generate manifest │
                       │  - Sort labels       │
                       │  - Upload to GitHub  │
                       └──────────┬───────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    ▼                            ▼
          ┌──────────────────┐        ┌──────────────────┐
          │ Staff Dashboard  │        │  Admin Panel     │
          │  - View labels   │        │  - Monitor       │
          │  - Download ZIP  │        │  - Bulk AWB      │
          │  - History       │        │  - Analytics     │
          └──────────────────┘        └──────────────────┘
```

## 🎯 Next Features

- [ ] 7-day trends (charts)
- [ ] Courier performance tracking
- [ ] Failed order retry
- [ ] Export reports (CSV)
- [ ] WhatsApp notifications
- [ ] Inventory alerts

---

Built with ❤️ by Kluzo 😎 for JSK Labs
