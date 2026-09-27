# 🚀 Step-by-Step Deployment Guide: Render (Backend) & Vercel (Frontend)

This guide provides the complete, pre-configured workflow to deploy your full-stack application (**FastAPI Backend** on **Render** & **Vite/React Frontend** on **Vercel**).

---

## 🛠️ Summary of Pre-Deployment Setup Completed in Your Project

Your codebase has been fully pre-configured for seamless cloud deployment:

1. **Centralized Frontend API Configuration (`frontend/src/apiConfig.js`)**:
   - Replaced all hardcoded `http://127.0.0.1:8000` URLs across `AuthContext`, `TenderContext`, `Government.jsx`, and `Bidder.jsx`.
   - Dynamic API base resolving via `import.meta.env.VITE_API_BASE_URL`.

2. **Vercel Single Page Application Routing (`frontend/vercel.json`)**:
   - Configured SPA rewrite rules so client routes (`/government`, `/bidder`) reload without 404 errors on Vercel.

3. **Render Server Setup (`backend/Procfile` & `render.yaml`)**:
   - Added `gunicorn` to `requirements.txt`.
   - Created `Procfile` (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`) and `render.yaml` for 1-click Render blueprint deployments.

---

## 🟢 Step 1: Deploy Backend to Render

1. Push your latest code changes to your **GitHub / GitLab** repository.
2. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
3. Select your repository.
4. Configure the Web Service settings:
   - **Name**: `sih-tender-backend`
   - **Root Directory**: `backend` *(or path to `backend` folder in your repo)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   - `PYTHON_VERSION`: `3.11.0`
   - `USE_POSTGRES`: `false` *(or pass `DATABASE_URL` if connecting PostgreSQL)*
6. Click **Create Web Service**.
7. Copy your deployed Render Backend URL (e.g. `https://sih-tender-backend.onrender.com`).

---

## ⚡ Step 2: Deploy Frontend to Vercel

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New...** -> **Project**.
2. Import your GitHub repository.
3. Configure the Project settings:
   - **Framework Preset**: `Vite` (Auto-detected)
   - **Root Directory**: Select `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Under **Environment Variables**, add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://sih-tender-backend.onrender.com` *(Paste your live Render URL from Step 1)*
5. Click **Deploy**.

---

## 🔍 Pre-Flight Checklist

- [x] CORS middleware in `backend/main.py` permits requests from all origins (`allow_origins=["*"]`).
- [x] All API calls in frontend utilize `VITE_API_BASE_URL`.
- [x] SPA rewrites configured in `frontend/vercel.json`.
- [x] Render start command uses `$PORT`.
