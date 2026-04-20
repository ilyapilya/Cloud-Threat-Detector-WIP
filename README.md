# CloudGuard

AWS security scanner SaaS. Runs 14 security checks against an AWS account in under 60 seconds and returns a scored, graded report with AI-generated remediation steps.

**Live:** [cloudguard-nine.vercel.app](https://cloudguard-nine.vercel.app)  
**API:** [cloudguard-production.up.railway.app](https://cloudguard-production.up.railway.app)

---

## Stack

| Layer | Service | Purpose |
|---|---|---|
| Frontend | Vite + React 18 + Tailwind + shadcn/ui | SPA |
| Auth | Clerk | Sign-in, sign-up, JWT |
| Backend | FastAPI + SQLAlchemy | REST API, background scan jobs |
| Database | Supabase (PostgreSQL) | Persistent storage, RLS |
| Hosting (frontend) | Vercel | Auto-deploy on push to `main` |
| Hosting (backend) | Railway | Docker container, auto-deploy |
| Email | Resend | Weekly digest emails |
| Payments | Stripe | Pro plan checkout + webhooks |
| AI | Anthropic Claude | Remediation generation (cached) |
| AWS scanning | boto3 + moto (tests) | 14 security checks |

---

## Monorepo layout

```
/
├── backend/                  FastAPI application
│   ├── app/
│   │   ├── main.py           Entry point, CORS, lifespan (APScheduler)
│   │   ├── models.py         SQLAlchemy models (User, Scan, Finding)
│   │   ├── schemas.py        Pydantic request/response schemas
│   │   ├── deps.py           DB session + Clerk JWT → user_id
│   │   ├── database.py       SQLAlchemy engine (DATABASE_URL)
│   │   ├── routes/
│   │   │   ├── scan_routes.py        POST/GET /api/v1/scan(s)
│   │   │   ├── schedule_routes.py    POST /api/v1/scan/{id}/schedule
│   │   │   ├── remediation_routes.py POST /api/v1/findings/{id}/remediate
│   │   │   ├── stripe_routes.py      POST /api/v1/stripe/checkout, GET /api/v1/me
│   │   │   └── webhook_routes.py     POST /api/v1/webhooks/stripe
│   │   ├── scanner/
│   │   │   └── aws_checks.py         14 AWS security checks + scoring
│   │   └── services/
│   │       ├── email.py              Resend weekly digest
│   │       ├── scheduler.py          APScheduler (Monday 09:00 UTC)
│   │       └── remediation.py        Claude AI fix generation + global cache
│   ├── tests/
│   │   ├── conftest.py               Fake AWS env vars for moto
│   │   └── test_aws_checks.py        45 unit tests (all 14 checks + scoring)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── web/                      Vite + React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   ├── Dashboard.jsx         Scan history from API
│   │   │   ├── NewScan.jsx           Credential form → POST /scan
│   │   │   ├── ScanResults.jsx       Polling + findings + AI fix + share
│   │   │   ├── History.jsx           Full scan history + GradeTimeline
│   │   │   └── Share.jsx             Public shareable report (no auth)
│   │   ├── components/
│   │   │   ├── AppNav.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── scan/
│   │   │       ├── CredentialForm.jsx
│   │   │       ├── ScanProgress.jsx
│   │   │       ├── ScoreCard.jsx
│   │   │       ├── FindingsList.jsx   Pro gate at finding index 5
│   │   │       ├── FindingCard.jsx    Expandable, locked/unlocked
│   │   │       ├── RemediationPanel.jsx  AI fix (CLI + steps)
│   │   │       ├── HistoryCard.jsx
│   │   │       ├── GradeTimeline.jsx  SVG sparkline
│   │   │       └── ShareCard.jsx     OG-ready public card
│   │   └── lib/
│   │       └── api.js                All API calls (auth + public)
│   └── .env                         Local env vars (see below)
│
├── supabase/
│   ├── schema.sql                   Initial schema + RLS policies
│   └── migrations/
│       └── 001_nullable_user_id.sql
│
├── memory/                          Project context for AI sessions
├── pyproject.toml                   pytest config (testpaths, pythonpath)
└── railway.json                     Railway build config
```

---

## Security checks (14 total)

| # | Check | Severity |
|---|---|---|
| 1 | S3 public access block missing/incomplete | Critical |
| 2 | S3 versioning disabled | Low |
| 3 | Security group allows all inbound traffic | Critical |
| 4 | Security group exposes dangerous port (SSH/RDP/DB) | High |
| 5 | IAM user has console access but no MFA | High |
| 6 | Root account has active access keys | Critical |
| 7 | Root account MFA not enabled | Critical |
| 8 | IAM password policy too weak / not set | Medium |
| 9 | CloudTrail not logging | High |
| 10 | EBS volume unencrypted | Medium |
| 11 | RDS instance publicly accessible | High |
| 12 | GuardDuty not enabled | Medium |
| 13 | EC2 instance has public IP | Low |

**Scoring:** 100 − deductions (Critical −20, High −10, Medium −5, Low −2). Grades: A ≥85, B ≥70, C ≥50, D ≥30, F <30.

---

## Local development

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Supabase project (free tier)
- A Clerk application (free tier)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill in env vars
cp .env.example .env

uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### Frontend

```bash
cd web
npm install

# Copy and fill in env vars
cp .env.example .env

npm run dev
# → http://localhost:5173
```

### Tests

```bash
# From repo root
pip install -r backend/requirements-dev.txt
pytest -v

# Targeted
pytest -v -k "S3"
pytest -v -k "violation"
```

---

## Environment variables

### Backend (`backend/.env` + Railway)

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | Supabase PostgreSQL URI | Yes |
| `RESEND_API_KEY` | Resend API key for email digest | Yes (Day 4) |
| `RESEND_FROM` | From address, e.g. `CloudGuard <reports@yourdomain.com>` | No |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI remediation | Yes (Day 5) |
| `STRIPE_SECRET_KEY` | Stripe secret key | Yes (Day 5) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | Yes (Day 5) |
| `STRIPE_PRICE_ID` | Stripe price ID for Pro plan (`price_xxx`) | Yes (Day 5) |
| `FRONTEND_URL` | Your Vercel URL, added to CORS origins | No |

### Frontend (`web/.env` + Vercel)

| Variable | Description | Required |
|---|---|---|
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (`pk_live_xxx`) | Yes |
| `VITE_API_URL` | Railway backend URL | Yes |
| `VITE_SUPABASE_URL` | Supabase project URL | Yes |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key | Yes |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (`pk_live_xxx`) | Yes (Day 5) |

---

## Database setup (Supabase)

Run in the Supabase SQL Editor in order:

```sql
-- 1. Initial schema
-- Paste contents of supabase/schema.sql

-- 2. Allow scans without a user (unauthenticated)
ALTER TABLE scans ALTER COLUMN user_id DROP NOT NULL;

-- 3. Day 4 — weekly email opt-in
ALTER TABLE scans ADD COLUMN IF NOT EXISTS notify_weekly BOOLEAN DEFAULT false;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS notify_email  TEXT;

-- 4. Day 5 — user plan tracking
ALTER TABLE users ADD COLUMN IF NOT EXISTS plan               TEXT DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS email              TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
```

---

## Deployment

### Railway (backend)

1. New project → Deploy from GitHub repo
2. Set **Root Directory** to `backend`
3. Set **Dockerfile path** to `backend/Dockerfile`
4. Add all backend environment variables under **Variables**
5. Railway auto-deploys on every push to `main`

**Stripe webhook:**  
After first deploy, go to Stripe Dashboard → Developers → Webhooks → Add endpoint:  
URL: `https://<your-railway-url>/api/v1/webhooks/stripe`  
Event: `checkout.session.completed`  
Copy the signing secret → add as `STRIPE_WEBHOOK_SECRET` in Railway.

### Vercel (frontend)

1. Import GitHub repo → set **Root Directory** to `web`
2. Framework: Vite (auto-detected)
3. Add all frontend environment variables
4. Vercel auto-deploys on every push to `main`

**SPA routing:** `web/vercel.json` already contains the rewrite rule for React Router.

---

## API reference

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | — | Health check |
| `POST` | `/api/v1/scan` | Optional | Create scan, validate credentials, start background job |
| `GET` | `/api/v1/scan/{id}` | — | Poll scan status |
| `GET` | `/api/v1/scan/{id}/findings` | — | Get findings (used by share page) |
| `GET` | `/api/v1/scans` | Required | List all scans for authenticated user |
| `POST` | `/api/v1/scan/{id}/schedule` | Required | Opt into weekly email digest |
| `POST` | `/api/v1/findings/{id}/remediate` | Required | Get AI fix (cached per finding type) |
| `GET` | `/api/v1/me` | Required | Get current user's plan |
| `POST` | `/api/v1/stripe/checkout` | Required | Create Stripe Checkout Session |
| `POST` | `/api/v1/webhooks/stripe` | — (signed) | Handle Stripe events |

Full interactive docs available at `/docs` on any running instance.

---

## Monetization

**Free plan:** Run scans, view all findings, AI fix for findings 1–5.  
**Pro plan ($29/month):** AI fix for all findings, shareable reports, weekly digest emails.

Upgrade flow: paywall CTA in findings → Stripe Checkout → webhook → `users.plan = 'pro'`.
