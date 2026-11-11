import React from "react";
import { Link } from "react-router-dom";
import "./passport.css";

export default function AppShell({ active, auditHref = "/?tab=audit", onClickCapture, children }) {
  const fleetUrl = import.meta.env.VITE_METABASE_DASHBOARD_URL;
  return <div className="passport-layout" onClickCapture={onClickCapture}>
    <nav className="passport-sidebar" aria-label="Navegación general">
      <strong className="passport-brand">PassportTwin</strong>
      <Link to="/" aria-current={active === "home" ? "page" : undefined}>Inicio</Link>
      <Link to="/?tab=inventory" aria-current={active === "inventory" ? "page" : undefined}>Inventario</Link>
      <Link to="/?tab=review" aria-current={active === "review" ? "page" : undefined}>Revisión documental</Link>
      <Link to={auditHref} aria-current={active === "audit" ? "page" : undefined}>Auditoría</Link>
      {fleetUrl && <a href={fleetUrl}>Flota</a>}
    </nav>
    {children}
  </div>;
}
