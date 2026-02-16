# 🎛️ JSK Labs Shiprocket Dashboard

Premium admin dashboard for managing Shiprocket shipping operations.

## 🚀 Features

### 10-Section Admin Dashboard

1. **🤖 AI Status** - Real-time status, current task, sub-agents
2. **⚡ Quick Actions** - Ship Now, Download Labels
3. **📋 Task Board** - Kanban with Open/In Progress/Done columns
4. **📜 Activity Logs** - Search, filter, export CSV
5. **📝 Notes Panel** - User & AI notes with timestamps
6. **📦 Deliverables** - Labels by date, ZIP downloads
7. **📥 Bulk AWB Download** - Paste AWBs → combined PDF
8. **⏰ Scheduled Actions** - Auto-ship at set times
9. **🔌 Connection Status** - API health monitoring
10. **🔍 Global Search** - Search across all data

### Staff Dashboard (app.py)
- Latest batch labels organized by SKU → Courier
- Live processing status indicator
- Processing history with download links
- Mobile-friendly design

## 📁 Project Structure

```
shiprocket-dashboard/
├── admin_app.py          # Admin dashboard (10 sections)
├── app.py                # Staff dashboard (simple)
├── staff_app.py          # Alternative staff view
├── shiprocket_workflow.py # Shipping workflow module
├── github_storage.py     # GitHub storage operations
├── download_awb_labels.py # AWB download helper
├── requirements.txt
├── .streamlit/
│   └── secrets.toml.example
└── public/
    ├── ai/
    │   ├── status.json
    │   └── sub_agents.json
    ├── tasks/
    │   ├── tasks.json
    │   └── archive/
    ├── logs/
    │   └── activity.json
    ├── notes/
    │   └── notes.json
    ├── schedules/
    │   └── schedules.json
    ├── deliverables/
    │   └── index.json
    ├── connections/
    │   └── status.json
    ├── batches_history.json
    └── batch_*.zip
```

## 🔧 Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/jsk-labs-maker/shiprocket-dashboard.git
cd shiprocket-dashboard

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create credentials file
cp .env.example .env
# Edit .env with your Shiprocket credentials

# Run admin dashboard
streamlit run admin_app.py --server.port 8505

# Run staff dashboard
streamlit run app.py --server.port 8501
```

### Streamlit Cloud Deployment

1. Fork this repository
2. Connect to Streamlit Cloud
3. Add secrets in app settings:

```toml
[shiprocket]
email = "your-email@example.com"
password = "your-password"
# OR use API key:
# api_key = "your-api-key"

[github]
token = "ghp_xxxx"  # For write operations
```

## 📡 API Integration

### Shiprocket API
- Authentication via email/password or API key
- Order fetching with status filters
- Bulk shipping with auto courier selection
- Label generation and download
- Pickup scheduling
- Manifest generation

### GitHub Storage
- JSON-based data storage in `public/` folder
- Real-time status updates
- Batch history tracking
- Read operations: No auth required
- Write operations: Requires GitHub token

## 🔄 Shipping Workflow

The "Ship Now" button runs this workflow:

1. **Authenticate** - Get Shiprocket token
2. **Fetch Orders** - Get NEW orders (last 7 days)
3. **Ship Orders** - Assign AWB with auto courier
4. **Download Labels** - Get labels for shipped orders
5. **Schedule Pickup** - One-by-one for reliability
6. **Generate Manifest** - Create shipping manifest
7. **Upload to GitHub** - Store labels in public/ folder

## 🎨 UI Features

- **Premium dark theme** with gradients
- **Responsive design** for mobile/desktop
- **Status indicators** with color coding
- **Alert banners** for connection issues
- **Metric cards** for quick stats
- **Kanban board** for task management

## 🤖 Telegram Integration

For automated shipping via Telegram:

```
"Ship them buddy" → Full shipping workflow
"Download labels: AWB1, AWB2" → Bulk label download
```

## 📊 Storage Schema

### ai/status.json
```json
{
  "status": "idle|working|processing|complete|error",
  "message": "Status message",
  "current_task": "Task description",
  "progress": 0-100,
  "updated_at": "ISO timestamp"
}
```

### tasks/tasks.json
```json
{
  "tasks": [
    {
      "id": "task-xxx",
      "title": "Task title",
      "description": "Description",
      "priority": "low|medium|high",
      "status": "open|in_progress|done",
      "created_at": "ISO timestamp"
    }
  ]
}
```

### batches_history.json
```json
{
  "batches": [
    {
      "date": "2026-02-16",
      "time": "14:30",
      "shipped": 50,
      "unshipped": 2,
      "skus": ["SKU1", "SKU2"],
      "sku_count": 5,
      "zip_file": "public/batch_2026-02-16_143000.zip"
    }
  ]
}
```

## 🔒 Security

- Credentials stored in Streamlit Secrets (production)
- Environment variables for local development
- GitHub token required only for write operations
- Public read access for dashboard data

## 📝 License

MIT License - Built with ❤️ by Kluzo 😎 for JSK Labs

## 🔗 Links

- **Staff Dashboard**: https://shiprocket-dashboard-5u7lgyldagcyv8dy6batr8.streamlit.app/
- **GitHub Repository**: https://github.com/jsk-labs-maker/shiprocket-dashboard
- **Label Sorter**: https://jsk-labs-maker-shiprocket-label-sorter-app-zzx9qs.streamlit.app/
