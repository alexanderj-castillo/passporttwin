"""Create a fresh reviewable dashboard in an existing Metabase collection.

Uses METABASE_SESSION_TOKEN or METABASE_API_KEY; never prints credentials.
Does not change existing dashboards. Re-running deliberately creates a new copy.
"""
import argparse
import os
from urllib.parse import urlsplit

import requests


BASE = "SELECT f.*, i.plant_tag, t.unit AS measurement_unit FROM passporttwin_bi.fleet_analytics f JOIN instrument_unit i ON i.id=f.instrument_id JOIN instrument_type t ON t.id=i.instrument_type_id WHERE 1=1 [[AND f.family = {{family}}]] [[AND f.location = {{location}}]]"


def translated(column, mapping, alias):
    return 'CASE '+column+' '+''.join("WHEN '"+key+"' THEN '"+value+"' " for key,value in mapping.items())+"ELSE 'Sin clasificar' END AS "+alias


TRAFFIC_STATES = {
    "red": ("Rojo", "#B91C1C"),
    "yellow": ("Amarillo", "#D4A017"),
    "gray": ("Gris", "#64748B"),
    "green": ("Verde", "#15803D"),
}
TRAFFIC_LEGEND = {
    "red": "Rojo · Requiere atención",
    "yellow": "Amarillo · Aviso",
    "gray": "Gris · Datos insuficientes",
    "green": "Verde · Sin alertas",
}
TECHNICAL_CARDS = {"Health Score · por versión y pesos", "Riesgo experimental · detalle técnico"}


def cards(passport_base_url="http://localhost:5173"):
    parsed=urlsplit(passport_base_url)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
        raise ValueError('Passport URL must be an HTTP(S) origin without credentials or query')
    literal="'"+passport_base_url.rstrip('/').replace("'", "''")+"'"
    traffic_labels = {state: label for state, (label, _) in TRAFFIC_STATES.items()}
    traffic = translated("traffic_light", traffic_labels, "estado")
    traffic_series = translated("traffic_light", TRAFFIC_LEGEND, "serie_estado")
    priority_state = translated("traffic_light", traffic_labels, '"Estado"')
    instrument = "COALESCE(NULLIF(BTRIM(plant_tag), ''), serial_number)" + ' AS "Instrumento"'
    passport = literal + " || '/passport/' || public_id::text AS passport_url"
    freshness = translated("analytics_status", {
        "CURRENT": "Vigente", "MISSING": "Sin cálculo guardado",
        "STALE_DATE": "Pendiente por fecha", "STALE_INPUTS": "Pendiente por cambios",
    }, '"Estado del cálculo"')
    reasons = translated("primary_reason", {
        "LIFECYCLE_ALERT": "Alerta de estado", "OUT_OF_TOLERANCE": "Fuera de tolerancia",
        "CALIBRATION_OVERDUE": "Calibración vencida", "NO_CALIBRATION": "Sin calibración",
        "INVALID_METROLOGY": "Valores por revisar", "MISSING_DUE_DATE": "Falta próximo vencimiento",
        "DUE_WITHIN_30_DAYS": "Vence en 30 días", "DOCUMENT_REVIEW": "Revisión documental",
        "NEAR_TOLERANCE": "Próximo a tolerancia", "AAS_SYNC_ERROR": "Error de sincronización",
        "NO_ALERT": "Sin alertas",
    }, '"Motivo"')
    return [
        ("Instrumentos activos", "scalar", "SELECT COUNT(*) AS instruments FROM fleet"),
        ("Calibraciones vencidas", "scalar", "SELECT COUNT(*) AS overdue FROM fleet WHERE days_to_due < 0"),
        ("Vencen en 30 días", "scalar", "SELECT COUNT(*) AS due_soon FROM fleet WHERE days_to_due BETWEEN 0 AND 30"),
        ("Documentos vinculados por revisar", "scalar", "SELECT COALESCE(SUM(documents_to_review),0) AS reviews FROM fleet"),
        ("Prioridad de intervención", "table",
         f'SELECT {instrument}, location AS "Ubicación", '
         f'{priority_state}, {reasons}, '
         f'days_to_due AS "Días al vencimiento", {passport}, serial_number AS "Número de serie" '
         "FROM fleet ORDER BY priority_rank, CASE UPPER(criticality) WHEN 'HIGH' THEN 1 "
         "WHEN 'MEDIUM' THEN 2 ELSE 3 END, days_to_due NULLS LAST, instrument_id LIMIT 50"),
        ("Semáforo de flota", "bar", f"SELECT {traffic}, {traffic_series}, COUNT(*) AS instruments "
         "FROM fleet GROUP BY traffic_light ORDER BY MIN(priority_rank)"),
        ("Vencimientos en los próximos 90 días", "table",
         f'SELECT {instrument}, location AS "Ubicación", next_due_date AS "Fecha de vencimiento", '
         f'days_to_due AS "Días restantes", {passport} FROM fleet '
         "WHERE days_to_due BETWEEN 0 AND 90 ORDER BY days_to_due, instrument_id"),
        ("Actualización de los cálculos", "table",
         f'SELECT {freshness}, COUNT(*) AS "Instrumentos" FROM fleet GROUP BY analytics_status ORDER BY analytics_status'),
        ("Riesgo experimental · 30, 60 y 90 días", "table",
         f'SELECT {instrument}, analytics_as_of AS "Fecha de referencia", '
         '100 * current_probability_30 AS "30 días (%)", 100 * current_probability_60 AS "60 días (%)", '
         f'100 * current_probability_90 AS "90 días (%)", {freshness}, {passport} '
         "FROM fleet ORDER BY current_probability_90 DESC NULLS LAST, instrument_id LIMIT 50"),
        ("Health Score · por versión y pesos", "table", "SELECT score_method_version, score_weights::jsonb::text AS weights, COUNT(current_health_score) AS instruments_with_score, AVG(current_health_score) AS mean_health_score FROM fleet WHERE current_health_score IS NOT NULL GROUP BY score_method_version, score_weights::jsonb::text ORDER BY score_method_version, score_weights::jsonb::text"),
        ("Riesgo experimental · detalle técnico", "table",
         f"SELECT {passport}, serial_number, family, location, {freshness}, analytics_as_of, analytics_computed_at, "
         "score_status, score_reason, current_health_score, risk_status, risk_reason, risk_uncertainty_90, "
         "current_probability_30, current_probability_60, current_probability_90, risk_method_version, "
         "measurement_unit, observed_error_ratio, documents_to_review, criticality FROM fleet "
         "ORDER BY current_probability_90 DESC NULLS LAST, current_health_score ASC NULLS LAST, instrument_id LIMIT 50"),
    ]



def provision(url, database_id, collection_id, session, passport_base_url="http://localhost:5173"):
    definitions=cards(passport_base_url)  # Validate before creating remote objects.
    def post(path, payload):
        response = session.post(url.rstrip('/') + '/api/' + path, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    dashboard = post("dashboard", {
        "name": "PassportTwin · Flota operativa",
        "description": "Semáforo basado en datos observados; no equivale a probabilidad predictiva ni Health Score.",
        "collection_id": collection_id,
        "parameters": [{"id": key, "name": label, "slug": key, "type": "string/="}
                       for key, label in (("family", "Familia"), ("location", "Ubicación"))],
    })
    dashcards = []
    for index, (name, display, sql) in enumerate(definitions):
        visualization_settings = {}
        if name == "Semáforo de flota":
            visualization_settings = {
                "graph.dimensions": ["estado", "serie_estado"],
                "graph.metrics": ["instruments"],
                "stackable.stack_type": "stacked",
                "series_settings": {TRAFFIC_LEGEND[state]: {"color": color}
                                    for state, (_, color) in TRAFFIC_STATES.items()},
            }
        card = post("card", {
            "name": name, "display": display, "collection_id": collection_id,
            "visualization_settings": {"column_settings": {
                '["name","passport_url"]': {"view_as":"link", "link_text":"Abrir pasaporte", "column_title":"Pasaporte"},
                '["name","measurement_unit"]': {"column_title":"Unidad del instrumento"}
            }} if "passport_url" in sql else visualization_settings,
            "dataset_query": {"database": database_id, "type": "native", "native": {
                "query": "WITH fleet AS (" + BASE + ") " + sql,
                "template-tags": {key: {"id": key, "name": key, "display-name": key,
                                         "type": "text", "required": False}
                                  for key in ("family", "location")},
            }},
        })
        if name in TECHNICAL_CARDS:
            continue
        if index < 4:
            row, col, width, height = 0, index * 6, 6, 3
        else:
            row, col, width, height = 3 + (index - 4) * 6, 0, 24, 6
        dashcards.append({
            "id": -(index + 1), "card_id": card["id"], "row": row, "col": col,
            "size_x": width, "size_y": height,
            "parameter_mappings": [{"parameter_id": key, "card_id": card["id"],
                                    "target": ["variable", ["template-tag", key]]}
                                   for key in ("family", "location")],
        })
    response = session.put(url.rstrip('/') + f'/api/dashboard/{dashboard["id"]}',
                           json={"dashcards": dashcards}, timeout=60)
    response.raise_for_status()
    return url.rstrip('/') + f'/dashboard/{dashboard["id"]}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database-id', type=int, required=True)
    parser.add_argument('--collection-id', type=int, required=True)
    parser.add_argument('--passport-base-url', default=os.getenv("PASSPORT_FRONTEND_BASE_URL", "http://localhost:5173"))
    args = parser.parse_args()
    url = os.environ['METABASE_URL']
    session = requests.Session()
    if os.getenv('METABASE_API_KEY'):
        session.headers['x-api-key'] = os.environ['METABASE_API_KEY']
    else:
        session.headers['X-Metabase-Session'] = os.environ['METABASE_SESSION_TOKEN']
    print(provision(url, args.database_id, args.collection_id, session, args.passport_base_url))


if __name__ == '__main__':
    main()
