# Maintaina — Predictive Maintenance Platform

A full-stack predictive-maintenance project that trains on real CSV datasets (including Kaggle exports) and serves live predictions through a React dashboard.

## Start locally

Open two terminals in this folder.

```powershell
.\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000
```

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. In **Data & Train**, upload your CSV, choose its label/target column (such as `Machine failure`), train the model, then use **Predict** to enter a new machine's readings.

## Dataset guidance

The app accepts ordinary comma-separated CSV files up to 100 MB. It automatically imputes missing data, one-hot encodes text categories, and excludes identifier, timestamp, RUL, and alternate failure-label columns to avoid data leakage. For a Kaggle dataset, select the actual failure outcome as the target rather than an ID or a sensor column.

The included `machine_data.csv` remains only a development sample; it is never silently used by the web application.

## CLI training

For automation, train using the same production pipeline:

```powershell
.\venv\Scripts\python.exe train_pipeline.py --data path\to\dataset.csv --target "Machine failure"
```

## Production build

```powershell
cd frontend
npm run build
```

Serve `frontend/dist` through a static host and set `VITE_API_URL` to the deployed API URL at build time. The FastAPI backend exposes interactive API documentation at `/docs`.

## Publish a public link

This repository is ready for a Railway + Vercel deployment.

1. Push the whole project (including `machine_data.csv`) to a GitHub repository.
2. In Railway, create a project from that repository. It detects `railway.toml`; deploy it without changing the start command. Copy the generated public URL, such as `https://maintaina-api.up.railway.app`.
3. In Vercel, import the same repository and set the **Root Directory** to `frontend`. Add an environment variable named `VITE_API_URL` with the Railway URL from the previous step. Deploy.
4. Open the Vercel URL. The backend trains automatically from `machine_data.csv` on its first startup; the first request can take a short time while that happens.

Optional: in Railway set `FRONTEND_ORIGINS` to your final Vercel URL. Vercel preview domains are already permitted.
