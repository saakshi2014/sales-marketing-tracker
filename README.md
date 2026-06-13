---

## Firestore Collections

| Collection | Purpose |
|-----------|---------|
| users | User profiles with roles (7 users across 3 teams) |
| teams | Teams with members subcollection (3 teams) |
| leads | Lead pipeline data |
| pipeline_stages | 13 default + custom stages |
| audit_logs | Stage change history |
| tasks | Task assignments |
| notifications | In-app notifications |
| kpi_targets | KPI target values per employee |
| kpi_custom_columns | Custom KPI definitions |
| kpi_custom_entries | Employee KPI values |
| coaching_sessions | Coaching records |
| manager_reviews | Review meeting records |

---

## Local Setup

### Prerequisites
- Python 3.10+
- Git
- Firebase project with Firestore and Auth enabled

### Installation

```bash
# 1. Clone repository
git clone https://github.com/saakshi2014/sales-marketing-tracker.git
cd sales-marketing-tracker

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Mac/Linux

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Set up environment
copy .env.example .env          # Windows
cp .env.example .env            # Mac/Linux
# Fill in your Firebase credentials in .env

# 5. Add firebase-service-account.json to project root

# 6. Seed initial data (first time only)
python backend/seed_all.py
python backend/seed_demo_data.py
python backend/seed_new_teams.py

# 7. Run the application
cd backend
python app.py
```

Open: `http://127.0.0.1:5000`

---

## Docker Setup

```bash
docker compose up --build
```

Open: `http://localhost:5000`

---

## Demo Accounts

### Sales Team Alpha
| Role | Email | Password |
|------|-------|----------|
| Employee | employee@test.com | Test@1234 |
| M1 Manager | m1manager@test.com | Test@1234 |

### Sales Team Beta
| Role | Email | Password |
|------|-------|----------|
| Employee | employee2@test.com | Test@1234 |
| M1 Manager | m1manager2@test.com | Test@1234 |

### Sales Team Gamma
| Role | Email | Password |
|------|-------|----------|
| Employee | employee3@test.com | Test@1234 |
| M1 Manager | m1manager3@test.com | Test@1234 |

### Organisation Level
| Role | Email | Password |
|------|-------|----------|
| M2 Manager | m2manager@test.com | Test@1234 |

> **Note:** The M2 Manager has full visibility across all 3 teams.
> Each M1 Manager can only see their own team's data.
> Each Employee can only see their own leads and tasks.

---

## Running Tests

```bash
python backend/tests/test_all.py
```

Expected: 33/33 PASS

---

## Team Structure
M2 Manager (m2manager@test.com)

├── Sales Team Alpha

│   ├── M1 Manager (m1manager@test.com)

│   └── Employee   (employee@test.com)

├── Sales Team Beta

│   ├── M1 Manager (m1manager2@test.com)

│   └── Employee   (employee2@test.com)

└── Sales Team Gamma

├── M1 Manager (m1manager3@test.com)

└── Employee   (employee3@test.com)
---

## V1–V4 Acceptance Criteria

### V1 (Sprint 1) — All Passed ✅
1. All 3 roles log in and land on correct dashboard
2. Employee moves lead through all 13 pipeline stages
3. Every stage change creates an audit log entry
4. M1 sees team leads only — no cross-team data
5. M2 sees org-wide summary across all teams
6. Route protection — no dashboard access without login

### V2 (Sprint 2) — All Passed ✅
1. M1/M2 can create and assign tasks with priority and due date
2. Employee sees assigned tasks and updates status
3. Tasks past due date auto-flagged as Overdue
4. M2 sees consolidated task health across all teams
5. Employee notified on task assignment
6. M1 notified on task completion/overdue
7. M1/M2 can create/rename/deactivate custom stages
8. All 9 KPIs calculate correctly from pipeline data
9. KPI targets settable per employee
10. Employee KPI dashboard shows progress vs target

### V3 (Sprint 3) — All Passed ✅
1. Bar charts render on M1 and M2 dashboards
2. Funnel chart shows pipeline conversion
3. M2 date range filter updates all charts
4. M1 can log and track coaching sessions
5. M2 can schedule and track manager reviews
6. Firestore security rules enforce role isolation
7. CSV export works for all 4 data types
8. 33/33 regression tests pass

### V4 (Sprint 4) — All Passed ✅
1. Docker Compose builds and runs correctly
2. Pagination works for large lead datasets
3. Bulk CSV import creates leads in Firestore
4. Import error handling works correctly
5. Stages API uses caching
6. All previous acceptance criteria still pass

---

## SRS Compliance

| SRS Requirement | Status |
|----------------|--------|
| Highlander Rule — only 1 M2 Manager | ✅ Enforced at auth layer |
| Soft deletes — no data loss on deactivation | ✅ All deactivations use isActive flag |
| Audit trail — every stage change logged | ✅ audit_logs collection |
| Automatic overdue task flagging | ✅ Checked on every GET /api/tasks |
| Stage 6.2 excluded from active counts | ✅ isArchived filter applied |
| KPI target setting UI for managers | ✅ Set Targets modal on M1 dashboard |

---

## Security

- Firebase Authentication handles all identity
- JWT tokens verified server-side on every request
- Firestore Security Rules enforce collection-level access
- Highlander Rule prevents duplicate M2 Manager accounts
- Secret keys stored in .env (gitignored)
- Service account JSON gitignored
- Role-based access control on all 45 API routes

---

## Known Limitations

- Docker TLS issue on restricted networks (use home WiFi)
- Firestore test mode rules expire after 30 days
  (production rules implemented in Sprint 3)
- KPI trend chart uses estimated weekly buckets
- Email notifications not implemented (in-app only)

---

## Project Statistics

| Metric | Count |
|--------|-------|
| Development Days | 25 |
| Sprints | 4 |
| API Routes | 45 |
| Firestore Collections | 12 |
| Active Teams | 3 |
| Total Users | 7 |
| Regression Tests | 33 |
| Manual QA Tests | 40 |
| GitHub Version Tags | 30+ |

---

## Academic Information

- Student: Saakshi
- Registration: P05MG24S038019
- Institution: Mahatma Gandhi Memorial College, Udupi
- Program: Master of Science (Computer Science)
- Academic Year: 2025–26
- Project Duration: 25 development days (5 weeks)
- Development Methodology: Agile Scrum (4 sprints)
- Internal Guide: Mrs. Srinidhi Acharya
- GitHub Repository: https://github.com/saakshi2014/sales-marketing-tracker