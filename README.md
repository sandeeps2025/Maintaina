# Maintaina — Predictive Maintenance Platform

A full-stack predictive-maintenance project that trains on CSV datasets and serves predictions through a React dashboard.

## Start locally

Open two terminals in the project folder.

**Terminal 1 — FastAPI backend**

```powershell
.\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000
```

**Terminal 2 — React frontend**

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173.

In **Data & Train**, upload your CSV, choose its label/target column (such as `Machine failure`), and train the model. Then use **Predict** to enter new machine readings.

## Dataset guidance

The app accepts CSV files up to 100 MB. It handles missing values, encodes text categories, and excludes identifier, timestamp, RUL, and alternate failure-label columns to help prevent data leakage.

For a Kaggle dataset, select the actual failure outcome as the target rather than an ID or sensor column.

## CLI training

```powershell
.\venv\Scripts\python.exe train_pipeline.py --data path\to\dataset.csv --target "Machine failure"
```

## Production build

```powershell
cd frontend
npm run build
```

Serve `frontend/dist` through a static host and configure `VITE_API_URL` with the deployed API URL at build time. FastAPI provides interactive API documentation at `/docs`.

## Deployment

The project includes Railway configuration and a React frontend suitable for deployment.

1. Push the project to GitHub.
2. Deploy the backend using Railway and obtain its public URL.
3. Import the repository into Vercel, setting the root directory to `frontend`.
4. Set the `VITE_API_URL` environment variable to the Railway backend URL, then deploy the frontend.
5. Configure `FRONTEND_ORIGINS` in Railway with the Vercel URL if needed.