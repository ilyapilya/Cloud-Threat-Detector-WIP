# Deployment Guide

## How it works

| Layer | Service | Trigger |
|-------|---------|---------|
| Frontend (`web/`) | Vercel | Auto-deploys on `git push` to `main` |
| Backend (`backend/`) | Railway | Auto-deploys on `git push` to `main` |

---

## Deploying frontend changes

Every push to `main` triggers a Vercel rebuild automatically. No manual steps needed after initial setup.

```bash
git add .
git commit -m "your message"
git push
```

Vercel will pick it up within ~30 seconds. Watch the build at:
`https://vercel.com/dashboard` → your project → Deployments tab.

### Testing locally before pushing

```bash
cd web
npm run dev        # dev server at http://localhost:5173
npm run build      # verify production build has no errors before pushing
```

---

## Deploying backend changes

Same flow — push to `main` and Railway redeploys automatically.

### Testing locally before pushing

```bash
cd backend
uvicorn app.main:app --reload --port 8000
# API available at http://localhost:8000
```

### First-time Railway setup (if not done yet)

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. Select this repo, set **Root Directory** to `backend`
3. Add environment variables (same as your `.env`)
4. Railway detects the `Dockerfile` and builds automatically

---

## Environment variables

If you add or change a key in `web/.env`, you must also update it in Vercel:

`Vercel Dashboard` → Project → **Settings** → **Environment Variables**

Same for Railway if you add backend env vars.

---

## Previewing before it goes live

Vercel creates a unique preview URL for every push — even to `main`. Check the Deployments tab to grab a preview link before traffic hits the production domain.

---

## Rollback

In Vercel dashboard → Deployments → find any previous deploy → click **...** → **Promote to Production**.
