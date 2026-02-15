# Database Migration Guide

## Overview
The application uses **SQLite** for all environments.

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

## Production Deployment

SQLite remains the supported database for production in this project.

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
| `backend/scripts/migrate_db.py` | Main migration script (SQLite) |
| `backend/models.py` | ORM models for datasets |
| `backend/db.py` | Database connection logic |
| `dataset2/*.csv` | Source datasets |
| `backend/data_cache.json` | Generated symptom cache |

---

## Next Steps

1. ✅ **SQLite**: Run migration and seed data
2. 🔧 **Verify API**: Test endpoints with real data
3. 🚀 **Deploy**: Push to production

