# 🏥 Medicy: AI-Powered Smart Triage & Hospital Management
### *Prioritizing lives with Intelligence*

Medicy is a high-performance **Healthcare Management System** that uses a hybrid **Machine Learning Pipeline** to automate patient triage. By analyzing vitals and symptoms in real-time, Medicy assigns medical priority scores and explains AI decisions using **Explainable AI (SHAP)**.

---

## 📺 Project Overview
*   **Mission:** Reduce Emergency Room wait times by intelligently routing patients to the right department.
*   **Target Audience:** Triage Officers, Doctors, and Hospital Administrators.
*   **Key Innovation:** A dual-stage ML model (XGBoost + Logistic Regression) paired with a real-time WebSocket dashboard.

---

## 🚀 Key Features

### 🧠 Intelligent Triage
*   **Automated Risk Scoring:** Real-time calculation of Low, Medium, or High risk levels.
*   **Smart Routing:** Instantly assigns patients to Cardiology, Neurology, Pulmonology, etc.
*   **Explainable AI (XAI):** Uses **SHAP TreeExplainer** to show clinicians exactly *why* a risk level was assigned.

### 💻 Unified Dashboards
*   **Reception/Triage View:** Quick patient intake with instant priority feedback.
*   **Doctor Cockpit:** Focused view of pending patients, categorized by medical urgency.
*   **Admin Analytics:** Data-driven insights into department load and risk distribution.

### 📱 Mobile Excellence
*   **Mobile-First Design:** Built on the Ionic framework for a premium look and feel.
*   **Android App:** Fully native Android project generated via Capacitor.
*   **PWA Ready:** Smooth, app-like experience even in the browser.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18 (TypeScript)
- **UI:** Ionic Framework (Android & iOS UI Patterns)
- **State Management:** React Hooks + WebSockets
- **Visuals:** Chart.js for real-time analytics

### Backend & AI
- **Framework:** FastAPI (Python 3.10+)
- **ML Models:** XGBoost Classifier & Logistic Regression
- **Explainability:** SHAP (Shapley Additive Explanations)
- **Database:** SQLite (Async via SQLAlchemy 2.0)

### Mobile & DevOps
- **Mobile runtime:** Capacitor 7.0
- **Automation:** GitHub Actions (Self-building APK Pipeline)

---

## 📂 Project Structure

```bash
frontend/
├── android/            # Native Android Project files
├── src/
│   ├── components/     # High-quality UI components (Navbar, StatsCards)
│   ├── pages/          # Dashboard views (Admin, Doctor, Triage)
│   └── api/            # Centralized Axios integration
├── assets/             # Branding & App Icons
└── .github/            # Automation (CI/CD)

backend/
├── services/           # ML Inference and SHAP logic
├── models/             # Database Schema
├── main.py             # FastAPI Server Entry
└── requirements.txt    # Python dependencies
```

---

## ⚙️ Installation & Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 📱 Mobile App (Android)
The project is already configured for Android. To build locally:
1. Ensure you have Android Studio and Java 21 installed.
2. Run:
```bash
cd frontend
npm run build
npx cap sync android
npx cap open android
```

---

## 🤖 CI/CD Build Pipeline
We have configured **GitHub Actions** to automatically build your APK. 
Every time you push code to the `main` branch, a new **Android APK** is generated and available in the **Actions** tab of the repository.

---

## 🤝 Team
Developed for the Kanini Hackathon. 🩺✨