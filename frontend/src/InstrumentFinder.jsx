import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

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
    {loading ? <p role="status">Cargando instrumentos…</p> : error ? <p role="alert">No se ha podido cargar el inventario.</p> : <ul className="document-results">{matches.slice(0, 20).map(i =>
      <li key={i.public_id}>
        <Link to={mode === "audit" ? `/?tab=audit&entity=instrument&id=${i.id}&passport=${i.public_id}` : `/passport/${i.public_id}`}>
          {[i.technical_name, i.plant_tag, i.serial_number].filter(Boolean).join(" · ")}
        </Link>
        <span>{i.location || "Sin ubicación"}</span>
      </li>)}</ul>}
    {!loading && !error && !matches.length && <p>No hay instrumentos que coincidan.</p>}
    {matches.length > 20 && <p>Se muestran 20 resultados. Afina la búsqueda para encontrar el instrumento.</p>}
    {import.meta.env.VITE_METABASE_DASHBOARD_URL && <a href={import.meta.env.VITE_METABASE_DASHBOARD_URL}>Abrir dashboard de flota</a>}
  </section>;
}
