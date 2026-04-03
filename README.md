# Metro Journey Planner (Refreshed)

This is a Metro Journey Planner project that is now set up with an improved workflow and the same core functionality as before.

## What the app does

- Computes the shortest metro path from source to destination using an internal metro graph.
- Calculates travel distance and estimated time/cost.
- Provides a list of in-between stations for the chosen route.
- Shows a real-time UI with modern controls and readable styling.

## Stack

- **Backend**: Python + Flask (`backend/metro.py`)
- **Frontend**: React + TypeScript + Vite (`frontend/src/components/Metro.tsx`)
- **CORS**: `flask-cors`

## Local setup (current project state)

### 1. Backend

From project root:

```bash
cd backend
python -m pip install -r requirements.txt
python metro.py
```

Server runs on: `http://127.0.0.1:5000`

### 2. Frontend

From project root:

```bash
cd frontend
npm install
npm run dev
```

Front end runs on a Vite port, e.g. `http://localhost:3000` (or 3001/3002/3003 if used).
