"""Add three reproducible fleet fixtures to an isolated PassportTwin database."""

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
from app.services.analytics_snapshots import create_snapshot
from app.services.audit_service import AuditService


PILOT_VERSION = "water-treatment-pilot-v1"
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
)


def add_certificate(db, instrument, case, calibration):
    values = (
        ("serial_number", "Serial Number", instrument.serial_number),
        ("calibration_date", "Calibration Date", calibration.calibration_date.isoformat()),
        ("next_due_date", "Due Date", calibration.next_due_date.isoformat()),
        ("error_value", "Max Error", str(calibration.error_value)),
        ("tolerance", "Tolerance", str(calibration.tolerance)),
        ("unit", "Unit", case["unit"]),
    )
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
    document = Document(instrument_unit_id=instrument.id, file_path=str(path),
                        original_filename=f"CAL-{case['tag']}-{calibration.calibration_date}.pdf",
                        sha256_hash=digest, source_type="PDF_CERTIFICATE", processing_status="ACCEPTED")
    db.add(document)
    db.flush()
    for name, _, value in values:
        status = "NOT_EVALUATED" if name in {"error_value", "tolerance"} else "VALIDATED"
        db.add(ExtractedField(document_id=document.id, field_name=name, raw_value=value,
                              normalized_value=value, confidence="1.0", validation_status=status))
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
            criticality=case["criticality"], installed_at=as_of - timedelta(days=180 if case["errors"] else 4),
        )
        db.add(instrument)
        db.flush()
        latest = None
        for index, error in enumerate(case["errors"]):
            measured = as_of - timedelta(days=7 + (len(case["errors"]) - 1 - index) * 21)
            latest = CalibrationEvent(
                instrument_unit_id=instrument.id, calibration_date=measured,
                error_value=Decimal(error), tolerance=Decimal("0.1"), result="pass",
                next_due_date=measured + timedelta(days=case["due_days"] + 7),
            )
            db.add(latest)
        if latest is not None:
            db.flush()
            add_certificate(db, instrument, case, latest)
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
            f"{value:.3%}" if value is not None else "No estimable"
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
