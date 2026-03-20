# 🛡️ AURA - Student Wellness Intelligence System

<img src="/aura-icon.png" alt="AURA Logo" width="100" height="100" />

**Privacy-First AI System for Early Mental Health Intervention in Universities**

---

## 🎯 Overview

**AURA** analyzes behavioral metadata (login patterns, WiFi zones, submission times) to identify students at risk of mental health crises. **No invasive monitoring—only anonymized behavioral signals with FERPA compliance.**

### Key Benefits

- 📊 **97.5% F1 Score** - Ensemble ML model (IsolationForest + XGBoost + RandomForest)
- 🔐 **Privacy-First** - SHA-256 pseudonymization + AES-256-GCM encryption
- ⚡ **Real-Time Dashboard** - Live updates via SSE for instant alerts
- 📈 **18 Features** - Sleep disruption, social isolation, academic drift detection
- 🔄 **Auto TTL** - Behavioral logs auto-delete after 90 days

---

## 📑 Table of Contents

| Section                                | Description       |
| -------------------------------------- | ----------------- |
| [🎯 Overview](#overview)               | What is AURA?     |
| [✨ Features](#features)               | Core capabilities |
| [⚙️ Setup](#setup--installation)       | Getting started   |
| [🔌 API](#api-documentation)           | HTTP endpoints    |
| [🛠️ Tech Stack](#technology-stack)     | Technologies used |
| [🚀 Deployment](#deployment)           | Production setup  |
| [🐛 Troubleshooting](#troubleshooting) | Common issues     |

---

## ✨ Features

- ✅ Real-time risk dashboard with student filtering
- ✅ 7-day behavioral history per student
- ✅ Live data feed with SSE streaming
- ✅ SMOTE-balanced ML ensemble (200 → 412 samples)
- ✅ Encrypted identity vault (counselor-only access)
- ✅ System audit logging for compliance
- ✅ Responsive UI with Recharts visualizations

---

## ⚙️ Setup & Installation

### Prerequisites

```bash
Python 3.12+ | Node.js 18+ | MongoDB Atlas | Git
```

### Quick Start (5 Steps)

```bash
# 1. Clone
git clone https://github.com/RajeshKumarYadav12/Student-Wellness-Intelligence-System.git

# 2. Environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# 3. Install
pip install -r requirements.txt backend/requirements.txt
cd frontend && npm install

# 4. ML Pipeline
python data/generate.py          # 12,000 behavioral entries
python data/seed_mongo.py        # Load to MongoDB
python models/features.py        # Extract 18 features
python models/train.py           # Train model (2-3 min, F1=0.975)

# 5. Run
cd backend && uvicorn main:app --reload --port 8000
# Terminal 2: cd frontend && npm run dev
```

**Environment Variables (.env)**

```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/aura_db
AURA_SALT=your_random_salt
COUNSELLOR_KEY=your_encryption_key
```

---

## 🔌 API Documentation

### Base URL

```
Development: http://localhost:8000
Production: https://student-wellness-intelligence-system.onrender.com
```

### Key Endpoints

| Endpoint                | Method | Description                        |
| ----------------------- | ------ | ---------------------------------- |
| `/api/students`         | GET    | List all students with risk scores |
| `/api/students/{id}`    | GET    | 7-day behavioral history           |
| `/api/alerts`           | GET    | Critical/high risk students        |
| `/api/alerts/analytics` | GET    | Risk distribution stats            |
| `/api/feed/live`        | GET    | Real-time SSE updates              |
| `/api/health`           | GET    | Server status                      |

### Example Response

```json
{
  "success": true,
  "data": {
    "student_id": "STU#EEAADFF0",
    "risk_score": 0.85,
    "risk_level": "High",
    "anomaly_score": 0.92
  }
}
```

---

## 🛠️ Technology Stack

| Layer          | Technology                                    |
| -------------- | --------------------------------------------- |
| **Frontend**   | React 18.2, Recharts, Lucide, Vite            |
| **Backend**    | FastAPI 0.109, Uvicorn, Motor                 |
| **ML**         | scikit-learn 1.4, XGBoost 2.0.3, RandomForest |
| **Database**   | MongoDB Atlas                                 |
| **Data**       | pandas 2.2.3, NumPy 1.26.3                    |
| **Deployment** | Render (backend), Vercel (frontend)           |

---

## 📊 Model Performance

| Metric         | Score   | Status      |
| -------------- | ------- | ----------- |
| **F1 Score**   | 0.975   | ✅ Exceeded |
| **Precision**  | 0.98    | ✅ Exceeded |
| **Recall**     | 0.97    | ✅ Exceeded |
| **Model Size** | 3.62 MB | ✅ Met      |

**Risk Distribution (200 students):**

- 🔴 Critical: 13 (Immediate intervention)
- 🟠 High: 27 (24-48 hour follow-up)
- 🟡 Medium: 57 (Weekly check-in)
- 🟢 Low: 103 (Routine monitoring)

---

## 🚀 Deployment

### Backend → Render

1. Go to render.com, connect GitHub
2. New Web Service → Select repo
3. Root: `backend` | Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: MONGO_URI, AURA_SALT, COUNSELLOR_KEY
6. Deploy ✅

### Frontend → Vercel

1. Go to vercel.com, import repo
2. Root: `frontend`
3. Add env: `VITE_API_URL=<render-backend-url>`
4. Deploy ✅

**Total time: ~15 minutes**

---

## 🐛 Troubleshooting

### MongoDB Connection Failed

```bash
# Check connection string
echo $MONGO_URI

# Verify IP whitelist in MongoDB Atlas
# Verify credentials are correct
```

### Frontend Won't Connect

```bash
# Check VITE_API_URL
cat frontend/.env.local

# Clear browser cache (Ctrl+Shift+R)
# Verify CORS in backend/main.py
```

### Model Won't Load

```bash
# Train model if missing
python models/train.py

# Verify Python 3.12.x
python --version

# Check scikit-learn 1.4.0+
pip show scikit-learn
```

### API Returns 404

```bash
# Restart backend
cd backend && uvicorn main:app --reload --port 8000

# Verify routes imported in main.py
grep "include_router" backend/main.py
```

---

## 📁 Project Structure

```
AURA/
├── backend/           # FastAPI app
│   ├── main.py
│   ├── db.py
│   └── routers/
├── frontend/          # React dashboard
│   ├── src/
│   │   └── AuraDashboard.jsx
│   └── package.json
├── data/              # Data generation
│   ├── generate.py
│   └── seed_mongo.py
├── models/            # ML pipeline
│   ├── train.py
│   ├── evaluate.py
│   └── saved/
└── README.md
```

---

## 📞 Support

- **API Docs:** http://localhost:8000/docs (Swagger)
- **GitHub:** https://github.com/RajeshKumarYadav12/Student-Wellness-Intelligence-System
- **Issues:** Create GitHub issue
- **Live Backend:** https://student-wellness-intelligence-system.onrender.com

---

**Version:** 1.0.0 | **Status:** ✅ Production Ready | **F1 Score:** 97.5%

Made with ❤️ for university wellness and student mental health
