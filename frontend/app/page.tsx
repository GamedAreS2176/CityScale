"use client";

import { useMemo, useState } from "react";
import axios from "axios";
import MapComponent from "../components/Map";

type AxiosErrorLike = {
  response?: {
    status?: number;
    data?: {
      detail?: unknown;
      error?: unknown;
      message?: unknown;
    };
  };
};

type DataPoint = {
  lat: number;
  lng: number;
  bias_score: number;
  region?: string;
  allocation?: number;
  population?: number;
  allocation_per_capita?: number;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const projectHighlights = [
  "Surfaces funding inequity across regions using a bias-aware analysis pipeline.",
  "Turns raw allocation CSVs into an interactive map for quick spatial insight.",
  "Inspect hotspots, drill into regions, and compare bias scores instantly.",
];

const workflowSteps = [
  {
    title: "Upload city data",
    description: "Upload a CSV with `region`, `allocation`, and `population`.",
  },
  {
    title: "Run fairness analysis",
    description:
      "We clean data, add coordinates, and compute bias scores for each region.",
  },
  {
    title: "Explore the map",
    description:
      "Click a point to view allocation, population, and per-capita funding.",
  },
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stats = useMemo(() => {
    const totalAllocation = data.reduce(
      (sum, point) => sum + (point.allocation ?? 0),
      0
    );
    const totalPopulation = data.reduce(
      (sum, point) => sum + (point.population ?? 0),
      0
    );
    const hotspots = data.filter((point) => Math.abs(point.bias_score) > 0.3);
    const highestBias = data.reduce(
      (best, point) =>
        Math.abs(point.bias_score) > Math.abs(best.bias_score) ? point : best,
      data[0] ?? { lat: 0, lng: 0, bias_score: 0 }
    );

    return {
      regions: data.length,
      hotspots: hotspots.length,
      totalAllocation,
      totalPopulation,
      highestBiasRegion: highestBias.region ?? "Awaiting analysis",
      highestBiasScore: highestBias.bias_score,
    };
  }, [data]);

  const insights = useMemo(
    () => [
      {
        label: "Regions analyzed",
        value: stats.regions.toLocaleString(),
        helper: "Live records available on the map",
      },
      {
        label: "Funding hotspots",
        value: stats.hotspots.toLocaleString(),
        helper: "Areas with strong over/under allocation signals",
      },
      {
        label: "Tracked allocation",
        value: stats.totalAllocation
          ? `₹${Math.round(stats.totalAllocation).toLocaleString()}`
          : "Upload CSV",
        helper: "Sum of allocations from the latest run",
      },
      {
        label: "Population covered",
        value: stats.totalPopulation
          ? Math.round(stats.totalPopulation).toLocaleString()
          : "Waiting",
        helper: "People represented in the uploaded dataset",
      },
    ],
    [stats]
  );

  const handleUpload = async () => {
    if (!file) {
      setError("Select a CSV file to run the analysis.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setError(null);

      const uploadRes = await axios.post(`${API_BASE_URL}/upload/`, formData);
      const filePath = uploadRes.data.file_path;

      const analyzeRes = await axios.post(`${API_BASE_URL}/analyze/`, {
        file_path: filePath,
      });

      const points = Array.isArray(analyzeRes.data) ? analyzeRes.data : [];
      if (!Array.isArray(analyzeRes.data)) {
        console.warn("Unexpected analyze response:", analyzeRes.data);
      }

      setData(points);
    } catch (err) {
      console.error("Error while analyzing CSV:", err);
      const axiosErr = err as AxiosErrorLike;
      const status = axiosErr?.response?.status;
      const detail =
        axiosErr?.response?.data?.detail ??
        axiosErr?.response?.data?.error ??
        axiosErr?.response?.data?.message;
      const hint = detail
        ? `Backend error${status ? ` (${status})` : ""}: ${String(detail)}`
        : "CityScale could not process that file right now. Check that the backend is running and the CSV includes region, allocation, and population columns.";
      setError(hint);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-10%] top-0 h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute right-[-5%] top-20 h-96 w-96 rounded-full bg-violet-500/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-emerald-400/10 blur-3xl" />
      </div>

      <section className="mx-auto flex min-h-screen w-full max-w-[104rem] flex-col px-4 py-10 sm:px-8 lg:px-16">
        <div className="rounded-[40px] border border-white/12 bg-white/8 p-7 shadow-2xl shadow-slate-950/30 backdrop-blur sm:p-10 xl:p-12">
          <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 text-sm font-medium text-cyan-100">
                <span className="h-2 w-2 rounded-full bg-cyan-300" />
                Hackathon demo ready
              </div>

              <div className="space-y-5">
                <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
                  CityScale visualizes urban funding fairness in one clean map.
                </h1>
                <p className="max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
                  Upload your allocation CSV and instantly see where regions are
                  over-funded or under-funded, with clear metrics and an
                  interactive map.
                </p>
              </div>

              <div className="space-y-4">
                <p className="text-sm font-medium uppercase tracking-[0.3em] text-slate-300/80">
                  Key features
                </p>
                <div className="grid gap-4 sm:grid-cols-3">
                  {projectHighlights.map((item) => (
                    <div
                      key={item}
                      className="rounded-3xl border border-white/10 bg-slate-950/40 p-6 text-sm leading-7 text-slate-200"
                    >
                      {item}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {insights.map((item) => (
                  <div
                    key={item.label}
                    className="rounded-3xl border border-white/10 bg-slate-950/50 p-6"
                  >
                    <p className="text-sm text-slate-400">{item.label}</p>
                    <p className="mt-2 text-2xl font-semibold text-white">
                      {item.value}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {item.helper}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[32px] border border-white/10 bg-slate-950/60 p-7 shadow-xl shadow-slate-950/20 sm:p-8">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-200/80">
                    Analyze dataset
                  </p>
                  <h2 className="mt-3 text-2xl font-semibold text-white">
                    Upload a city allocation CSV
                  </h2>
                </div>
                <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                  {loading ? "Processing" : "Ready"}
                </div>
              </div>

              <p className="mt-4 text-sm leading-7 text-slate-300">
                CityScale expects `region`, `allocation` (or `budget`), and
                `population` columns. Once uploaded, the backend geocodes the
                regions and renders bias signals directly on the map.
              </p>

              <div className="mt-7 rounded-3xl border border-dashed border-white/15 bg-white/5 p-6">
                <label
                  htmlFor="csv-upload"
                  className="block text-sm font-medium text-slate-200"
                >
                  Choose CSV file
                </label>
                <input
                  id="csv-upload"
                  type="file"
                  accept=".csv"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      setFile(e.target.files[0]);
                      setError(null);
                    }
                  }}
                  className="mt-3 block w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-full file:border-0 file:bg-cyan-400 file:px-4 file:py-2 file:font-medium file:text-slate-950 hover:file:bg-cyan-300"
                />
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                  <p className="text-sm text-slate-400">
                    {file ? `Selected: ${file.name}` : "No file selected yet"}
                  </p>
                  <button
                    onClick={handleUpload}
                    disabled={loading}
                    className="inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-slate-400"
                  >
                    {loading ? "Analyzing dataset..." : "Run analysis"}
                  </button>
                </div>
              </div>

              {error && (
                <div className="mt-5 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm leading-6 text-rose-100">
                  {error}
                </div>
              )}

              <div className="mt-8">
                <p className="text-sm font-medium uppercase tracking-[0.3em] text-slate-300/80">
                  How it works
                </p>
                <div className="mt-4 grid gap-4">
                  {workflowSteps.map((step, index) => (
                    <div
                      key={step.title}
                      className="flex gap-4 rounded-3xl border border-white/10 bg-white/5 p-5"
                    >
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white/10 text-sm font-semibold text-white">
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="font-medium text-white">{step.title}</h3>
                        <p className="mt-1 text-sm leading-6 text-slate-400">
                          {step.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <section className="mt-10 grid gap-8">
          <div className="rounded-[36px] border border-white/10 bg-slate-950/55 p-4 shadow-2xl shadow-slate-950/20 backdrop-blur sm:p-6">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3 px-2">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-200/80">
                  Fairness map
                </p>
                <h2 className="mt-2 text-2xl font-semibold text-white">
                  Interactive regional bias explorer
                </h2>
              </div>
              <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">
                {data.length
                  ? `${data.length} mapped points`
                  : "Upload data to populate the map"}
              </div>
            </div>
            <MapComponent data={data} />
          </div>
        </section>
      </section>
    </main>
  );
}