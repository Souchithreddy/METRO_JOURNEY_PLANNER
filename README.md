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

## Why this is updated

- Added station matching robustness (exact station matching, case-insensitive)
- Fixed route parsing edge case to avoid `substring not found`
- Added `intermediate_stations` to response payload
- UI redesign with better color contrast and route details section

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

## Verified behavior

- `GET /get_elements` populates station dropdown data (Blue/Red/Green line splits)
- `POST /` returns route details and intermediate stations array:
  - `source_station`, `destination_station`, `distance`, `time`, `cost`, `intermediate_stations`

## GitHub repository

The repository is now pushed to:

`https://github.com/Souchithreddy/METRO_JOURNEY_PLANNER`

## Notes

- The UI now uses a simple card-like layout for readability.
- You can hide/show the route map via the toggle button.
- Error handling is shown in the app when a station is missing or malformed.

   python app.py
   ```

2. **Run the Vite frontend:**

   ```bash
   # Make sure you are in the 'frontend' directory
   npm run dev
   ```

3. **Open the Application:**

   Open your web browser and go to http://localhost:3000 to see the Metro Journey Planner application in action.
