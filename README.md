# CityScale 🏙️

Welcome to **CityScale** — an advanced, full-stack application that visualizes urban infrastructure funding allocation and detects spatial biases using interactive maps and Generative AI.

## 🚀 Overview

CityScale helps city planners, journalists, and citizens identify over-funded and under-funded regions within a city. By simply uploading a CSV containing regional allocations and population data, the system automatically geocodes the regions, analyzes fair funding distributions, and renders an interactive heatmap along with an AI-generated executive summary of the fairness implications.

### ✅ Key Features
* **Interactive Fairness Map (Next.js + Google Maps API)**: Renders regions as dynamically sized, color-coded clusters representing the severity of funding bias (over-funded vs. under-funded).
* **Robust Backend Pipeline (FastAPI)**: A highly scalable API that processes messy CSV uploads, dynamically corrects column names, drops invalid data, and securely uploads artifacts to Google Cloud Storage.
* **Algorithmic Funding Bias Engine**: Mathematically scores regions based on per-capita allocation and vulnerable population metrics to determine an "Expected Budget" and isolates spatial inequity.
* **Generative AI Analyst (Gemini 2.5 Flash)**: Ingests the computed bias scores and instantly produces a succinct, natural-language executive report explaining the fairness implications and providing actionable reallocation advice.
* **Intelligent Fallbacks & Geocoding**: Relies on a local mapping dictionary (`region_latlng.json`), falling back to OpenStreetMap Nominatim for unknown regions. If the LLM API drops, it falls back to a deterministic string report without crashing the API.

---

## 🛠️ Tech Stack

### Frontend
* **Framework**: Next.js 16 (App Router)
* **Styling**: Tailwind CSS v4, Vanilla CSS
* **Map Visualization**: `@react-google-maps/api`
* **Deployment**: Firebase App Hosting

### Backend & AI Engine
* **Framework**: FastAPI / Uvicorn (Python 3.10+)
* **Data Processing**: Pandas, NumPy
* **LLM Engine**: Google GenAI (`gemini-2.5-flash`)
* **Deployment**: Google Cloud Run, Google Cloud Storage (GCS)

---

## 📂 Project Structure

```text
CityScale/
├── frontend/             # Next.js Application
│   ├── app/              # App Router pages & global styles
│   ├── components/       # Reusable React components (Map.tsx)
│   ├── package.json      # Frontend dependencies
│   └── apphosting.yaml   # Firebase App Hosting configuration
├── backend/              # FastAPI Application
│   ├── app/              # API Routes, Services, and Core App logic
│   └── requirements.txt  # Core dependencies
├── ai_engine/            # AI & Bias Pipeline Engine
│   ├── pipelines/        # Bias calculation & Report generation
│   ├── llm/              # Gemini Client & Prompt templates
│   └── utils/            # Data formatting for the heatmap
├── data/                 # Raw datasets, Uploads, and region mapping
│   └── mappings/         # region_latlng.json mapping coordinates
├── infra/                # Infrastructure definitions
├── Dockerfile            # Unified Dockerfile for Cloud Run
└── firebase.json         # Firebase project configuration
```

---

## 💻 Local Development

### Prerequisites
* Node.js v20+
* Python 3.10+
* Google Maps API Key
* Gemini API Key

### 1. Running the Backend
Create a `.env` file at the root of the project:
```env
GEMINI_API_KEY="your-gemini-key"
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

Start the FastAPI server:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*The API and interactive Swagger docs will be available at `http://localhost:8000/docs`.*

### 2. Running the Frontend
Create a `.env.local` file inside the `frontend/` directory:
```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY="your-google-maps-key"
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
```

Start the Next.js development server:
```bash
cd frontend
npm install
npm run dev
```
*The web app will be available at `http://localhost:3000`.*

---

## ☁️ Deployment Instructions

CityScale is built for serverless deployment on Google Cloud. It utilizes **Cloud Run** for the backend and **Firebase App Hosting** for the frontend.

### 1. Deploy the Backend (Google Cloud Run)
The unified root `Dockerfile` wraps the `backend` and `ai_engine`. We utilize a `.gcloudignore` file to safely exclude secrets from standard Git tracking while ensuring they are securely injected into Cloud Build context.

```bash
# Ensure you are at the project root
gcloud run deploy cityscale-api --source . --region asia-south1 --allow-unauthenticated
```

### 2. Deploy the Frontend (Firebase App Hosting)
Firebase App Hosting automatically listens to GitHub pushes. The configuration lives in `frontend/apphosting.yaml`.

Make sure your production `NEXT_PUBLIC_API_BASE_URL` is pointing to the deployed Cloud Run service URL in `apphosting.yaml`.

```bash
git add .
git commit -m "Deploy production frontend"
git push
```
Firebase will automatically build and roll out the frontend. Monitor the build status in the [Firebase Console](https://console.firebase.google.com).
