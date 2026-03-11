# 🛡️ AURA — Student Wellness Intelligence System

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com) [![React](https://img.shields.io/badge/React-18.2-blue)](https://reactjs.org) [![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248)](https://mongodb.com) [![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-orange)](https://scikit-learn.org) [![XGBoost](https://img.shields.io/badge/XGBoost-3.2-red)](https://xgboost.ai)

**Privacy-First AI System for Early Mental Health Intervention in Universities**

AURA (Automated University Risk Assessment) analyzes behavioral metadata—login patterns, WiFi zones, assignment submission times—to identify students showing early warning signs of mental health crises. **No message content, no cameras, no invasive monitoring**. Results appear on a real-time counselor dashboard enabling proactive intervention while preserving student privacy.

![AURA Dashboard](https://img.shields.io/badge/F1_Score-97.5%25-brightgreen) ![Students Monitored](https://img.shields.io/badge/Students-200-blue) ![Predictions](https://img.shields.io/badge/Predictions-Real--Time-orange) ![Privacy](https://img.shields.io/badge/FERPA-Compliant-success)

---

## 📋 Table of Contents
- [Features](#-features)
- [What AURA Detects](#-what-aura-detects)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start-local-setup)
- [Project Output](#-project-output--expected-results)
- [Privacy & Security](#-privacy--security)

---

## ✨ Features

### **Real-Time Monitoring Dashboard**
- 🎯 **Risk-Based Filtering**: Click KPI cards to filter by Critical (13), High (27), or Medium (57) risk levels
- 📊 **Live Data Feed**: Server-Sent Events (SSE) for real-time prediction updates
- 🎨 **Interactive UI**: Color-coded risk badges, behavioral trend sparklines, hover animations
- 👤 **Student Detail Modal**: Click "View" to see 7-day behavioral history, trends, and AI recommendations
- 🔔 **Notification System**: Bottom-right panel shows recent system updates

### **Machine Learning Pipeline**
- 🤖 **Ensemble Model**: IsolationForest + XGBoost (60%) + RandomForest (40%) = **97.5% F1 Score**
- 📈 **Feature Engineering**: 18 features including rolling averages, Z-scores, isolation streaks
- ⚖️ **SMOTE Balancing**: 200 → 412 balanced samples for improved minority class detection
- 🎲 **Cross-Validation**: 5-fold StratifiedKFold for robust performance estimates

### **Privacy-First Architecture**
- 🔐 **Pseudonymization**: SHA-256 hashed student IDs (e.g., `STU#EEAADFF0`)
- 🗝️ **Encrypted Identity Vault**: AES-256-GCM encryption for real names (counselor-only access)
- 📝 **Audit Logging**: Every identity reveal tracked with timestamp, admin ID, and reason
- ⏰ **TTL Policy**: Behavioral logs auto-deleted after 90 days
- ✅ **FERPA Compliant**: No educational records accessed, only anonymized behavioral metadata

---

## 🔍 What AURA Detects

| Behavioral Signal      | Indicator                      | Example Pattern                                    |
|------------------------|--------------------------------|----------------------------------------------------|
| **Sleep Disruption**   | Login timestamps               | Consecutive logins only between 1:00–5:00 AM       |
| **Social Isolation**   | WiFi zone patterns             | 7+ consecutive days with 85%+ time in dorm room    |
| **Academic Drift**     | Assignment submission timing   | Shift from 48hrs early → 30mins before deadline    |
| **Routine Collapse**   | Daily activity irregularity    | Variance in login times >4 hours from baseline     |
| **Engagement Decline** | Campus location diversity      | Visits to library/cafeteria drop by 60%+ vs avg    |

**AURA Does NOT Monitor:**
- ❌ Message content (SMS, email, chat apps)
- ❌ Browser history or search queries
- ❌ Camera/microphone feeds
- ❌ Social media activity
- ❌ Academic performance (grades, test scores)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         🌐 FRONTEND (React)                             │
│  Dashboard → Charts → Live Feed → Student Details → Risk Filters        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP + SSE
┌────────────────────────────────▼────────────────────────────────────────┐
│                      🚀 BACKEND (FastAPI)                               │
│  /api/students  /api/alerts  /api/analytics  /api/feed/live            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Motor (async)
┌────────────────────────────────▼────────────────────────────────────────┐
│                    🗄️ MONGODB ATLAS (Cloud Database)                   │
│  • behavioral_logs (12,000 docs)  • students (200 docs)                │
│  • identity_vault (200 encrypted) • risk_predictions (200 docs)        │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                       🤖 ML PIPELINE (Python)                           │
│  IsolationForest → SMOTE → Ensemble (XGBoost + RandomForest)           │
│  → Risk Predictions (Critical/High/Medium/Low)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| **Layer**            | **Technology**                      | **Purpose**                                              |
|----------------------|-------------------------------------|----------------------------------------------------------|
| **Frontend**         | React 18.2, Recharts, Lucide Icons | Real-time dashboard with SSE live feed                   |
| **Backend**          | FastAPI 0.109, Uvicorn, Motor       | Async REST API + Server-Sent Events                      |
| **Database**         | MongoDB Atlas (Cloud)               | NoSQL for behavioral logs, predictions, identity vault   |
| **ML Framework**     | scikit-learn 1.6, XGBoost 3.2       | Ensemble model training & inference                      |
| **Data Processing**  | pandas 2.2, NumPy 2.0               | Feature engineering & time-series transformations        |
| **Explainability**   | SHAP 0.51                           | Model interpretability for counselor transparency        |
| **Containerization** | Docker, Docker Compose              | One-command deployment with service orchestration        |
| **CI/CD**            | GitHub Actions                      | Automated testing, linting, and deployment               |

---

## 📦 Prerequisites

Before running AURA locally, ensure you have:

- **Python 3.13+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+ & npm** ([Download](https://nodejs.org/))
- **MongoDB Atlas Account** (Free tier: [Sign up](https://www.mongodb.com/cloud/atlas))
- **Git** ([Download](https://git-scm.com/downloads))

---

## 🚀 Quick Start (Local Setup)

### **Step 1: Clone the Repository**

```bash
# Clone via HTTPS
git clone https://github.com/YOUR_USERNAME/aura.git
cd aura

# Or clone via SSH
git clone git@github.com:YOUR_USERNAME/aura.git
cd aura
```

### **Step 2: Set Up Environment Variables**

Create a `.env` file in the project root:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` with your MongoDB Atlas credentials:

```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
AURA_SALT=your_64_character_salt_for_pseudonymization_here_must_be_random
COUNSELLOR_KEY=your_46_character_encryption_key_for_identity_vault_random
MODEL_VERSION=v1.0
```

### **Step 3: Install Python Dependencies**

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn motor python-dotenv
```

### **Step 4: Install Frontend Dependencies**

```bash
cd frontend
npm install
cd ..
```

### **Step 5: Generate Synthetic Data & Train Model**

```bash
# Set environment variables (Windows PowerShell)
$env:MONGO_URI="your_mongodb_atlas_uri"
$env:AURA_SALT="your_salt"
$env:COUNSELLOR_KEY="your_key"

# Generate 200 students with 60 days of behavioral logs (12,000 entries)
python data/generate.py

# Seed MongoDB Atlas
python data/seed_mongo.py

# Extract 18 features (rolling averages, Z-scores, behavioral signals)
python models/features.py

# Train ensemble model (IsolationForest + XGBoost + RandomForest)
# Expected runtime: 2-3 minutes, F1 Score: 97.5%
python models/train.py
```

### **Step 6: Start Backend API**

```bash
# From project root, with virtual environment activated
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend accessible at: **http://localhost:8000**  
📚 API Documentation: **http://localhost:8000/docs**

### **Step 7: Start Frontend Dashboard**

In a **new terminal**:

```bash
cd frontend
npm start
```

✅ Dashboard opens automatically at: **http://localhost:3000**

---

## 📊 Project Output & Expected Results

### **Dashboard Preview**

```
┌────────────────────────────────────────────────────────────┐
│  🛡️ AURA - Student Wellness Intelligence    [🟢 LIVE]     │
├────────────────────────────────────────────────────────────┤
│  [13 CRITICAL]  [27 HIGH]  [57 MEDIUM]  [200 TOTAL]       │
├────────────────────────────────────────────────────────────┤
│  [Overview]  [Alerts]  [Analytics]                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Student Risk Overview                                      │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ ID          Risk Level  Anomaly  Sleep  Isolation   │  │
│  │ STU#xxx     🔴 Critical  95%     █████  ████████    │  │
│  │ STU#yyy     🟠 High      82%     ███    ██████      │  │
│  │ STU#zzz     🟡 Medium    67%     ██     ████        │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### **Model Performance**

| Metric       | Target  | Achieved  | Status   |
|--------------|---------|-----------|----------|
| F1 Score     | 0.92-0.96 | **0.975** | ✅ EXCEEDED |
| Precision    | >0.90     | **0.98**  | ✅ EXCEEDED |
| Recall       | >0.90     | **0.97**  | ✅ EXCEEDED |
| Model Size   | <10 MB    | **3.62 MB** | ✅ MET    |
| API Response | <200ms    | **~50ms** | ✅ EXCEEDED |

### **Risk Distribution**

- **Critical (13 students)** - Immediate intervention required
- **High (27 students)** - Counselor assignment recommended within 24-48 hours
- **Medium (57 students)** - Monitoring and check-in within 1 week
- **Low (103 students)** - Normal behavioral patterns, routine monitoring

---

## 🌐 Deployment

### **Quick Deploy (Production)**

AURA is ready to deploy to **Render + Vercel** (recommended) or AWS/Google Cloud.

**📖 [Step-by-Step Deployment Guide](./GITHUB_DEPLOY.md)**

#### Deploy in 3 Steps:

1. **Push to GitHub** (5 min)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/aura.git
   git push -u origin main
   ```

2. **Deploy Backend to Render** (5 min)
   - Go to [render.com](https://render.com) → Sign up with GitHub
   - New Web Service → Connect `aura` repo
   - Root Directory: `backend`
   - Add environment variables: `MONGODB_URI`, `AURA_SALT`, `COUNSELLOR_KEY`
   - Deploy → Copy backend URL

3. **Deploy Frontend to Vercel** (3 min)
   - Go to [vercel.com](https://vercel.com) → Sign up with GitHub
   - Import `aura` repo → Root Directory: `frontend`
   - Add env var: `REACT_APP_API_URL=<your-render-backend-url>`
   - Deploy → Your dashboard is live! 🎉

**💰 Cost:** $0-7/month (Free tier available)

**📚 Detailed Guides:**
- **[GitHub → Render → Vercel Guide](./GITHUB_DEPLOY.md)** - 15-minute deployment
- **[Full Deployment Options](./DEPLOYMENT.md)** - AWS, Google Cloud, DigitalOcean
- **[Local Development](./BUILD_AND_DEPLOY.md)** - Build scripts and testing

---

## 🔐 Privacy & Security

AURA is built with **privacy-first** principles:


| Rule                       | Implementation                                                      |
| -------------------------- | ------------------------------------------------------------------- |
| **No Real Names in DB**    | SHA-256 pseudonymization with salt (student IDs like `STU#8A3F`)    |
| **No Content Capture**     | Only timestamps & zone IDs — never message text or browser history  |
| **Counselor-Only Reveal**  | AES-256-GCM encrypted identity vault; every access logged for audit |
| **Data Retention**         | TTL index: behavioral logs auto-deleted after 90 days               |
| **Consent Gate**           | Students must opt-in; opt-out deletes all documents                 |
| **FERPA Compliant**        | No educational records accessed; behavioral metadata only           |

### Identity Vault Access Logging

Every time a counselor reveals a student's identity, the action is logged:

```json
{
  "admin_id": "dr.patel",
  "accessed_at": "2026-03-12T14:30:00Z",
  "student_id": "STU#EEAADFF0",
  "reason": "welfare check",
  "ip_address": "10.0.1.45"
}
```

---

## 🌐 API Documentation

Full interactive API documentation available at: **http://localhost:8000/docs** (Swagger UI)

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/students` | GET | List all students with latest risk predictions |
| `/api/students/{id}` | GET | Detailed risk breakdown + 7-day behavioral history |
| `/api/alerts` | GET | Critical/high risk students requiring intervention |
| `/api/alerts/{id}/assign` | POST | Assign counselor to student |
| `/api/alerts/analytics` | GET | Risk distribution statistics |
| `/api/feed/live` | GET | Server-Sent Events (SSE) for real-time updates |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Support

**Project Maintainer**: [Your Name](mailto:your.email@example.com)  
**Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/aura/issues)  
**Documentation**: [PROJECT_OUTPUT_SUMMARY.md](PROJECT_OUTPUT_SUMMARY.md)

---

## 🙏 Acknowledgments

- MongoDB Atlas for cloud database hosting
- FastAPI community for excellent async framework
- scikit-learn & XGBoost teams for ML libraries
- React & Recharts for frontend visualization tools
- All contributors to open-source mental health awareness

---

**AURA v1.0** | © 2026 | Built with ❤️ for student wellness
#   S t u d e n t - W e l l n e s s - I n t e l l i g e n c e - S y s t e m  
 