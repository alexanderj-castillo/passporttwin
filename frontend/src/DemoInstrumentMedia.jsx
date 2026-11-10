import React from "react";
import sano from "./assets/demo/sano.webp";
import vencido from "./assets/demo/vencido.webp";
import revision from "./assets/demo/revision.webp";

const resources = new Map([
  ["PTWIN-DEMO-SANO", { photo: sano, zone: "Área de trabajo", x: 302, y: 90 }],
  ["PTWIN-DEMO-VENCIDO", { photo: vencido, zone: "Banco de calibración", x: 96, y: 90 }],
  ["PTWIN-DEMO-REVISION", { photo: revision, zone: "Almacén", x: 509, y: 90 }],
]);

export function demoInstrumentMedia(instrument) {
  if (instrument.manufacturer !== "PassportTwin Demo" || instrument.location !== "Laboratorio Demo") return null;
  return resources.get(instrument.serial_number) ?? null;
}

export function DemoLocationPlan({ media }) {
  return <figure className="passport-demo-plan">
    <svg viewBox="0 0 600 220" role="img" aria-label={`Plano ficticio de Laboratorio Demo. Instrumento situado en ${media.zone}.`}>
      <rect x="5" y="5" width="590" height="210" rx="10" fill="#f3f6fa" stroke="#9db1c6" strokeWidth="2" />
      <g fill="#eaf1fc" stroke="#9db1c6" strokeWidth="2">
        <rect x="16" y="16" width="169" height="120" rx="6" />
        <rect x="194" y="16" width="212" height="120" rx="6" />
        <rect x="415" y="16" width="169" height="120" rx="6" />
      </g>
      <g fill="#18334c" fontSize="16" fontWeight="600" textAnchor="middle">
        <text x="100" y="48">Banco de calibración</text>
        <text x="300" y="48">Área de trabajo</text>
        <text x="500" y="48">Almacén</text>
        <text x="300" y="178">Pasillo principal</text>
      </g>
      <circle cx={media.x} cy={media.y} r="12" fill="#125e60" stroke="#fff" strokeWidth="3" />
    </svg>
    <figcaption>Plano ficticio · Ubicación de ejemplo: <strong>{media.zone}</strong></figcaption>
  </figure>;
}
