"""Validate recorded EXP-07 human observations; never generates participant results."""
import argparse
import csv
from datetime import date, datetime
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / 'exp07/protocol.json'
PARTICIPANT_COLUMNS = ['participant_id', 'role', 'group']
OBSERVATION_COLUMNS = ['participant_id', 'task_id', 'method', 'variant', 'period',
                       'status', 'elapsed_seconds', 'errors', 'assists', 'verified',
                       'evidence_ref', 'observer_ref', 'notes']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path, columns):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError(f'Unexpected columns in {Path(path).name}')
        result = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in result):
        raise ValueError('Malformed CSV row')
    return result


def validate_session(session):
    required = ('study_id', 'environment_ref', 'consent_record_ref')
    if any(not isinstance(session.get(key), str) or not session[key].strip() for key in required):
        raise ValueError('Session identity, environment and consent references required')
    if not re.fullmatch('[0-9a-f]{40}', session.get('app_commit', '')):
        raise ValueError('Full application commit required')
    frozen = datetime.fromisoformat(session['frozen_at'])
    if frozen.tzinfo is None:
        raise ValueError('Freeze timestamp must include timezone')
    date.fromisoformat(session['reference_date'])
    hashes = [session.get('protocol_sha256', ''), session.get('answer_key_sha256', '')]
    for name in ('variant_sha256', 'baseline_sha256', 'passport_snapshot_sha256'):
        hashes.extend(session[name][variant] for variant in ('A', 'B'))
    if any(not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value) for value in hashes):
        raise ValueError('Frozen protocol/datasets/baselines/UI snapshots/answer key hashes required')
    if session['protocol_sha256'] != digest(PROTOCOL):
        raise ValueError('Protocol hash differs from checked-in protocol')


def summarize(participants, observations, session):
    validate_session(session)
    protocol = json.loads(PROTOCOL.read_text())
    tasks = {task['id']: task for task in protocol['tasks']}
    roster = {}
    for row in participants:
        key = row['participant_id']
        if not re.fullmatch('[A-Za-z0-9_-]{1,40}', key) or key in roster:
            raise ValueError('Invalid or duplicated participant pseudonym')
        if not row['role'].strip() or row['group'] not in protocol['groups']:
            raise ValueError('Participant role and AB/BA group required')
        roster[key] = row
    trials = {}
    for row in observations:
        who, task, method = row['participant_id'], row['task_id'], row['method']
        if who not in roster or task not in tasks or method not in protocol['methods']:
            raise ValueError('Unknown participant, task or method')
        key = (who, task, method)
        if key in trials:
            raise ValueError('Duplicate trial; practice/retries must be recorded separately')
        assignment = protocol['groups'][roster[who]['group']][method]
        if row['variant'] != assignment['variant'] or row['period'] != str(assignment['period']):
            raise ValueError('Trial violates assigned order or dataset variant')
        status = row['status']
        if status not in protocol['statuses'] or row['verified'] not in ('true', 'false'):
            raise ValueError('Invalid status or verification flag')
        elapsed = float(row['elapsed_seconds'])
        cap = tasks[task]['timeout_seconds']
        if not math.isfinite(elapsed) or elapsed <= 0 or elapsed > cap:
            raise ValueError('Time must be finite, positive and within task limit')
        if status == 'timeout' and elapsed != cap:
            raise ValueError('Timeout must record full prespecified time limit')
        if any(not re.fullmatch('[0-9]+', row[name]) for name in ('errors', 'assists')):
            raise ValueError('Errors and assists must be nonnegative integers')
        if not row['evidence_ref'].strip() or not row['observer_ref'].strip():
            raise ValueError('Every trial needs evidence and observer references')
        verified = row['verified'] == 'true'
        if status == 'success' and not verified:
            raise ValueError('Success requires observer verification against frozen answer key')
        if (status == 'aborted' or int(row['assists']) > 0) and not row['notes'].strip():
            raise ValueError('Aborts and assistance need an explanation')
        trials[key] = {**row, 'elapsed': elapsed, 'assists_n': int(row['assists']), 'errors_n': int(row['errors'])}
    expected = {(who, task, method) for who in roster for task in tasks for method in protocol['methods']}
    missing = sorted(expected - trials.keys())
    groups = {name: sum(row['group'] == name for row in roster.values()) for name in ('AB', 'BA')}
    cells = []
    pairs = []
    for task in tasks:
        for method in protocol['methods']:
            rows = [row for (who, tid, met), row in trials.items() if tid == task and met == method]
            successes = [row for row in rows if row['status'] == 'success']
            cells.append({'task_id': task, 'method': method, 'planned': len(roster), 'observed': len(rows),
                          'missing': len(roster) - len(rows),
                          'statuses': {status: sum(row['status'] == status for row in rows) for status in protocol['statuses']},
                          'success_fraction_observed': len(successes) / len(rows) if rows else None,
                          'unassisted_successes': sum(row['assists_n'] == 0 for row in successes),
                          'errors': sum(row['errors_n'] for row in rows),
                          'assists': sum(row['assists_n'] for row in rows),
                          'median_success_seconds_conditional': median(row['elapsed'] for row in successes) if successes else None})
        eligible = []
        exclusions = {'missing_method': 0, 'non_success': 0, 'assisted': 0}
        for who in roster:
            pair = [trials.get((who, task, method)) for method in protocol['methods']]
            if any(row is None for row in pair):
                exclusions['missing_method'] += 1
            elif any(row['status'] != 'success' for row in pair):
                exclusions['non_success'] += 1
            elif any(row['assists_n'] for row in pair):
                exclusions['assisted'] += 1
            else:
                manual, passport = pair
                eligible.append({'participant_id': who, 'manual_seconds': manual['elapsed'],
                                 'passport_seconds': passport['elapsed'],
                                 'saved_seconds': manual['elapsed'] - passport['elapsed'],
                                 'saved_percent': 100 * (manual['elapsed'] - passport['elapsed']) / manual['elapsed']})
        pairs.append({'task_id': task, 'eligible_pairs': len(eligible), 'exclusions': exclusions,
                      'median_paired_saved_seconds': median(row['saved_seconds'] for row in eligible) if eligible else None,
                      'median_paired_saved_percent': median(row['saved_percent'] for row in eligible) if eligible else None,
                      'pairs': eligible})
    return {'experiment': 'EXP-07', 'protocol': protocol['version'],
            'execution_status': 'NO_DATA' if not roster else ('INCOMPLETE' if missing else 'COMPLETE_OBSERVATIONS'),
            'validation_status': 'NOT_ESTABLISHED_BY_THIS_TOOL', 'session': session,
            'participants': len(roster), 'groups': groups, 'expected_trials': len(expected),
            'observed_trials': len(trials), 'missing_trials': [list(key) for key in missing],
            'cells': cells, 'paired_timing': pairs,
            'limitations': ['Descriptive results only; no automatic acceptance or causal claim.',
                            'Conditional times exclude failed, missing or assisted pairs; inspect counts and exclusions.',
                            'Evidence references and declared hashes require independent human review.'] +
                            ([] if all(groups.values()) else ['Both counterbalanced groups have not been observed.']) +
                            ([] if len(roster) >= protocol['proposed_sample']['participants'] else ['Roster is below the proposed exploratory sample size.'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--participants', type=Path, required=True)
    parser.add_argument('--observations', type=Path, required=True)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = summarize(read_csv(args.participants, PARTICIPANT_COLUMNS),
                           read_csv(args.observations, OBSERVATION_COLUMNS),
                           json.loads(args.session.read_text(encoding='utf-8')))
        report['inputs_sha256'] = {key: digest(getattr(args, key)) for key in ('participants', 'observations', 'session')}
        report['analyzer_sha256'] = digest(Path(__file__))
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f'EXP-07 input/output rejected ({type(exc).__name__}); check protocol, CSV and new output path.\n')
    print(f"{report['execution_status']}: {args.output}")
    return 0 if report['execution_status'] == 'COMPLETE_OBSERVATIONS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
