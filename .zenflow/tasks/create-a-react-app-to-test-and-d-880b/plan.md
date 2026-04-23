# Plan: React Demo App for balloon-predictor

Create a `frontend/` Vite+React app with two sections:
1. **Burst Calculator** — calls `POST /api/burst` and displays computed burst altitude, ascent rate, neck lift, and helium mass.
2. **Trajectory Predictor** — calls `POST /api/predict` and renders the flight path on a Leaflet map with burst/landing markers.

Vite dev proxy forwards `/api/*` to the local FastAPI server. `vercel.json` updated to build+serve the SPA alongside the Python serverless function.

### [x] Step 1: Update .gitignore and plan.md
### [x] Step 2: Scaffold Vite + React frontend in frontend/
### [x] Step 3: Build Burst Calculator and Trajectory Predictor components with Leaflet map
### [x] Step 4: Configure Vite proxy and update vercel.json
