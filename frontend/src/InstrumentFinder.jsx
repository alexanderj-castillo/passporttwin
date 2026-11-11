import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const calibrationLabels = {
  CURRENT: ["✓", "En plazo"],
  DUE_SOON: ["◷", "Vence pronto"],
  OVERDUE: ["!", "Vencida"],
  NO_HISTORY: ["–", "Sin historial"],
  NO_DUE_DATE: ["–", "Sin vencimiento"],
};

function InstrumentIdentity({ instrument, to, location }) {
  const { technical_name, serial_number, plant_tag } = instrument;
  return <>
    <Link to={to}>{technical_name || serial_number}</Link>
    {(plant_tag || technical_name) && <span>
      {[plant_tag, technical_name && `Serie ${serial_number}`].filter(Boolean).join(" · ")}
    </span>}
    {location && <span>{location}</span>}
  </>;
}

function InventoryGroups({ instruments }) {
  const groups = new Map();
  for (const instrument of instruments) {
    const parts = instrument.location?.split(" · ").map(part => part.trim()).filter(Boolean) ?? [];
    const area = parts.slice(0, 2).join(" · ") || "Sin ubicación";
    if (!groups.has(area)) groups.set(area, []);
    groups.get(area).push({ instrument, point: parts.slice(2).join(" · ") });
  }
  return <div className="inventory-groups">
    {[...groups].sort(([a], [b]) => a.localeCompare(b, "es")).map(([area, rows]) => <section key={area} className="inventory-group">
      <h3>{area} <small>{rows.length} {rows.length === 1 ? "instrumento" : "instrumentos"}</small></h3>
      <ul className="document-results instrument-results">
        {rows.map(({ instrument, point }) => {
          const status = instrument.calibration_status;
          const [icon, label] = calibrationLabels[status] ?? ["–", "Estado no disponible"];
          return <li key={instrument.public_id} className="inventory-row">
            <div className="inventory-identity">
              <InstrumentIdentity instrument={instrument} to={`/passport/${instrument.public_id}`} location={point} />
            </div>
            <span className="inventory-status" data-status={status} aria-label={`Calibración: ${label}`}>
              <span aria-hidden="true">{icon}</span> {label}
            </span>
          </li>;
        })}
      </ul>
    </section>)}
  </div>;
}

export default function InstrumentFinder({ apiBaseUrl, mode = "passport" }) {
  const [instruments, setInstruments] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    fetch(`${apiBaseUrl}/api/v1/instruments`, { signal: controller.signal })
      .then(response => { if (!response.ok) throw new Error(); return response.json(); })
      .then(setInstruments).catch(() => { if (!controller.signal.aborted) setError(true); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [apiBaseUrl]);
  const search = query.trim().toLowerCase();
  const matches = instruments.filter(i => [i.technical_name, i.plant_tag, i.serial_number, i.location]
    .join(" ").toLowerCase().includes(search));
  return <section className="workspace-panel" aria-labelledby="finder"><h2 id="finder">{mode === "audit" ? "Buscar un instrumento para auditoría" : "Buscar un pasaporte"}</h2>
    <label htmlFor="passport-search">Nombre, etiqueta, número de serie o ubicación</label>{" "}
    <input id="passport-search" value={query} onChange={event => setQuery(event.target.value)} />
    {loading ? <p role="status">Cargando instrumentos…</p> : error ? <p role="alert">No se ha podido cargar el inventario.</p>
      : !matches.length ? <p>No hay instrumentos que coincidan.</p>
      : mode === "passport" ? <InventoryGroups instruments={matches} />
      : <ul className="document-results instrument-results">{matches.slice(0, 20).map(i =>
        <li key={i.public_id}><InstrumentIdentity instrument={i}
          to={`/?tab=audit&entity=instrument&id=${i.id}&passport=${i.public_id}`} location={i.location || "Sin ubicación"} /></li>)}</ul>}
    {mode === "audit" && matches.length > 20 && <p>Se muestran 20 resultados. Afina la búsqueda para encontrar el instrumento.</p>}
    {import.meta.env.VITE_METABASE_DASHBOARD_URL && <a href={import.meta.env.VITE_METABASE_DASHBOARD_URL}>Abrir dashboard de flota</a>}
  </section>;
}
