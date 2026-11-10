import React, { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import AppShell from "./AppShell";
import "./passport.css";

export default function DocumentOriginal({ apiBaseUrl }) {
  const { documentId } = useParams();
  const [params] = useSearchParams();
  const passport = params.get("passport");
  const [state, setState] = useState({ loading: true });

  useEffect(() => {
    const controller = new AbortController();
    let objectUrl;
    setState({ loading: true });
    async function load() {
      try {
        const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/api/v1/documents/${encodeURIComponent(documentId)}/original`, { signal: controller.signal });
        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          throw new Error(data.detail || "No se ha podido abrir el original. Inténtalo de nuevo o revisa su disponibilidad.");
        }
        const blob = await response.blob();
        if (controller.signal.aborted) return;
        objectUrl = URL.createObjectURL(blob);
        const encodedName = response.headers.get("Content-Disposition")?.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
        let filename = `documento-${documentId}${blob.type === "application/pdf" ? ".pdf" : ""}`;
        if (encodedName) {
          try { filename = decodeURIComponent(encodedName); } catch { /* Use the fallback name. */ }
        }
        setState({ url: objectUrl, filename, pdf: blob.type === "application/pdf", sha256: response.headers.get("X-Content-SHA256") });
      } catch (error) {
        if (!controller.signal.aborted) setState({ error: error.message });
      }
    }
    load();
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [apiBaseUrl, documentId]);

  return <AppShell active="review"><main className="passport workspace-page" data-view="review">
    <header className="workspace-heading"><p>Evidencia documental</p><h1>Documento original</h1>
      <nav className="passport-links" aria-label="Navegación del documento">
        {passport && <Link to={`/passport/${encodeURIComponent(passport)}`}>Volver al pasaporte</Link>}
        <Link to={`/?tab=review&documentId=${encodeURIComponent(documentId)}${passport ? `&passport=${encodeURIComponent(passport)}` : ""}#selected-document`}>Revisar campos</Link>
        <Link to="/">Inicio y búsqueda</Link>
      </nav>
    </header>
    {state.loading ? <p role="status">Cargando original…</p> : state.error ? <p role="alert">{state.error}</p> : <section className="workspace-panel">
      <h2>{state.filename}</h2>
      <p><a href={state.url} download={state.filename}>Descargar original</a></p>
      {state.sha256 && <p className="original-hash">SHA-256 verificado: <code>{state.sha256}</code></p>}
      {state.pdf ? <>
        <p>Si tu navegador no muestra el PDF, descarga el original para abrirlo en tu visor.</p>
        <iframe title={`Original: ${state.filename}`} src={state.url} className="original-viewer" />
      </> : <p>Este formato está disponible para descargar.</p>}
    </section>}
  </main></AppShell>;
}
