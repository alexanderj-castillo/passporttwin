import React from "react";
import sano from "./assets/demo/sano.webp";
import vencido from "./assets/demo/vencido.webp";
import revision from "./assets/demo/revision.webp";

const resources = new Map([
  ["PTWIN-DEMO-SANO", { photo: sano, zone: "Área de trabajo", x: 361, y: 157 }],
  ["PTWIN-DEMO-VENCIDO", { photo: vencido, zone: "Banco de calibración", x: 174, y: 157 }],
  ["PTWIN-DEMO-REVISION", { photo: revision, zone: "Almacén", x: 534, y: 157 }],
]);

export function demoInstrumentMedia(instrument) {
  if (instrument.manufacturer !== "PassportTwin Demo" || instrument.location !== "Laboratorio Demo") return null;
  return resources.get(instrument.serial_number) ?? null;
}

export function DemoLocationPlan({ media }) {
  return <figure className="passport-demo-plan">
    <svg viewBox="0 0 720 410" role="img" aria-label={`Plano ficticio de Laboratorio Demo. Instrumento situado en ${media.zone}.`}>
      <rect x="1" y="1" width="718" height="408" fill="#fbfdff" stroke="#9db1c6" />
      <text x="22" y="30" fill="#18334c" fontSize="20" fontWeight="700">LABORATORIO DEMO</text>
      <text x="698" y="30" fill="#526579" fontSize="13" textAnchor="end">PLANTA DE DISTRIBUCIÓN · A-01</text>

      {/* Cotas exteriores y marcas de extremo. */}
      <g fill="none" stroke="#60768b" strokeWidth="1">
        <path d="M100 73V52m480 21V52M100 59h480m-485 5 10-10m470 10 10-10" />
        <path d="M92 80H65m27 240H65M73 80v240m-5-235 10-10m-10 250 10-10" />
      </g>
      <g fill="#526579" fontSize="14" textAnchor="middle">
        <text x="340" y="55">12,00 m</text>
        <text x="60" y="200" transform="rotate(-90 60 200)">6,00 m</text>
      </g>

      <rect x="100" y="80" width="480" height="240" fill="#f2f6fa" />
      <g fill="#fff">
        <rect x="104" y="84" width="150" height="143" />
        <rect x="261" y="84" width="170" height="143" />
        <rect x="438" y="84" width="138" height="143" />
      </g>
      {/* Muros exteriores e interiores con huecos de paso. */}
      <g fill="none" stroke="#18334c" strokeWidth="7">
        <path d="M100 274V80h480v240H100v-13M258 80v150M435 80v150" />
        <path d="M100 230h99m31 0h149m31 0h121m31 0h18" />
      </g>
      <g fill="none" stroke="#60768b" strokeWidth="1.5">
        <path d="M199 230v-31a31 31 0 0 1 31 31M379 230v-31a31 31 0 0 1 31 31M531 230v-31a31 31 0 0 1 31 31" />
        <path d="M100 307h33a33 33 0 0 0-33-33" />
      </g>
      {/* Bancos y estanterías en planta. */}
      <g fill="#eaf1fc" stroke="#71879b" strokeWidth="1.2">
        <rect x="119" y="135" width="108" height="43" rx="2" />
        <rect x="282" y="135" width="126" height="43" rx="2" />
        <rect x="452" y="134" width="34" height="67" rx="2" />
        <rect x="513" y="134" width="46" height="45" rx="2" />
        <path d="M452 156h34m-34 22h34m41-44v45m16-45v45" />
      </g>
      <g fill="#18334c" fontSize="15" fontWeight="650" textAnchor="middle">
        <text x="179" y="113">Banco de calibración</text>
        <text x="347" y="113">Área de trabajo</text>
        <text x="508" y="113">Almacén</text>
        <text x="340" y="283">Pasillo principal</text>
      </g>
      <text x="110" y="343" fill="#526579" fontSize="13">Acceso</text>
      <g fill="none" stroke="#526579" strokeWidth="1.5">
        <path d="M630 128V90l-8 13m8-13 8 13" />
        <path d="M600 320v-7h80v7m-40-7v7" />
      </g>
      <g fill="#526579" fontSize="12" textAnchor="middle">
        <text x="630" y="84">N</text><text x="600" y="338">0</text><text x="640" y="338">1</text><text x="680" y="338">2 m</text>
      </g>
      <g transform={`translate(${media.x} ${media.y})`}>
        <circle r="13" fill="#125e60" stroke="#fff" strokeWidth="3" />
        <path d="M-5 0H5M0-5V5" stroke="#fff" strokeWidth="1.7" />
      </g>
      <path d="M22 365h676" stroke="#9db1c6" />
      <circle cx="31" cy="385" r="6" fill="#125e60" />
      <text x="45" y="390" fill="#18334c" fontSize="14">Instrumento seleccionado</text>
      <text x="698" y="390" fill="#526579" fontSize="13" textAnchor="end">PLANO FICTICIO · COTAS DE EJEMPLO</text>
    </svg>
    <figcaption>Plano ficticio · Ubicación de ejemplo: <strong>{media.zone}</strong></figcaption>
  </figure>;
}
