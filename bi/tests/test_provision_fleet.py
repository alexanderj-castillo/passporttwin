import importlib.util
from pathlib import Path

import pytest
import requests

spec = importlib.util.spec_from_file_location('provision_fleet', Path(__file__).parents[1] / 'metabase/provision_fleet.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_dashboard_cards_filters_and_layout_are_created_without_deleting_existing():
    class Response:
        def __init__(self, data): self.data = data
        def raise_for_status(self): pass
        def json(self): return self.data

    class Session:
        def __init__(self): self.posts = []; self.updates = []
        def post(self, url, json, timeout):
            self.posts.append((url,json))
            return Response({'id':len(self.posts)})
        def put(self, url, json, timeout):
            self.updates.append((url,json))
            return Response({})

    session = Session()
    assert module.provision('http://metabase', 2, 3, session) == 'http://metabase/dashboard/1'
    assert len(session.posts) == 12
    for url, card in session.posts[1:]:
        assert card['dataset_query']['database'] == 2
        assert card['collection_id'] == 3
        assert set(card['dataset_query']['native']['template-tags']) == {'family','location'}
    traffic_card = next(card for _, card in session.posts[1:] if card["name"] == "Semáforo de flota")
    settings = traffic_card["visualization_settings"]
    assert settings["graph.dimensions"] == ["estado", "serie_estado"]
    assert settings["graph.metrics"] == ["instruments"]
    assert settings["series_settings"] == {
        "Rojo · Requiere atención": {"color": "#B91C1C"},
        "Amarillo · Aviso": {"color": "#D4A017"},
        "Gris · Datos insuficientes": {"color": "#64748B"},
        "Verde · Sin alertas": {"color": "#15803D"},
    }
    dashcards = session.updates[0][1]['dashcards']
    assert len(dashcards) == 9
    names_by_id = {card_id: card["name"] for card_id, (_, card) in enumerate(session.posts[1:], 2)}
    dashboard_names = [names_by_id[card["card_id"]] for card in dashcards]
    assert dashboard_names[4:7] == [
        "Prioridad de intervención", "Semáforo de flota", "Vencimientos en los próximos 90 días",
    ]
    assert set(names_by_id.values()) - set(dashboard_names) == {
        "Health Score · por versión y pesos", "Riesgo experimental · detalle técnico",
    }
    assert all(len(card['parameter_mappings']) == 2 for card in dashcards)
    assert all(card['col'] + card['size_x'] <= 24 for card in dashcards)


def test_http_errors_propagate_without_claiming_success():
    class Session:
        def post(self, *args, **kwargs):
            response = requests.Response()
            response.status_code = 403
            return response

    with pytest.raises(requests.HTTPError):
        module.provision('http://metabase',2,3,Session())


def test_passport_links_have_configured_origin_and_raw_units_remain_available():
    cards = {name: sql for name, _, sql in module.cards('https://passport.example.com/')}
    assert 'measurement_unit' in module.BASE
    for name in (
        "Prioridad de intervención", "Vencimientos en los próximos 90 días",
        "Riesgo experimental · 30, 60 y 90 días", "Riesgo experimental · detalle técnico",
    ):
        assert "'https://passport.example.com' || '/passport/' || public_id::text AS passport_url" in cards[name]
    assert "COALESCE(NULLIF(BTRIM(plant_tag), ''), serial_number)" in cards["Prioridad de intervención"]
    assert 'serial_number AS "Número de serie"' in cards["Prioridad de intervención"]
    assert "days_to_due BETWEEN 0 AND 90" in cards["Vencimientos en los próximos 90 días"]
    assert "measurement_unit" in cards["Riesgo experimental · detalle técnico"]
    with pytest.raises(ValueError):module.cards('javascript:alert(1)')
    with pytest.raises(ValueError):module.cards('https://user:pass@example.com')
