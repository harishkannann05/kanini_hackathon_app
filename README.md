# 🏥 Smart Triage System

> **AI-Powered Emergency Triage & Smart Routing**

Smart Triage is an intelligent hospital management system that uses **Machine Learning** to prioritize patients based on their symptoms and vitals. It reduces emergency room wait times by automatically routing patients to the right department and predicting the severity of their condition.

## 🚀 Features

- **AI Risk Assessment**: Predicts patient risk levels (Low, Medium, High, Critical) using a trained ML model.
- **Smart Routing**: Automatically assigns patients to the correct medical department (Cardiology, Neurology, etc.).
- **Dynamic Prioritization**: Adjusts patient priority based on real-time vitals and symptoms.
- **SHAP Explainability**: Provides transparent reasoning for AI decisions.
- **Real-time Dashboard**: Live tracking of patient flow and waiting times.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+
- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **AI/ML**: Scikit-learn, SHAP, Pandas
- **Frontend**: HTML, CSS, Vanilla JavaScript

## 📂 Project Structure

```
backend/
├── api/                  # FastAPI endpoints
├── models/               # SQLAlchemy models
├── services/             # Business logic & AI services
├── scripts/              # Utility scripts (training, migration)
├── data/                 # Datasets and model files
└── main.py               # Application entry point

frontend/
├── index.html            # Main dashboard
├── login.html            # Authentication
├── patient_entry.html    # Patient registration
└── style.css             # Styling
```

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- SQLite (local file)

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
USE_SQLITE=1
JWT_SECRET=your_jwt_secret
```

### 3. Run Database Migrations

Apply the database schema:

```bash
python backend/scripts/migrate_schema.py
```

### 4. Train the AI Model

Generate and train the ML model:

```bash
python backend/scripts/train_model.py
```

### 5. Start the Server

```bash
python backend/main.py
```

The API will be available at `http://localhost:8000`.

## 🏃 Usage

### 1. Access the Dashboard

Open `frontend/index.html` in your browser.

### 2. Login

- **Username**: `admin`
- **Password**: `admin123`

### 3. Add Patients

- Click **"Add New Patient"**.
- Fill in the patient details (Age, Vitals, Symptoms).
- Click **"Submit"**.

### 4. View Triage Results

The dashboard will automatically display:
- **Risk Level**: Calculated by the AI model.
- **Recommended Department**: Where the patient should be sent.
- **SHAP Explanation**: Why the AI made this decision.
- **Priority Queue**: Real-time ordering of patients.

## 🧪 Testing

Run the verification script to test the core logic:

```bash
python backend/scripts/verify_logic_direct.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Create a feature branch (`git checkout -b feature/AmazingFeature`).
2. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
3. Push to the branch (`git push origin feature/AmazingFeature`).
4. Open a Pull Request.