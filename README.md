# 🤖 AI Powered Automated Data Analyst System

**University of Sindh, Jamshoro — Final Year Project 2026**  
Department of Software Engineering, Faculty of Engineering & Technology

| Field | Detail |
|-------|--------|
| Students | Mohsin Ali (2K23/SWEE/36), Sammar Abbas (2K23/SWEE/69) |
| Supervisor | Engr. Noorulain |
| Co-Supervisor | Sir Amir Mal |

---

## 📁 Project File Structure

```
ai_data_analyst/
│
├── app.py                        ← Main entry point (run this)
│
├── pages/
│   ├── __init__.py
│   ├── home.py                   ← Upload page (multi-file CSV/Excel)
│   ├── dashboard.py              ← Interactive charts + AI auto-graph selection
│   ├── insights.py               ← AI Insights (OpenAI GPT)
│   ├── chatbot.py                ← Advanced AI Chatbot (OpenAI GPT)
│   └── report.py                 ← PDF Report Generator
│
├── utils/
│   ├── __init__.py
│   ├── data_processor.py         ← Load, clean, summarize datasets
│   ├── chart_engine.py           ← Smart auto chart selection engine
│   ├── ai_engine.py              ← OpenAI API integration
│   └── pdf_generator.py         ← ReportLab PDF builder
│
├── requirements.txt              ← All dependencies
└── README.md                     ← This file
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 Multi-File Upload | Upload multiple CSV or Excel files; switch between them |
| 🧹 Auto Data Cleaning | Auto-detect types, fill missing values, remove duplicates |
| 📊 Smart Dashboard | AI auto-selects best chart types for your data |
| 🔧 Custom Chart Builder | Build any chart type manually with filters |
| 🧠 AI Insights | GPT analyzes dataset and generates full report |
| 💬 AI Chatbot | Ask questions about your data in natural language |
| 📄 PDF Report | One-click professional PDF with stats, charts, AI analysis |

---

## 🚀 Setup & Run

### Step 1 — Install Python
Make sure Python 3.10+ is installed.

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the app
```bash
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## 🔑 OpenAI API Key

The AI Insights and Chatbot features require an **OpenAI API Key**.

1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Paste it into the app when prompted (it is only used in your session)

---

## 📊 Sample Datasets to Test

Download free datasets from:
- https://www.kaggle.com/datasets (search "titanic", "sales data", "iris")
- https://data.gov.pk (Pakistan government open data)
- Any CSV/Excel file you have

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Charts | Plotly Express |
| AI/LLM | OpenAI GPT-3.5-turbo |
| PDF | ReportLab |
| Charts → PDF | Kaleido |
| File Formats | CSV, XLSX, XLS |

---

## 📋 System Flow

```
[User] → [Upload CSV/Excel]
            ↓
    [Data Processing Module]
    (clean, detect types, stats)
            ↓
    [Visualization Module] ←→ [Auto Chart Selection AI]
            ↓
    [AI Insight Generator (OpenAI GPT)]
            ↓
    [Chatbot Interface (OpenAI GPT)]
            ↓
    [PDF Report Generator]
            ↓
    [Dashboard UI (Streamlit)]
```

---

*© 2026 — Mohsin Ali & Sammar Abbas — University of Sindh*
