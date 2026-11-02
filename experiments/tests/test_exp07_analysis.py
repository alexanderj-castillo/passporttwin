"""Synthetic software checks only: these rows are not participant evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

PATH = Path(__file__).resolve().parents[1] / 'analyze_exp07.py'
spec = importlib.util.spec_from_file_location('exp07', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def inputs():
    session = {'study_id': 'software-test-only', 'app_commit': 'a' * 40,
               'frozen_at': '2026-11-02T12:00:00+00:00', 'reference_date': '2026-11-02',
               'protocol_sha256': m.digest(m.PROTOCOL), 'answer_key_sha256': 'b' * 64,
               'environment_ref': 'test-only', 'consent_record_ref': 'test-only'}
    for name in ('variant_sha256', 'baseline_sha256', 'passport_snapshot_sha256'):
        session[name] = {'A': 'c' * 64, 'B': 'd' * 64}
    roster = [{'participant_id': 'test01', 'role': 'test-only', 'group': 'AB'},
              {'participant_id': 'test02', 'role': 'test-only', 'group': 'BA'}]
    protocol = json.loads(m.PROTOCOL.read_text())
    rows = []
    for person in roster:
        for task in protocol['tasks']:
            for method in protocol['methods']:
                assignment = protocol['groups'][person['group']][method]
                rows.append({'participant_id': person['participant_id'], 'task_id': task['id'],
                             'method': method, 'period': str(assignment['period']), 'variant': assignment['variant'],
                             'status': 'success', 'elapsed_seconds': '100' if method == 'manual' else '50',
                             'errors': '0', 'assists': '0', 'verified': 'true', 'evidence_ref': 'test-only',
                             'observer_ref': 'test-only', 'notes': ''})
    return roster, rows, session


def test_paired_differences_and_denominators():
    result = m.summarize(*inputs())
    assert result['execution_status'] == 'COMPLETE_OBSERVATIONS'
    assert result['expected_trials'] == result['observed_trials'] == 8
    assert result['groups'] == {'AB': 1, 'BA': 1}
    for pair in result['paired_timing']:
        assert pair['eligible_pairs'] == 2
        assert pair['median_paired_saved_seconds'] == 50
        assert pair['median_paired_saved_percent'] == 50
    assert result['validation_status'] == 'NOT_ESTABLISHED_BY_THIS_TOOL'


def test_timeout_assistance_and_missing_pairs_are_never_silently_dropped():
    roster, rows, session = inputs()
    rows[0].update(status='timeout', elapsed_seconds='180', verified='false')
    rows[4].update(assists='1', notes='test assistance')
    rows.pop()  # A missing observation must remain in denominators.
    result = m.summarize(roster, rows, session)
    assert result['execution_status'] == 'INCOMPLETE'
    assert len(result['missing_trials']) == 1
    cert = result['paired_timing'][0]
    assert cert['eligible_pairs'] == 0
    assert cert['exclusions'] == {'missing_method': 0, 'non_success': 1, 'assisted': 1}
    assert cert['median_paired_saved_seconds'] is None
    assert result['cells'][0]['statuses']['timeout'] == 1
    assert result['cells'][0]['success_fraction_observed'] == .5


def test_empty_study_is_no_data_not_success():
    _, _, session = inputs()
    report = m.summarize([], [], session)
    assert report['execution_status'] == 'NO_DATA'
    assert all(row['success_fraction_observed'] is None for row in report['cells'])
    assert all(row['median_paired_saved_seconds'] is None for row in report['paired_timing'])


@pytest.mark.parametrize('changes', [
    {'elapsed_seconds': 'nan'}, {'elapsed_seconds': '0'}, {'elapsed_seconds': '-1'},
    {'elapsed_seconds': '181'}, {'status': 'timeout', 'elapsed_seconds': '20'},
    {'verified': 'false'}, {'errors': '-1'}, {'assists': '1'},
    {'variant': 'B'}, {'period': '2'}, {'evidence_ref': ''}, {'observer_ref': ''},
    {'participant_id': 'unknown'}, {'status': 'aborted', 'notes': ''},
])
def test_invalid_or_unverifiable_trials_rejected(changes):
    roster, rows, session = inputs()
    rows[0].update(changes)
    with pytest.raises(ValueError):
        m.summarize(roster, rows, session)


def test_duplicate_trials_and_participants_rejected():
    roster, rows, session = inputs()
    with pytest.raises(ValueError, match='Duplicate trial'):
        m.summarize(roster, rows + [rows[0]], session)
    with pytest.raises(ValueError, match='duplicated participant'):
        m.summarize(roster + [roster[0]], rows, session)


def test_negative_savings_are_retained():
    roster, rows, session = inputs()
    for row in rows:
        if row['method'] == 'passport':
            row['elapsed_seconds'] = '150'
    assert m.summarize(roster, rows, session)['paired_timing'][0]['median_paired_saved_percent'] == -50


def test_freeze_and_protocol_required():
    roster, rows, session = inputs()
    session['protocol_sha256'] = 'a' * 64
    with pytest.raises(ValueError, match='Protocol hash'):
        m.summarize(roster, rows, session)
    session['protocol_sha256'] = m.digest(m.PROTOCOL)
    session['baseline_sha256']['A'] = ''
    with pytest.raises(ValueError, match='hashes required'):
        m.summarize(roster, rows, session)


def test_blank_templates_have_headers_but_no_fabricated_participants():
    base = PATH.parent / 'exp07'
    assert m.read_csv(base / 'participants-template.csv', m.PARTICIPANT_COLUMNS) == []
    assert m.read_csv(base / 'observations-template.csv', m.OBSERVATION_COLUMNS) == []
    with pytest.raises(ValueError):
        m.summarize([], [], json.loads((base / 'session-template.json').read_text()))


def test_cli_writes_report_then_refuses_overwrite(tmp_path):
    import csv
    roster, rows, session = inputs()
    for name, columns, values in [('participants', m.PARTICIPANT_COLUMNS, roster),
                                   ('observations', m.OBSERVATION_COLUMNS, rows)]:
        with (tmp_path / f'{name}.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader(); writer.writerows(values)
    (tmp_path / 'session.json').write_text(json.dumps(session))
    command = [sys.executable, str(PATH), '--participants', str(tmp_path / 'participants.csv'),
               '--observations', str(tmp_path / 'observations.csv'), '--session', str(tmp_path / 'session.json'),
               '--output', str(tmp_path / 'report.json')]
    assert subprocess.run(command, capture_output=True).returncode == 0
    original = (tmp_path / 'report.json').read_bytes()
    assert subprocess.run(command, capture_output=True).returncode == 2
    assert (tmp_path / 'report.json').read_bytes() == original
