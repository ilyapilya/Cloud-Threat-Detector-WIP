---
name: CloudGuard SaaS Build Plan
description: 7-day SaaS productization plan for Cloud-Threat-Detector, tech stack decisions, and current build state
type: project
---

This project (Cloud-Threat-Detector) is being productized as "CloudGuard" — a cloud security scanner SaaS.

**Why:** Maximize ROI from the existing scanner codebase. Goal is a live product at the end of 7 days.

**Tech Stack:**
- Frontend: Vite + React 18 + Tailwind CSS + shadcn/ui (in `web/`)
- Backend: FastAPI (existing `backend/` — functions as the `/api` of the monorepo)
- Auth: Clerk (VITE_CLERK_PUBLISHABLE_KEY)
- DB: Supabase / PostgreSQL (VITE_SUPABASE_URL + VITE_SUPABASE_ANON_KEY)
- AI Remediation: Anthropic Claude Sonnet (user's own API key)
- Payments: Stripe Checkout (Day 5, not yet built)
- Deploy: Vercel (frontend) + Railway (backend)

**How to apply:** All frontend work lives in `web/`. Backend API work lives in `backend/`. Supabase schema is in `supabase/schema.sql`.

**Live URLs:**
- Frontend (Vercel): cloudguard.vercel.app (or similar)
- Backend (Railway): https://cloudguard-production.up.railway.app

**Current state (Day 2 complete):**
- Backend live on Railway at https://cloudguard-production.up.railway.app
- 14 AWS security checks implemented in `backend/app/scanner/aws_checks.py`
- API endpoints: POST /api/v1/scan, GET /api/v1/scan/{id}, GET /api/v1/scan/{id}/findings
- Async background scan with scoring (A-F grade)
- DB connected to Supabase (DATABASE_URL set in Railway)
- Supabase migration run: user_id nullable on scans table

**Day 3 TODO — Results Dashboard:**
- Add VITE_API_URL=https://cloudguard-production.up.railway.app to Vercel env vars
- Build credential input page (AWS key + secret + region form)
- Build scan results page (findings list, severity badges, score/grade)
- Build scan history page
- Wire frontend → backend end-to-end

**Pricing model:** Free (5 findings/scan) | Pro $29/mo (unlimited + AI remediation)
