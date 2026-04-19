# CityScale 🏙️

Welcome to **CityScale** — an advanced, scalable backend architecture for intelligent urban infrastructure analysis and funding bias detection.

## 🚀 State of the Project (Where we are)

As of the latest major development sprint, the core backend pipeline is completely functional, seamlessly fusing local data handling, algorithmic analysis, geographically mapped visualizations, and generative AI reporting. It has been successfully Dockerized and is production-ready for **Google Cloud Run**.

### ✅ Completed Features
* **Robust Backend Operations (FastAPI)**
  * A scalable architecture configured at `/backend` with highly adaptive API routes.
  * Robustly authenticates against Google Cloud Storage using `.json` service accounts or Cloud Run's native Application Default Credentials interchangeably. Uses `gcsfs` natively under the hood. 
* **Dynamic Pipeline System (`ai_engine`)**
  * **Intelligent Merging & Normalization:** Extracts features dynamically whether the incoming stream drops standard DataFrames or cloud file-paths. Automatically remaps standard database keys (e.g., `region` -> `area`, `allocation` -> `budget`).
  * **Defensive Fallbacks:** Smartly corrects for merged identical DataFrames, stripping away ambiguous `_x` and `_y` pandas suffixes, and dynamically mapping core missing indicators (like defaulting to "middle" income) to shield against missing datasets. 
  * **Funding Bias Calculation Engine:** Automatically scores regions mathematically by analyzing population dynamics. Calculates an "Expected Budget", directly isolating overfunded and underfunded geographical boundaries. 
  * **Frontend Heatmap Payload Generation:** Converts backend results to strict frontend mapping constraints by automatically resolving missing latitude/longitude coordinates via `region_latlng.json`.
* **Generative AI Analyst (Gemini)**
  * Fully integrated `google.genai` (utilizing the newest `gemini-2.5-flash` model).
  * Ingests the output of the Bias Calculation Engine, intelligently structuring the data into actionable prompt templates, and returning a succinct, natural-language executive summary.
  * **Graceful Failover:** In the event an LLM key drops (or fails to connect), the pipeline catches the exception immediately and falls safely back to a structured deterministic string report without crashing the API.
* **Streamlined DevOps & Docker**
  * Unified root-level `Dockerfile` constructed specifically to absorb the overarching dependencies (tying together `/backend`, `/ai_engine`, `.env` keys, and `/data` artifacts).
  * Automatically sets `GOOGLE_APPLICATION_CREDENTIALS` dynamically when booting `uvicorn app.main:app` inside the container. 
  * Formatted perfectly for one-line deployments to **Google Cloud Run**.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI / Uvicorn
* **Data Processing:** Pandas, NumPy
* **Cloud Platform:** Google Cloud (Storage, Cloud Run)
* **LLM Engine:** Google GenAI (`gemini-2.5-flash`)

## ☁️ Deployment Instructions

CityScale is natively optimized for **Google Cloud Run**.

1. **Verify your credentials:** 
   Place your standard service account chunk into the root, mapping `GEMINI_API_KEY` into your instance constraints if required.
2. **Push to Google Cloud:** (Requires `gcloud` CLI)
   ```bash
   gcloud run deploy cityscale-api --source . --region asia-south1 --allow-unauthenticated --set-env-vars="GEMINI_API_KEY=YOUR_KEY_HERE"
   ```

## 🧪 Testing Locally

You can spin the full pipeline up locally isolated in Docker:
```bash
docker build -t cityscale-api .
docker run -p 8080:8080 cityscale-api
```
Navigate to `http://localhost:8080/docs` to directly fire JSON at the highly interactive Swagger test bed!
