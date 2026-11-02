"""Track only checks actually performed by the documentary rule engine."""
from app.services.document_validation import _resolve_canonical_unit

EVIDENCE_FIELDS = {'serial_candidates', '__full_text__'}
CHECKED_FIELDS = {'serial_number', 'calibration_date', 'next_due_date', 'unit', 'operating_range'}


def invalidate_fields(fields):
    for field in fields:
        field.validation_status = ('EVIDENCE' if field.field_name in EVIDENCE_FIELDS else
                                   'STAGING' if field.field_name in CHECKED_FIELDS else 'NOT_EVALUATED')


def validate_field_states(db, document, fields, rules_failed, target):
    values = {field.field_name: field.normalized_value for field in fields}
    codes = {rule.split(':', 1)[0] for rule in rules_failed}
    canonical_unit = _resolve_canonical_unit(db, target) if target and values.get('unit') else None
    for field in fields:
        name, value = field.field_name, field.normalized_value
        state = 'NOT_EVALUATED'
        if name in EVIDENCE_FIELDS:
            state = 'EVIDENCE'
        elif document.source_type == 'PDF_CERTIFICATE':
            if name == 'serial_number':
                state = 'REVIEW_REQUIRED' if not value or codes & {'R-ID-01', 'R-ID-AMBIGUOUS'} else 'VALIDATED'
            elif name == 'calibration_date':
                state = 'REVIEW_REQUIRED' if not value or codes & {'R-DATE-01', 'R-DATE-02'} else 'VALIDATED'
            elif name == 'next_due_date' and value and values.get('calibration_date'):
                state = 'REVIEW_REQUIRED' if 'R-DATE-02' in codes else 'VALIDATED'
            elif name == 'unit' and value and canonical_unit:
                state = 'REVIEW_REQUIRED' if 'R-UNIT-01' in codes else 'VALIDATED'
            elif name == 'operating_range' and value:
                state = 'REVIEW_REQUIRED' if 'R-RANGE-01' in codes else 'VALIDATED'
        field.validation_status = state


def field_states(fields):
    return [{'field_id': field.id, 'field_name': field.field_name, 'validation_status': field.validation_status} for field in fields]
