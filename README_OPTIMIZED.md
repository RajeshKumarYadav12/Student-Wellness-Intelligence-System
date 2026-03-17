# 🛡️ AURA — Student Wellness Intelligence System

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com) [![React](https://img.shields.io/badge/React-18.2-blue)](https://reactjs.org) [![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248)](https://mongodb.com) [![F1_Score](https://img.shields.io/badge/F1_Score-97.5%25-brightgreen)](https://scikit-learn.org) [![FERPA](https://img.shields.io/badge/FERPA-Compliant-success)](https://www2.ed.gov/policy/gen/guid/fpco/ferpa/)

**Privacy-First AI System for Early Mental Health Intervention in Universities**

AURA analyzes behavioral metadata (login patterns, WiFi zones, assignment submission times) to identify students at risk of mental health crises. **No invasive monitoring—only anonymized behavioral signals with FERPA compliance.**

---

## 📋 Quick Navigation

| Section                                     | Content                                                  |
| ------------------------------------------- | -------------------------------------------------------- |
| ✨ [Features](#-features)                   | Real-time dashboard, ML pipeline, privacy architecture   |
| 🔍 [What AURA Detects](#-what-aura-detects) | Sleep disruption, social isolation, academic drift, etc. |
| 📦 [Prerequisites](#-prerequisites)         | Python 3.13+, Node.js 18+, MongoDB Atlas                 |
| 🚀 [Quick Start](#-quick-start)             | Local development setup (10 minutes)                     |
| 🎯 [Model Performance](#-model-performance) | 97.5% F1 Score, 98% Precision                            |
| 🌐 [Deployment](#-deployment)               | Render (backend) + Vercel (frontend)                     |

---

## ✨ Features

### Dashboard

- 🎯 **Risk Filtering**: Critical (13), High (27), Medium (57), Low (103) students
- 📊 **Real-Time Feed**: Server-Sent Events (SSE) for live updates
- 👤 **Student Details**: 7-day behavioral history with AI insights
- 🔔 **Notifications**: System alerts in bottom-right panel

### Machine Learning

- 🤖 **Ensemble Model**: IsolationForest + XGBoost (60%) + RandomForest (40%)
- 📈 **18 Features**: Rolling averages, Z-scores, behavioral signals
- ⚖️ **SMOTE Balancing**: 200 → 412 balanced samples for minority class
- 🎲 **5-Fold Cross-Validation**: Robust performance estimation

### Privacy & Security

- 🔐 **SHA-256 Pseudonymization**: Student IDs hashed (e.g., `STU#EEAADFF0`)
- 🗝️ **AES-256-GCM Encryption**: Identity vault (counselor-only access)
- 📝 **Audit Logging**: Every identity reveal tracked
- ⏰ **TTL Policy**: Behavioral logs auto-deleted after 90 days

---

## 🔍 What AURA Detects

| Signal                 | Indicator          | Example                                         |
| ---------------------- | ------------------ | ----------------------------------------------- |
| **Sleep Disruption**   | Login timestamps   | Consecutive 1:00-5:00 AM logins                 |
| **Social Isolation**   | WiFi zone patterns | 85%+ dorm time for 7+ days                      |
| **Academic Drift**     | Submission timing  | Shift from 48hrs early → 30mins before deadline |
| **Routine Collapse**   | Activity variance  | Login time variance >4 hours                    |
| **Engagement Decline** | Location diversity | 60%+ drop in library/cafeteria visits           |

**AURA Does NOT Monitor:** ❌ Messages, ❌ Browser history, ❌ Cameras, ❌ Social media, ❌ Grades

---

## 📦 Prerequisites

- **Python 3.13+** — https://python.org/downloads
- **Node.js 18+ & npm** — https://nodejs.org
- **MongoDB Atlas** (Free tier) — https://mongodb.com/cloud/atlas
- **Git** — https://git-scm.com/downloads

---

## 🚀 Quick Start

### 1️⃣ Clone & Setup Environment

```bash
git clone https://github.com/RajeshKumarYadav12/Student-Wellness-Intelligence-System.git
cd Student-Wellness-Intelligence-System
cp .env.example .env
```

### 2️⃣ Configure `.env`

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/aura_db
AURA_SALT=your_32_random_characters_here
COUNSELLOR_KEY=your_32_random_characters_here
```

### 3️⃣ Install Dependencies

```bash
# Python
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 4️⃣ Generate Data & Train Model

```bash
python data/generate.py        # 12,000 behavioral entries
python data/seed_mongo.py      # Upload to MongoDB
python models/features.py      # Extract 18 features
python models/train.py         # Train ensemble (2-3 min)
```

### 5️⃣ Run Locally

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

✅ **Backend**: http://localhost:8000/docs  
✅ **Frontend**: http://localhost:3000

---

## 🎯 Model Performance

| Metric           | Score   | Status                      |
| ---------------- | ------- | --------------------------- |
| **F1 Score**     | 0.975   | ✅ Exceeds 0.92-0.96 target |
| **Precision**    | 0.98    | ✅ Exceeds 0.90 target      |
| **Recall**       | 0.97    | ✅ Exceeds 0.90 target      |
| **Model Size**   | 3.62 MB | ✅ Under 10 MB              |
| **API Response** | ~50ms   | ✅ Under 200ms              |

**Risk Distribution (200 students):**

- 🔴 Critical: 13 (6.5%) → Immediate intervention
- 🟠 High: 27 (13.5%) → 24-48 hour follow-up
- 🟡 Medium: 57 (28.5%) → Weekly check-in
- 🟢 Low: 103 (51.5%) → Routine monitoring

---

## 🌐 Deployment

### Backend → Render

1. Go to https://render.com → Connect GitHub
2. New Blueprint → Select repo
3. Set environment variables: `MONGODB_URI`, `AURA_SALT`, `COUNSELLOR_KEY`
4. Deploy ✅ → Get backend URL

### Frontend → Vercel

1. Go to https://vercel.com → Connect GitHub
2. Import repo → Root directory: `frontend`
3. Add `REACT_APP_API_URL=<your-render-backend-url>`
4. Deploy ✅ → Live dashboard

**Total deployment time: ~15 minutes**

---

## 📂 Project Structure

```
├── backend/              # FastAPI server
│   ├── main.py          # API entry point
│   ├── db.py            # MongoDB connection
│   └── routers/         # /api endpoints
├── frontend/            # React dashboard
│   └── src/
│       └── AuraDashboard.jsx
├── data/                # Data generation
│   ├── generate.py      # Synthetic data
│   └── seed_mongo.py    # MongoDB loader
├── models/              # ML pipeline
│   ├── train.py         # Ensemble training
│   ├── features.py      # Feature extraction
│   └── evaluate.py      # Model evaluation
└── render.yaml          # Deployment config
```

---

## 🛠️ Tech Stack

| Layer    | Technology                          |
| -------- | ----------------------------------- |
| Frontend | React 18.2, Recharts, Lucide Icons  |
| Backend  | FastAPI 0.109, Uvicorn, Motor       |
| Database | MongoDB Atlas                       |
| ML       | scikit-learn, XGBoost, RandomForest |
| Data     | pandas 2.2, NumPy 1.26              |

---

## 📞 Support & Documentation

- **API Docs**: `/docs` (Swagger UI)
- **Live Backend**: https://student-wellness-intelligence-system.onrender.com
- **Code**: https://github.com/RajeshKumarYadav12/Student-Wellness-Intelligence-System
- **Issues**: Open on GitHub

---

## 📜 License

MIT License — See LICENSE file for details

---

**🎉 AURA: Where Privacy Meets Wellness Intelligence**
