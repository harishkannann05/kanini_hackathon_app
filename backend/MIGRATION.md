# Database Migration Guide

## Overview
The application supports both **SQLite (local development)** and **PostgreSQL/Supabase (production)**.

### Current Status
- ✓ **Local SQLite**: Fully populated with all datasets (60,000+ rows)
- ⏳ **Supabase PostgreSQL**: Ready to migrate when network is available

---

## Data Summary

| Table | Rows |
|-------|------|
| departments | 8 |
| doctors | 13 |
| disease_priority | 10,000 |
| symptom_severity | 10,000 |
| vital_signs_reference | 10,000 |
| chronic_condition_modifiers | 10,000 |
| doctor_specialization | 10,000 |
| focused_patient_dataset | 15,000 |
| **TOTAL** | **68,041** |

---

## Local Development (SQLite)

### Current .env
```
USE_SQLITE=1
```

### Run Migration
```bash
cd backend
python -m scripts.migrate_db
```

This will:
1. Create all tables
2. Seed 8 departments + 13 doctors
3. Import all 6 CSV datasets (~60K rows)
4. Build symptom→department cache
5. Verify data integrity

---

## Production Deployment (Supabase)

### Prerequisites
1. Network connectivity to Supabase
2. Update `.env` with correct credentials:

```bash
user=postgres
password=kanini@hackathon
host=db.fenkwvjteungvsjtwryz.supabase.co
port=5432
dbname=postgres
USE_SQLITE=0
```

### Migration Steps

**1. Create tables in Supabase:**
```bash
cd backend
python -m scripts.migrate_db
```

**2. Verify tables in Supabase Console:**
- Go to: https://app.supabase.com
- Select your project
- Check the **SQL Editor** → Tables section

**3. Verify in app:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Then test the API:
```bash
curl http://localhost:8000/stats
```

---

## Troubleshooting

### DNS Resolution Fails
If you see: `socket.gaierror: [Errno 11001] getaddrinfo failed`
- Check internet connectivity
- Verify hostname is correct: `db.fenkwvjteungvsjtwryz.supabase.co`
- Try from a different network

### Connection Refused
If you see: `psycopg2.OperationalError: connection refused`
- Verify credentials in `.env`
- Check that Supabase project is active
- Ensure IP whitelist allows your connection (if applicable)

### Tables Already Exist
To re-import (delete existing and re-create):
```bash
# Drop tables manually in Supabase console, then:
python -m scripts.migrate_db
```

---

## Data Cache

A symptom→department mapping cache is built during migration:
- **File**: `backend/data_cache.json`
- **Purpose**: Speed up triage lookups
- **Size**: ~296 symptom mappings
- **Auto-built**: Happens during migration step 4

---

## Files Involved

| File | Purpose |
|------|---------|
| `backend/scripts/migrate_db.py` | Main migration script (SQLite + PostgreSQL) |
| `backend/models.py` | ORM models for datasets |
| `backend/db.py` | Database connection logic |
| `dataset2/*.csv` | Source datasets |
| `backend/data_cache.json` | Generated symptom cache |

---

## Next Steps

1. ✅ **Local SQLite**: Full migration complete
2. ⏳ **Supabase**: Run migration when network available
3. 🔧 **Verify API**: Test endpoints with real data
4. 🚀 **Deploy**: Push to production

