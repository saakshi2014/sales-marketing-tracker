# Sales & Marketing Performance Tracking System

**Masters Level Project — 2025–26**
Mahatma Gandhi Memorial College, Udupi
Submitted by: Saakshi | Reg No: P05MG24S038019

---

## About

A centralized web-based platform for sales and marketing performance
tracking. Supports three user roles with distinct access levels:
Employee, M1 Manager, and M2 Manager.

---

## V1 Features (Sprint 1 — Complete)

### Employee
- Add and manage leads with full contact details
- Move leads through 13 default pipeline stages
- View complete stage-change audit trail for every lead
- Edit lead details and archive leads
- Lead detail panel with quick actions

### M1 Manager
- View all leads across their team in one table
- Team stats bar — total, active, interested, meetings
- Stage distribution panel with progress bars
- Filter by stage, team member, or search by name
- View history of any team member's lead

### M2 Manager
- Organisation-wide stats across all teams
- Team cards with conversion rate indicators
- Drill-down from org → team → individual leads
- Org-wide stage distribution
- View history of any lead in the organisation

### All Roles
- Secure Firebase Authentication (email + password)
- JWT token verification on all API routes
- Role-based routing and route protection
- Responsive design — works on mobile and desktop
- Session management with auto-expiry

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript ES6+, Bootstrap 5 |
| Backend | Python 3.12 (Flask) |
| Database | Firebase Firestore |
| Auth | Firebase Authentication |
| Deployment | Docker (on-premises) |
| Version Control | Git / GitHub |

---

## Project Structure
```
sales-marketing-tracker/
├── backend/
│   ├── app.py                  # Flask application + routes
│   ├── firebase_config.py      # Firebase Admin SDK setup
│   ├── requirements.txt        # Python dependencies
│   ├── routes/
│   │   ├── auth.py             # Login, logout, session
│   │   ├── leads.py            # Lead CRUD + org routes
│   │   └── stages.py           # Pipeline stages API
│   ├── seed_users.py           # Seed 3 test users
│   ├── seed_stages.py          # Seed 13 pipeline stages
│   ├── seed_teams.py           # Seed test team
│   ├── seed_all.py             # Run all seeders
│   └── seed_demo_data.py       # Seed demo leads for V1
├── frontend/
│   ├── templates/
│   │   ├── base.html           # Master layout
│   │   ├── login.html          # Login page
│   │   ├── employee_dashboard.html
│   │   ├── m1_dashboard.html
│   │   └── m2_dashboard.html
│   └── static/
│       ├── css/main.css        # Global styles
│       └── js/
│           ├── main.js         # Global utilities
│           ├── leads.js        # Employee pipeline JS
│           ├── m1_dashboard.js # M1 dashboard JS
│           └── m2_dashboard.js # M2 dashboard JS
├── docker/
│   └── Dockerfile
├── docs/
│   └── SCHEMA.md               # Firestore data model
├── docker-compose.yml
├── .env.example                # Environment variables template
└── README.md
```

---

## Local Setup (Without Docker)

### Prerequisites
- Python 3.10 or higher
- Git
- Firebase project with Firestore and Authentication enabled

### Step 1 — Clone the repository
```bash
git clone https://github.com/saakshi2014/sales-marketing-tracker.git
cd sales-marketing-tracker
```

### Step 2 — Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 3 — Install dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4 — Set up environment variables
```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

Open `.env` and fill in your Firebase credentials.

### Step 5 — Add Firebase service account
Download your Firebase service account JSON from:
Firebase Console → Project Settings → Service Accounts → Generate new private key

Rename the file to `firebase-service-account.json` and place it
in the project root folder.

### Step 6 — Run the seeders (first time only)
```bash
python backend/seed_all.py
python backend/seed_demo_data.py
```

### Step 7 — Start the application
```bash
cd backend
python app.py
```

Open your browser at: `http://127.0.0.1:5000`

---

## Docker Setup (On-Premises)

### Prerequisites
- Docker Desktop installed and running

### Run with Docker
```bash
docker compose up --build
```

Open your browser at: `http://localhost:5000`

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Employee | employee@test.com | Test@1234 |
| M1 Manager | m1manager@test.com | Test@1234 |
| M2 Manager | m2manager@test.com | Test@1234 |

---

## Firestore Security Note

The Firestore database is currently running in **test mode**
(open read/write for 30 days). For production deployment,
full security rules should be implemented as defined in `docs/SCHEMA.md`.

---

## Sprint Progress

| Sprint | Weeks | Focus | Status |
|--------|-------|-------|--------|
| Sprint 1 | Week 1–2 | V1 Launch | ✅ Complete |
| Sprint 2 | Week 3–4 | Task Management | ⏳ Pending |
| Sprint 3 | Week 5–6 | KPIs & Charts | ⏳ Pending |
| Sprint 4 | Week 7–8 | Deploy & Polish | ⏳ Pending |

---

## V1 Acceptance Criteria (All Passed)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 3 roles can log in and access correct dashboard | ✅ |
| 2 | Employee can add a lead and move through all 13 stages | ✅ |
| 3 | Every stage change creates an audit log with user + timestamp | ✅ |
| 4 | M1 Manager can see all team leads (not other teams) | ✅ |
| 5 | M2 Manager can see org-wide summary across all teams | ✅ |
| 6 | Accessing dashboards without login redirects to login page | ✅