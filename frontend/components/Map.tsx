"use client";

import React, { useCallback, useMemo, useState } from "react";
import {
  GoogleMap,
  LoadScript,
  Circle,
  InfoWindow,
  Marker,
} from "@react-google-maps/api";

type DataPoint = {
  lat: number;
  lng: number;
  bias_score: number;
  region?: string;
  allocation?: number;
  population?: number;
  allocation_per_capita?: number;
};

const libraries: ("places" | "drawing" | "geometry" | "visualization")[] = [];
const fallbackCenter = { lat: 22.5726, lng: 88.3639 }; // Kolkata

function getBiasColor(score: number): { fill: string; stroke: string } {
  // Requirement: red for negative (underfunded), green for positive (well-funded)
  if (score < 0) return { fill: "#ef4444", stroke: "#b91c1c" };
  if (score > 0) return { fill: "#22c55e", stroke: "#15803d" };
  return { fill: "#94a3b8", stroke: "#64748b" };
}

function getBiasLabel(score: number): string {
  if (score < 0) return "Underfunded";
  if (score > 0) return "Overfunded";
  return "Balanced";
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

export default function MapComponent({ data }: { data: DataPoint[] }) {
  const [selected, setSelected] = useState<DataPoint | null>(null);
  const [hoveredKey, setHoveredKey] = useState<string | null>(null);
  const hasApiKey = Boolean(process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY);

  const center = useMemo(() => {
    if (!data.length) return fallbackCenter;
    return { lat: data[0].lat, lng: data[0].lng };
  }, [data]);

  const mapOptions = useMemo<google.maps.MapOptions>(
    () => ({
      disableDefaultUI: true,
      zoomControl: true,
      clickableIcons: false,
      styles: [
        {
          elementType: "geometry",
          stylers: [{ color: "#0f172a" }],
        },
        {
          elementType: "labels.text.fill",
          stylers: [{ color: "#cbd5e1" }],
        },
        {
          elementType: "labels.text.stroke",
          stylers: [{ color: "#0f172a" }],
        },
        {
          featureType: "administrative",
          elementType: "geometry.stroke",
          stylers: [{ color: "#334155" }],
        },
        {
          featureType: "poi",
          stylers: [{ visibility: "off" }],
        },
        {
          featureType: "road",
          elementType: "geometry",
          stylers: [{ color: "#1e293b" }],
        },
        {
          featureType: "water",
          elementType: "geometry",
          stylers: [{ color: "#0f766e" }],
        },
      ],
    }),
    []
  );

  const points = useMemo(() => {
    return data
      .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng))
      .map((point) => {
        const radius = clamp(Math.abs(point.bias_score) * 12000, 900, 9000);
        const key = `${point.region ?? "region"}:${point.lat}:${point.lng}`;
        return { ...point, radius, key };
      });
  }, [data]);

  const handleMapClick = useCallback(() => {
    setSelected(null);
  }, []);

  if (!hasApiKey) {
    return (
      <div className="flex h-[560px] items-center justify-center rounded-[24px] border border-white/10 bg-slate-950/70 p-8 text-center">
        <div className="max-w-md">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-200/80">
            Map unavailable
          </p>
          <h3 className="mt-3 text-2xl font-semibold text-white">
            Add your Google Maps key to unlock the live visualization
          </h3>
          <p className="mt-4 text-sm leading-7 text-slate-300">
            Set `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` in the frontend environment
            and restart the app. The rest of the dashboard will still work.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="pointer-events-none absolute inset-0 rounded-[24px] bg-gradient-to-br from-cyan-400/5 via-transparent to-violet-500/10" />

      <div className="absolute right-4 top-4 z-10 w-[240px] rounded-2xl border border-white/10 bg-slate-950/78 p-4 text-sm shadow-xl shadow-slate-950/30 backdrop-blur">
        <div className="mb-2 text-sm font-semibold text-white">Bias legend</div>
        <div className="space-y-2 text-slate-200">
          <div className="flex items-center gap-3">
            <div className="h-3.5 w-3.5 rounded-full bg-red-500" />
            <span className="text-xs leading-5">Underfunded (negative)</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-3.5 w-3.5 rounded-full bg-green-500" />
            <span className="text-xs leading-5">Overfunded (positive)</span>
          </div>
        </div>
        <div className="mt-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-[11px] leading-5 text-slate-400">
          Click a circle or marker to view region details.
        </div>
      </div>

      <LoadScript
        googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!}
        libraries={libraries}
      >
        <GoogleMap
          mapContainerStyle={{
            width: "100%",
            height: "min(78vh, 820px)",
            borderRadius: "24px",
          }}
          center={center}
          zoom={points.length ? 11 : 10}
          options={mapOptions}
          onClick={handleMapClick}
        >
          {!points.length && (
            <InfoWindow position={fallbackCenter}>
              <div className="min-w-[220px] text-[13px] leading-6 text-slate-800">
                <div className="text-[15px] font-bold text-slate-900">
                  No mapped regions yet
                </div>
                <div className="mt-2 text-slate-700">
                  Upload a CSV and run analysis to highlight regions on the map.
                </div>
              </div>
            </InfoWindow>
          )}
          {points.map((point) => {
            const { fill, stroke } = getBiasColor(point.bias_score);
            const isHovered = hoveredKey === point.key;

            return (
              <React.Fragment key={point.key}>
                <Circle
                  center={{ lat: point.lat, lng: point.lng }}
                  radius={point.radius}
                  options={{
                    fillColor: fill,
                    fillOpacity: isHovered ? 0.55 : 0.38,
                    strokeColor: stroke,
                    strokeOpacity: 0.9,
                    strokeWeight: isHovered ? 3 : 2,
                    clickable: true,
                    zIndex: isHovered ? 3 : 2,
                  }}
                  onClick={() => setSelected(point)}
                  onMouseOver={() => setHoveredKey(point.key)}
                  onMouseOut={() => setHoveredKey(null)}
                />

                <Marker
                  position={{ lat: point.lat, lng: point.lng }}
                  label={{
                    text: point.region ?? "Region",
                    color: "#e2e8f0",
                    fontSize: "12px",
                    fontWeight: "600",
                  }}
                  options={{
                    optimized: true,
                  }}
                  onClick={() => setSelected(point)}
                />
              </React.Fragment>
            );
          })}

          {/* InfoWindow — shown when a circle is clicked */}
          {selected && (
            <InfoWindow
              position={{ lat: selected.lat, lng: selected.lng }}
              onCloseClick={() => setSelected(null)}
            >
              <div className="min-w-[220px] text-[13px] leading-7 text-slate-800">
                <div className="mb-1 text-[15px] font-bold text-slate-900">
                  {selected.region ?? "Region"}
                </div>
                <div
                  className="mb-3 inline-block rounded-full px-3 py-1 text-[11px] font-semibold text-white"
                  style={{
                    backgroundColor: getBiasColor(selected.bias_score).fill,
                  }}
                >
                  {getBiasLabel(selected.bias_score)}
                </div>
                <div>
                  <b>Bias Score:</b> {selected.bias_score.toFixed(3)}
                </div>

                {selected.allocation !== undefined && (
                  <div>
                    <b>Allocation:</b> ₹
                    {Number(selected.allocation).toLocaleString()}
                  </div>
                )}
                {selected.population !== undefined && (
                  <div>
                    <b>Population:</b> {Number(selected.population).toLocaleString()}
                  </div>
                )}
                {selected.allocation_per_capita !== undefined && (
                  <div>
                    <b>Per Capita:</b> ₹
                    {Number(selected.allocation_per_capita).toFixed(2)}
                  </div>
                )}
              </div>
            </InfoWindow>
          )}
        </GoogleMap>
      </LoadScript>
    </div>
  );
}