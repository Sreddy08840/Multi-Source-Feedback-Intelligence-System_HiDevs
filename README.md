# 🧠 Multi-Source Feedback Intelligence System

> A full-stack AI-powered platform for ingesting, analyzing, categorizing, and routing customer feedback from multiple sources — with a real-time analytics dashboard.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61dafb?logo=react)
![Vite](https://img.shields.io/badge/Vite-8-646cff?logo=vite)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

The **Multi-Source Feedback Intelligence System** collects and processes customer feedback from diverse sources (web forms, email, app stores, API webhooks, G2 reviews), applies NLP-based sentiment analysis and ML categorization, scores urgency, and routes high-priority items to integrations like **Slack**, **Microsoft Teams**, **Jira**, and **Salesforce** — all visualized in a beautiful real-time dashboard.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                    │
│         (Vite + React 19 | Port: 5173)              │
└────────────────────┬────────────────────────────────┘
                     │ REST API (HTTP)
┌────────────────────▼────────────────────────────────┐
│              FastAPI Backend                        │
│          (Uvicorn | Port: 8000)                     │
│  ┌───────────┐ ┌────────────┐ ┌──────────────────┐  │
│  │ Ingestion │ │ Processing │ │   Intelligence   │  │
│  │  Layer    │ │   Layer    │ │      Layer       │  │
│  └───────────┘ └────────────┘ └──────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │          SQLite Database (feedback.db)         │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │     Actions: Slack / Teams / Jira / SFDC       │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🔌 Multi-Source Ingestion
| Source | Description |
|--------|-------------|
| **Web Form** | Direct form submissions via `/api/feedback/submit` |
| **Email Parser** | Parses structured fields from email payloads |
| **Webhooks** | Receives real-time events from external systems |
| **App Store APIs** | Simulated Google Play & Apple App Store review intake |
| **G2 Reviews** | Simulated G2 Crowd review ingestion |
| **CSV/File Import** | Bulk upload feedback via CSV file |

### 🧪 Processing Pipeline
- **Text Cleaning** — Strips noise, normalizes whitespace, removes special characters
- **Sentiment Analysis** — Local heuristic + keyword-based sentiment scoring (Positive / Negative / Neutral)
- **Categorization** — ML keyword-weighted classification into: `Bug`, `Feature Request`, `Performance`, `UI/UX`, `Billing`, `Support`, `General`
- **Priority Scoring** — Urgency score calculated from sentiment, rating, keywords, and customer segment (VIP priority)

### 🤖 Intelligence Layer
- **Trend Detection** — Identifies emerging complaint/request patterns over time using rolling windows
- **ML Models** — TF-IDF + category frequency models for advanced topic extraction
- **AI Prompt Templates** — Prebuilt prompt scaffolds for LLM-based summarization and analysis

### 📊 Analytics Dashboard
- Real-time sentiment breakdown (donut charts)
- Feedback volume over time (line/bar charts)
- Category distribution heatmaps
- Source comparison views
- Urgent feedback triage queue
- Integration status panel

### 🔗 Integrations & Actions
| Integration | Capability |
|-------------|------------|
| **Slack** | Sends urgent feedback alerts to channels |
| **Microsoft Teams** | Adaptive card notifications |
| **Jira** | Auto-creates tickets for bug/urgent items |
| **Salesforce** | Creates CRM cases for VIP customer issues |
| **Reports** | Exportable PDF/JSON summaries |

---

## 📁 Project Structure

```
feedback_intelligence/
│
├── src/                          # Backend source code
│   ├── main.py                   # FastAPI app entry point & DB seeder
│   ├── database.py               # SQLAlchemy engine & session config
│   ├── models.py                 # ORM models (FeedbackItem, IntegrationConfig)
│   ├── schemas.py                # Pydantic request/response schemas
│   │
│   ├── api/
│   │   ├── endpoints.py          # All REST API route handlers
│   │   └── middleware.py         # Request logging middleware
│   │
│   ├── ingestion/
│   │   ├── api_clients.py        # External API (AppStore, G2) clients
│   │   ├── email_parser.py       # Email payload parser
│   │   ├── file_importer.py      # CSV/file bulk import handler
│   │   └── webhooks.py           # Webhook event receiver
│   │
│   ├── processing/
│   │   ├── cleaner.py            # Text normalization & cleaning
│   │   ├── analyzer.py           # Sentiment analysis engine
│   │   ├── categorizer.py        # Feedback category classifier
│   │   └── priority_scorer.py    # Urgency scoring algorithm
│   │
│   ├── intelligence/
│   │   ├── ai_prompts.py         # LLM prompt templates
│   │   ├── ml_models.py          # TF-IDF & ML topic extraction
│   │   └── trend_detector.py     # Time-series trend analysis
│   │
│   └── actions/
│       ├── alerts.py             # Slack/Teams notification sender
│       ├── integrations.py       # Jira/Salesforce connector
│       └── reports.py            # Report generator (PDF/JSON)
│
├── frontend/                     # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx               # Main dashboard application
│   │   ├── App.css               # Component styles
│   │   ├── index.css             # Global styles & design tokens
│   │   └── main.jsx              # React app entry point
│   ├── index.html                # HTML shell
│   ├── vite.config.js            # Vite dev server config
│   └── package.json              # Frontend dependencies
│
├── tests/                        # Backend test suite (pytest)
├── requirements.txt              # Python dependencies
├── feedback.db                   # SQLite database (auto-created)
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| Git | 2.x |

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sreddy08840/Multi-Source-Feedback-Intelligence-System_HiDevs.git
cd Multi-Source-Feedback-Intelligence-System_HiDevs
```

---

### 2️⃣ Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Run the Backend Server

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at:
- **API Base**: `http://localhost:8000`
- **Interactive Docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

> **Note**: The database (`feedback.db`) and seed data are created automatically on first startup.

---

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at: **`http://localhost:5173`**

---

## 🔑 API Reference

### Feedback Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/feedback/submit` | Submit new feedback (web form) |
| `GET` | `/api/feedback` | List all feedback with filters |
| `GET` | `/api/feedback/{id}` | Get single feedback item |
| `PATCH` | `/api/feedback/{id}/status` | Update feedback status |
| `DELETE` | `/api/feedback/{id}` | Delete feedback item |
| `POST` | `/api/feedback/import` | Bulk import from CSV file |
| `POST` | `/api/feedback/webhook` | Receive webhook events |
| `POST` | `/api/feedback/email` | Ingest email feedback |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/summary` | Overall metrics summary |
| `GET` | `/api/analytics/sentiment` | Sentiment distribution |
| `GET` | `/api/analytics/categories` | Category breakdown |
| `GET` | `/api/analytics/trends` | Time-series trend data |
| `GET` | `/api/analytics/sources` | Source comparison metrics |

### Intelligence Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/intelligence/trends` | ML-detected emerging trends |
| `GET` | `/api/intelligence/insights` | Auto-generated insights |
| `POST` | `/api/intelligence/prompts` | Get AI prompt for a feedback batch |

### Integration & Action Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/integrations` | List integration configs |
| `POST` | `/api/integrations/{name}/toggle` | Enable/disable an integration |
| `POST` | `/api/actions/alert/{id}` | Send alert for feedback item |
| `POST` | `/api/actions/report` | Generate analytics report |

---

## 🧪 Running Tests

```bash
# From the project root (with venv activated)
pytest tests/ -v
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root to configure optional settings:

```env
# Database
DATABASE_URL=sqlite:///./feedback.db

# API Keys (for production integrations)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR_URL
JIRA_API_TOKEN=your-jira-api-token
JIRA_BASE_URL=https://your-domain.atlassian.net
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com

# LLM (optional, for AI summarization)
OPENAI_API_KEY=sk-your-openai-key
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **SQLAlchemy** | ORM & database toolkit |
| **SQLite** | Embedded database (dev) |
| **Pydantic** | Data validation & serialization |
| **Pandas** | Data manipulation for analytics |
| **scikit-learn** | TF-IDF vectorization & ML models |
| **NumPy** | Numerical computations |
| **HTTPX** | Async HTTP client for API ingestion |
| **python-dotenv** | Environment variable management |
| **pytest** | Test framework |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **Vite 8** | Build tool & dev server |
| **Vanilla CSS** | Custom design system & animations |

---

## 🔄 Data Flow

```
External Sources
       │
       ▼
┌─────────────────┐
│  Ingestion Layer │  ← Web, Email, Webhook, API, CSV
│  (src/ingestion) │
└────────┬────────┘
         │ Raw Text + Metadata
         ▼
┌─────────────────┐
│ Processing Layer │  ← Clean → Analyze → Categorize → Score
│ (src/processing) │
└────────┬────────┘
         │ Processed FeedbackItem
         ▼
┌─────────────────┐
│    SQLite DB     │  ← feedback.db
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────────────┐
│ API  │  │ Intelligence │  ← Trends, ML Insights
│Layer │  │   Layer      │
└──┬───┘  └──────────────┘
   │
   ▼
┌──────────────┐   ┌──────────────────┐
│ React        │   │ Actions Layer    │
│ Dashboard    │   │ Slack/Teams/Jira │
└──────────────┘   └──────────────────┘
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Sreddy08840**  
GitHub: [@Sreddy08840](https://github.com/Sreddy08840)  
Project: [Multi-Source-Feedback-Intelligence-System_HiDevs](https://github.com/Sreddy08840/Multi-Source-Feedback-Intelligence-System_HiDevs)

---

*Built with ❤️ as part of the HiDevs program.*
