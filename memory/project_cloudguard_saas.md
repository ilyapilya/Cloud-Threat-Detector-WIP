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

**Current state (Day 1 complete):**
- `web/` scaffolded: React + Tailwind + shadcn/ui, landing page live, Clerk/Supabase stubs
- `supabase/schema.sql` created (users, scans, findings, waitlist tables with RLS)
- Auth pages ready — waiting for VITE_CLERK_PUBLISHABLE_KEY
- Waitlist form ready — waiting for Supabase project keys

**Remaining manual steps before landing page goes live:**
1. Create Supabase project → run supabase/schema.sql → copy URL + anon key to web/.env
2. Create Clerk account → copy publishable key to web/.env
3. Push to GitHub → connect to Vercel → deploy

**Pricing model:** Free (5 findings/scan) | Pro $29/mo (unlimited + AI remediation)
