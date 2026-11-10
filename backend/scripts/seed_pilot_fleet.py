"""Add reproducible fleet fixtures to an isolated PassportTwin database."""

import argparse
from datetime import date, timedelta
from decimal import Decimal
import hashlib
import io
import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from reportlab.pdfgen.canvas import Canvas

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.models.calibration import CalibrationEvent
from app.models.document import Document, ExtractedField
from app.models.instrument import InstrumentType, InstrumentUnit
from app.models.maintenance import Incident, MaintenanceEvent
from app.services.analytics_snapshots import create_snapshot
from app.services.audit_service import AuditService


PILOT_VERSION = "water-treatment-pilot-v1"
PRESSURE_ERRORS = ("0.015", "0.022", "0.019", "0.024", "0.021", "0.023", "0.020", "0.022")
TEMPERATURE_ERRORS = ("0.11", "0.14", "0.12", "0.15", "0.13", "0.15", "0.16", "0.14")
PH_ERRORS = ("0.022", "0.029", "0.025", "0.031", "0.034", "0.030", "0.038", "0.035")


def fleet_case(tag, serial, name, model, area, point, criticality, due_days, **scenario):
    manufacturer, family, magnitude, unit, tolerance, errors = {
        "PT": ("WIKA", "Transmisor de presión", "Pressure", "bar", "0.1", PRESSURE_ERRORS),
        "TT": ("Endress+Hauser", "Sonda de temperatura", "Temperature", "°C", "0.5", TEMPERATURE_ERRORS),
        "PH": ("Mettler Toledo", "Electrodo de pH", "pH", "pH", "0.15", PH_ERRORS),
    }[tag.split("-")[0]]
    return dict(
        tag=tag, serial=serial, name=name, manufacturer=manufacturer, model=model,
        family=family, magnitude=magnitude, unit=unit, tolerance=tolerance, errors=errors,
        location=f"Planta A · {area} · {point}", criticality=criticality, due_days=due_days,
    ) | scenario


CASES = (
    dict(tag="PT-101", serial="26A041785", name="Transmisor de presión de impulsión",
         manufacturer="WIKA", model="S-20", family="Transmisor de presión", magnitude="Pressure", unit="bar",
         location="Planta A · Sala de bombas · P-01, impulsión", criticality="HIGH", due_days=120,
         errors=("0.015", "0.022", "0.019", "0.024", "0.021", "0.023", "0.020", "0.022")),
    dict(tag="PT-102", serial="26A041786", name="Transmisor de presión de aspiración",
         manufacturer="WIKA", model="S-20", family="Transmisor de presión", magnitude="Pressure", unit="bar",
         location="Planta A · Sala de bombas · P-01, aspiración", criticality="HIGH", due_days=90,
         errors=("0.021", "0.025", "0.042", "0.041", "0.059", "0.062", "0.077", "0.079")),
    dict(tag="PH-304", serial="26P073613", name="Electrodo de pH de reserva",
         manufacturer="Mettler Toledo", model="InPro 3250i", family="Electrodo de pH", magnitude="pH", unit="pH",
         location="Planta A · Laboratorio de instrumentación · Armario L-02", criticality="LOW", errors=()),
    fleet_case("PT-103", "26A041787", "Transmisor de presión de descarga", "S-20",
               "Sala de bombas", "P-02, descarga", "HIGH", -5),
    fleet_case("PT-104", "26A041788", "Transmisor de presión del colector", "S-20",
               "Filtración", "Colector de entrada", "HIGH", 75, lifecycle="out_of_tolerance", errors=PRESSURE_ERRORS[:-1] + ("0.128",)),
    fleet_case("PT-105", "26A041789", "Transmisor de presión aguas arriba del filtro", "A-10",
               "Filtración", "F-01, entrada", "MEDIUM", 70, document_review="unknown_serial"),
    fleet_case("PT-106", "26A041790", "Transmisor de presión aguas abajo del filtro", "A-10",
               "Filtración", "F-01, salida", "MEDIUM", 60, latest_tolerance="0.08"),
    fleet_case("TT-201", "26T085241", "Sonda de temperatura de alimentación", "iTHERM TM411",
               "Tratamiento", "Línea de alimentación", "HIGH", 15),
    fleet_case("TT-202", "26T085242", "Sonda de temperatura de retorno", "iTHERM TM411",
               "Tratamiento", "Línea de retorno", "MEDIUM", 100, maintenance_days=35),
    fleet_case("TT-203", "26T085243", "Sonda de temperatura del depósito pulmón", "iTHERM TM411",
               "Tratamiento", "Depósito TK-02", "MEDIUM", 100, maintenance_days=100),
    fleet_case("TT-204", "26T085244", "Sonda de temperatura de la salida del intercambiador", "iTHERM TM411",
               "Tratamiento", "Intercambiador HX-01", "HIGH", 100, lifecycle="blocked", incident_days=12),
    fleet_case("PH-301", "26P073610", "Electrodo de pH de entrada", "InPro 3250i",
               "Dosificación", "Entrada de proceso", "MEDIUM", 80, document_review="missing_unit"),
    fleet_case("PH-302", "26P073611", "Electrodo de pH de neutralización", "InPro 3250i",
               "Dosificación", "Reactor R-01", "HIGH", 85, duplicate_date=True),
    fleet_case("PH-303", "26P073612", "Electrodo de pH de control de salida", "InPro 3250i",
               "Dosificación", "Salida de proceso", "HIGH", 80),
    fleet_case("PT-107", "26A041791", "Transmisor de presión de banco", "A-10",
               "Laboratorio de instrumentación", "Banco B-01", "LOW", 100),
    fleet_case("PT-108", "26A041792", "Transmisor de presión de retorno retirado", "S-20",
               "Taller", "Zona de equipos retirados", "LOW", -210, lifecycle="retired", history_offset=270),
)


def add_certificate(db, instrument, case, calibration, review=None):
    values = (
        ("serial_number", "Serial Number", instrument.serial_number),
        ("calibration_date", "Calibration Date", calibration.calibration_date.isoformat()),
        ("next_due_date", "Due Date", calibration.next_due_date.isoformat()),
        ("error_value", "Max Error", str(calibration.error_value)),
        ("tolerance", "Tolerance", str(calibration.tolerance)),
        ("unit", "Unit", case["unit"]),
    )
    if review == "unknown_serial":
        values = (("serial_number", "Serial Number", f"{instrument.serial_number}X"), *values[1:])
    elif review == "missing_unit":
        values = values[:-1]
    stream = io.BytesIO()
    pdf = Canvas(stream, invariant=1)
    pdf.setTitle(f"Certificado de calibración {instrument.serial_number}")
    pdf.drawString(45, 780, f"Certificado de calibración · {case['tag']}")
    pdf.drawString(45, 756, case["name"])
    pdf.drawString(45, 734, f"{case['manufacturer']} · {case['model']}")
    for index, (_, label, value) in enumerate(values):
        pdf.drawString(45, 696 - index * 24, f"{label}: {value}")
    pdf.drawString(45, 500, "Registro sintético para pruebas de PassportTwin.")
    pdf.save()
    payload = stream.getvalue()
    digest = hashlib.sha256(payload).hexdigest()
    raw = Path(os.getenv("STORAGE_RAW_DIR", "./storage/raw")) / "pilot-fleet"
    raw.mkdir(parents=True, exist_ok=True)
    path = raw / f"{digest}.pdf"
    try:
        with path.open("xb") as file:
            file.write(payload)
    except FileExistsError:
        if path.read_bytes() != payload:
            raise ValueError(f"El archivo existente no coincide con el SHA-256 {digest}")
    filename_suffix = "-revision" if review else ""
    document = Document(
        instrument_unit_id=None if review == "unknown_serial" else instrument.id,
        file_path=str(path),
        original_filename=f"CAL-{case['tag']}-{calibration.calibration_date}{filename_suffix}.pdf",
        sha256_hash=digest, source_type="PDF_CERTIFICATE",
        processing_status="REVIEW_REQUIRED" if review else "ACCEPTED",
    )
    db.add(document)
    db.flush()
    for name, _, value in values:
        status = "NOT_EVALUATED" if review or name in {"error_value", "tolerance"} else "VALIDATED"
        db.add(ExtractedField(document_id=document.id, field_name=name, raw_value=value,
                              normalized_value=value, confidence="1.0", validation_status=status))
    if review:
        AuditService.log_event(db, "document", document.id, "PILOT_DOCUMENT_CREATED",
                               source="scripts.seed_pilot_fleet",
                               details={"synthetic_fixture": True, "scenario": review})
        return
    AuditService.log_event(
        db, "instrument_unit", instrument.id, "CALIBRATION_INGESTED", source="scripts.seed_pilot_fleet",
        details={"document_id": document.id, "calibration_event_id": calibration.id,
                 "instrument_id": instrument.id, "certificate_sha256": digest, "synthetic_fixture": True},
    )


def seed_pilot(db, as_of):
    instruments = []
    for case in CASES:
        public_id = uuid5(NAMESPACE_URL, f"urn:passporttwin:{PILOT_VERSION}:{case['serial']}")
        instrument = db.query(InstrumentUnit).filter_by(serial_number=case["serial"]).one_or_none()
        if instrument is not None:
            if instrument.public_id != public_id:
                raise ValueError(f"La serie {case['serial']} ya pertenece a otro instrumento")
            if instrument.technical_name is None:
                instrument.technical_name = case["name"]
            if instrument.plant_tag is None:
                instrument.plant_tag = case["tag"]
            instruments.append((case, instrument, False))
            continue
        family = db.query(InstrumentType).filter_by(name=case["family"]).one_or_none()
        if family is None:
            family = InstrumentType(name=case["family"], magnitude=case["magnitude"], unit=case["unit"])
            db.add(family)
            db.flush()
        if (family.magnitude, family.unit) != (case["magnitude"], case["unit"]):
            raise ValueError(f"La familia {family.name} ya existe con otra magnitud o unidad")
        instrument = InstrumentUnit(
            public_id=public_id, instrument_type_id=family.id, serial_number=case["serial"],
            technical_name=case["name"], plant_tag=case["tag"],
            manufacturer=case["manufacturer"], model=case["model"], location=case["location"],
            criticality=case["criticality"], lifecycle_state=case.get("lifecycle", "operational"),
            installed_at=as_of - timedelta(days=180 + case.get("history_offset", 0) if case["errors"] else 4),
        )
        db.add(instrument)
        db.flush()
        latest = None
        history_offset = case.get("history_offset", 0)
        for index, error in enumerate(case["errors"]):
            remaining = len(case["errors"]) - 1 - index
            days_ago = 7 + remaining * 21 + history_offset
            if case.get("duplicate_date") and remaining == 1:
                days_ago -= 21
            measured = as_of - timedelta(days=days_ago)
            tolerance = Decimal(case.get("tolerance", "0.1"))
            if remaining == 0 and "latest_tolerance" in case:
                tolerance = Decimal(case["latest_tolerance"])
            latest = CalibrationEvent(
                instrument_unit_id=instrument.id, calibration_date=measured,
                error_value=Decimal(error), tolerance=tolerance,
                result="out_of_tolerance" if abs(Decimal(error)) > tolerance else "pass",
                next_due_date=measured + timedelta(days=case["due_days"] + 7 + history_offset),
            )
            db.add(latest)
        if "maintenance_days" in case:
            db.add(MaintenanceEvent(
                instrument_unit_id=instrument.id,
                event_date=as_of - timedelta(days=case["maintenance_days"]),
                description="Sustitución de la sonda y verificación del lazo de temperatura.",
            ))
        if "incident_days" in case:
            db.add(Incident(
                instrument_unit_id=instrument.id,
                incident_date=as_of - timedelta(days=case["incident_days"]),
                severity="HIGH", description="Lectura intermitente en el lazo de temperatura.",
            ))
        if latest is not None:
            db.flush()
            add_certificate(db, instrument, case, latest)
            if "document_review" in case:
                pending = CalibrationEvent(
                    calibration_date=as_of - timedelta(days=1),
                    next_due_date=as_of + timedelta(days=90),
                    error_value=latest.error_value, tolerance=latest.tolerance,
                )
                add_certificate(db, instrument, case, pending, review=case["document_review"])
        AuditService.log_event(db, "instrument_unit", instrument.id, "PILOT_FIXTURE_CREATED",
                               source="scripts.seed_pilot_fleet",
                               details={"dataset_version": PILOT_VERSION, "tag": case["tag"],
                                        "technical_name": case["name"], "reference_date": as_of.isoformat()})
        instruments.append((case, instrument, True))
    db.commit()

    for case, instrument, created in instruments:
        snapshot = db.query(AnalyticsSnapshot).filter_by(instrument_unit_id=instrument.id, as_of=as_of).first()
        if snapshot is None:
            snapshot = create_snapshot(db, instrument, as_of)
        probabilities = [
            f"{value:.1%}" if value is not None else "No estimable"
            for value in (snapshot.probability_30, snapshot.probability_60, snapshot.probability_90)
        ]
        url = f"{str(settings.passport_frontend_base_url).rstrip('/')}/passport/{instrument.public_id}"
        print(f"{case['tag']} · {case['serial']} · {'creado' if created else 'conservado'} · {url}")
        print(f"  {snapshot.risk_status} · {' / '.join(probabilities)} · Health Score: {snapshot.health_score}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, required=True)
    parser.add_argument("--confirm-isolated", action="store_true", required=True)
    args = parser.parse_args()
    with SessionLocal() as db:
        seed_pilot(db, args.as_of)


if __name__ == "__main__":
    main()
