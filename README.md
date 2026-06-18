# Campus Registry — Complaint Prioritization System

A full-stack web app for educational institutions to file, automatically classify,
prioritize, and escalate student complaints through a hierarchical approval
workflow (HOD → Dean → Final Authority).

```
complaint-system/
  backend/    Django + DRF REST API, SQLite/MySQL, TF-IDF + Logistic Regression NLP engine
  frontend/   React (Vite) single-page app
```

## What's included

- **Authentication** — username/password login with JWT access + refresh tokens, one of four roles: Student, HOD, Dean, Final Authority.
- **NLP classification** — a TF-IDF vectorizer feeds two Logistic Regression models (category + priority), trained on a bundled labeled dataset of ~180 example complaints. A safety-keyword guardrail (fire, threats, harassment, etc.) forces High priority even if the model is unsure.
- **Auto-routing** — every new complaint is assigned to an HOD immediately, with an SLA deadline based on its priority (High: 24h, Medium: 72h, Low: 168h — configurable in `settings.py`).
- **Escalation engine** — a management command (`check_escalations`) walks all open complaints and bumps anything past its deadline to the next authority level (HOD → Dean → Final Authority). Authorities can also escalate manually from the UI.
- **Status tracking & notifications** — every action (classified, assigned, escalated, resolved) is logged to a per-complaint history timeline, and triggers an in-app notification to the relevant student/authority.
- **Dashboards** — role-aware: students see their own filed complaints, authorities see their current queue, both see live stat cards.

## Quick start

### 1. Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data        # creates demo users + sample complaints
python manage.py runserver        # http://localhost:8000
```

The first request that needs the NLP model will auto-train it from
`complaints/ml/training_data.py` and cache the result in
`complaints/ml/artifacts/` — no separate training step required.

**Demo accounts** (password for all: `password123`):

| Username  | Role                     |
|-----------|--------------------------|
| student1  | Student                  |
| student2  | Student                  |
| hod_cse   | HOD — CSE department     |
| hod_ece   | HOD — ECE department     |
| dean1     | Dean                     |
| final1    | Final Authority          |

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

It talks to the API at `http://localhost:8000/api` by default — change this
in `frontend/.env` (`VITE_API_BASE_URL`) if your backend runs elsewhere.

### 3. Run the escalation checker on a schedule

This is what actually enforces SLA deadlines. In development, run it manually
or via cron:

```bash
python manage.py check_escalations
```

In production, schedule it every few minutes with cron, a systemd timer, or
Celery beat.

## Switching to MySQL

By default the app uses SQLite (zero setup). To use MySQL instead:

```bash
pip install mysqlclient
export DB_ENGINE=mysql
export DB_NAME=complaint_system
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306
python manage.py migrate
```

(`mysqlclient` needs MySQL's client dev headers installed on your system —
`libmysqlclient-dev` on Debian/Ubuntu, `mysql-client` via Homebrew on macOS.)

## API overview

All endpoints are under `/api/`. Auth uses JWT — log in to get an
`access`/`refresh` pair, then send `Authorization: Bearer <access>`.

| Endpoint                                   | Method | Who               | Purpose |
|---------------------------------------------|--------|--------------------|---------|
| `/auth/register/`                          | POST   | anyone             | create an account |
| `/auth/login/`                             | POST   | anyone             | get JWT tokens |
| `/auth/login/refresh/`                     | POST   | anyone             | refresh access token |
| `/auth/me/`                                | GET    | authenticated      | current user profile |
| `/complaints/`                             | GET    | authenticated      | list (own complaints for students, current queue for authorities) |
| `/complaints/`                             | POST   | student            | file a complaint (auto-classified) |
| `/complaints/{id}/`                        | GET    | owner/assigned     | full detail + history |
| `/complaints/{id}/update_status/`          | POST   | assigned authority | `{status, notes}` |
| `/complaints/{id}/escalate/`               | POST   | assigned authority | `{reason}` — bump to next level |
| `/complaints/{id}/resolve/`                | POST   | assigned authority | `{notes}` |
| `/complaints/stats/`                       | GET    | authenticated      | dashboard counts |
| `/notifications/`                          | GET    | authenticated      | own notifications |
| `/notifications/{id}/read/`                | POST   | authenticated      | mark one as read |
| `/notifications/read-all/`                 | POST   | authenticated      | mark all as read |

The full admin UI is also available at `/admin/` (create a superuser with
`python manage.py createsuperuser`, or use the seeded `admin` account).

## Known simplifications (good next steps if you extend this)

- Authority routing is by **role**, not by a specific person — any HOD can
  act on any complaint sitting at the HOD level (department-aware
  assignment exists, but multiple HODs in the same department would share
  a queue). Tightening this to assigned-person-only is a permissions change
  in `accounts/permissions.py` + `complaints/views.py`.
- The NLP training set (`complaints/ml/training_data.py`) is a small,
  hand-labeled demo dataset. Swap in real historical complaint data and
  retrain (`python manage.py shell -c "from complaints.ml.train_model import train; train()"`)
  for production-quality predictions.
- Notifications are in-app only (no email/SMS) — `notifications/services.py`
  is the single place to add a delivery channel.
- The escalation checker is a manual/cron command rather than a background
  worker — swap in Celery beat for true async scheduling if needed.
