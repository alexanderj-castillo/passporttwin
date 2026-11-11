from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.instruments import list_instruments
from app.models.calibration import CalibrationEvent
from app.models.instrument import InstrumentType, InstrumentUnit


def test_inventory_uses_latest_calibration_available_today():
    engine = create_engine("sqlite://")
    for model in (InstrumentType, InstrumentUnit, CalibrationEvent):
        model.__table__.create(engine)

    today = date.today()
    expected = {
        "current": "CURRENT", "soon": "DUE_SOON", "overdue": "OVERDUE",
        "missing-date": "NO_DUE_DATE", "missing-history": "NO_HISTORY",
    }
    with Session(engine) as db:
        kind = InstrumentType(name="pressure", magnitude="Pressure", unit="bar")
        db.add(kind)
        db.flush()
        units = {
            serial: InstrumentUnit(instrument_type_id=kind.id, serial_number=serial, manufacturer="Test", model="Test")
            for serial in expected
        }
        db.add_all(units.values())
        db.flush()

        def add_calibration(serial, measured, due):
            db.add(CalibrationEvent(
                instrument_unit_id=units[serial].id, calibration_date=measured,
                next_due_date=due, error_value=0, tolerance=1, result="pass",
            ))
            db.flush()

        measured = today - timedelta(days=2)
        add_calibration("current", measured, today - timedelta(days=1))
        add_calibration("current", measured, today + timedelta(days=31))
        add_calibration("current", today + timedelta(days=1), today + timedelta(days=2))
        add_calibration("soon", measured, today + timedelta(days=30))
        add_calibration("overdue", measured, today - timedelta(days=1))
        add_calibration("missing-date", measured, None)
        add_calibration("missing-history", today + timedelta(days=1), None)

        result = list_instruments(db)
        assert len(result) == len(expected)
        assert {item.serial_number: item.calibration_status for item in result} == expected
    engine.dispose()
