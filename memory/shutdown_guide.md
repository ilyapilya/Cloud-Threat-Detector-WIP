---
name: Shutdown Guide
description: Step-by-step instructions for stopping all CloudGuard services — local dev, Docker, Railway backend, and Vercel frontend
type: reference
---

# CloudGuard — Full Shutdown Guide

## Stack Overview

| Service | Where it runs | How it starts |
|---|---|---|
| Frontend (Vite dev) | Local | `npm run dev` in `web/` |
| Backend (FastAPI/uvicorn) | Local or Docker | `uvicorn app.main:app` or `docker compose up` |
| Postgres (local) | Docker | `docker compose up` in `infra/` |
| Backend (production) | Railway | Auto-deploys on push to `main` |
| Frontend (production) | Vercel | Auto-deploys on push to `main` |

---

## 1. Stop Local Dev Servers

### Frontend (Vite)
Press `Ctrl+C` in the terminal running `npm run dev` inside `web/`.

### Backend (uvicorn, run directly)
Press `Ctrl+C` in the terminal running uvicorn.

If it was started in the background or you lost the terminal:
```bash
# Find and kill the uvicorn process
lsof -i :8000          # macOS/Linux — find PID on port 8000
kill <PID>

# Windows (PowerShell)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 2. Stop Docker Services (Local Postgres + Backend)

From the repo root or `infra/` directory:

```bash
# Graceful stop (containers stay, data preserved)
cd infra
docker compose down

# Stop AND remove volumes (wipes local Postgres data)
docker compose down -v
```

To verify everything stopped:
```bash
docker ps
```

---

## 3. Stop / Pause Production Backend (Railway)

The Railway backend at `https://cloudguard-production.up.railway.app` runs continuously.

**To pause a deployment (keeps config, stops billing):**
1. Go to [railway.app](https://railway.app) → your project → the `backend` service
2. Click the service → **Settings** → scroll to **Danger Zone**
3. Click **Suspend Service**

**To take it fully offline:**
- In the Railway dashboard, click **Remove Service** (irreversible — redeploy from Git to restore)
- Or, simply stop pushing to `main` — Railway won't redeploy until the next push

**To stop a single deployment mid-deploy:**
1. Railway dashboard → **Deployments** tab
2. Click the active deployment → **Cancel**

---

## 4. Stop / Pause Production Frontend (Vercel)

The Vercel frontend auto-deploys on every push to `main`.

**To take the site offline temporarily:**
1. Go to [vercel.com](https://vercel.com) → your project
2. **Settings** → **Domains** → remove or disable the domain

**To pause all new deployments:**
1. **Settings** → **Git** → disconnect the Git repository

**To delete the project entirely:**
1. **Settings** → scroll to **Delete Project** (irreversible)

---

## 5. Stop Supabase (Database)

Supabase (hosted) has no "stop" — it always runs. To cut access:

- **Revoke API keys:** Supabase dashboard → **Project Settings** → **API** → regenerate keys (invalidates old ones)
- **Pause the project (free tier only):** Supabase dashboard → **Project Settings** → **General** → **Pause project**
- **Delete the project:** Supabase dashboard → **General** → **Delete Project** (irreversible, destroys all data)

---

## Quick Reference: Full Local Shutdown

```bash
# 1. Ctrl+C in the Vite terminal (frontend)
# 2. Ctrl+C in the uvicorn terminal (backend)

# 3. Stop Docker (from infra/)
cd infra && docker compose down
```

## Quick Reference: Full Production Shutdown

1. Railway dashboard → suspend or remove the `backend` service
2. Vercel dashboard → disconnect Git or delete the project
3. Supabase dashboard → pause or delete the project
