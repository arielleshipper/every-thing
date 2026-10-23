#!/usr/bin/env python3
"""Private, account-scoped Codex metadata learning; no model or network calls."""
import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
DAY = 86400


def stamp(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
        except ValueError:
            pass
    return None


def finite(value, minimum=0, maximum=float('inf')):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and minimum <= value <= maximum


def windows(raw):
    result = []
    mapping = raw.get('rateLimitsByLimitId')
    if not isinstance(mapping, dict) or not mapping:
        legacy = raw.get('rateLimits') or {}
        mapping = {legacy.get('limitId', 'codex'): legacy}
    for key, limits in mapping.items():
        if key != 'codex' or not isinstance(limits, dict):
            continue
        for slot in ('primary', 'secondary'):
            w = limits.get(slot)
            if not isinstance(w, dict):
                continue
            used = w.get('usedPercent', w.get('used_percent'))
            renewal = stamp(w.get('resetsAt', w.get('resets_at')))
            minutes = w.get('windowDurationMins', w.get('window_minutes'))
            if finite(used, 0, 100) and renewal and finite(minutes, 1):
                result.append({'id': key + ':' + slot, 'used': used, 'renewal': renewal, 'minutes': minutes})
    return result


def read_json(path, default):
    if not path.exists():
        return default
    with path.open() as f:
        return json.load(f)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, separators=(',', ':'))
        os.replace(tmp, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextlib.contextmanager
def lock(root):
    import fcntl
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    with (root / '.lock').open('a') as f:
        os.chmod(root / '.lock', 0o600)
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def current_creator(source, account):
    """Bind workspace-scoped account IDs to the current local thread's user."""
    thread = os.environ.get('CODEX_THREAD_ID')
    creators = set()
    for path in source.rglob('*.jsonl') if source.exists() else []:
        if path.is_symlink():
            continue
        try:
            with path.open('rb') as f:
                meta = json.loads(f.readline()).get('payload', {})
        except (OSError, ValueError, UnicodeError):
            continue
        if meta.get('creator_account_id') != account:
            continue
        creator = meta.get('creator_user_id')
        if creator:
            creators.add(creator)
            if thread and meta.get('id') == thread:
                return creator
    return next(iter(creators)) if len(creators) == 1 else None


def collect(source, state, account, now, creator=None):
    """Only metadata from matching-account files; incremental complete-line reads."""
    cutoff = now - 28 * DAY
    active = set(state.get('active', []))
    samples = {tuple(s[:3]): s for s in state.get('samples', [])}
    cursors = state.setdefault('cursors', {})
    stats = {'matched_files': 0, 'unmatched_files': 0, 'malformed_lines': 0, 'new_lines': 0}
    for path in source.rglob('*.jsonl') if source.exists() else []:
        if path.is_symlink() or path.stat().st_mtime < cutoff:
            continue
        key = hashlib.sha256(str(path).encode()).hexdigest()
        with path.open('rb') as f:
            try:
                first = json.loads(f.readline())
            except (ValueError, UnicodeError):
                stats['malformed_lines'] += 1
                continue
            meta = first.get('payload', {})
            if (first.get('type') != 'session_meta' or meta.get('creator_account_id') != account
                    or (creator is not None and meta.get('creator_user_id') != creator)):
                stats['unmatched_files'] += 1
                continue
            stats['matched_files'] += 1
            cursor = cursors.get(key, {})
            size = path.stat().st_size
            # Content replacement/truncation invalidates a cursor, even at equal size.
            signature = hashlib.sha256(json.dumps(meta.get('id')).encode()).hexdigest()
            offset = cursor.get('offset', 0) if cursor.get('signature') == signature else 0
            if offset > size:
                offset = 0
            f.seek(offset)
            while True:
                start = f.tell()
                line = f.readline()
                if not line:
                    break
                if not line.endswith(b'\n'):
                    f.seek(start)
                    break
                stats['new_lines'] += 1
                try:
                    row = json.loads(line)
                except (ValueError, UnicodeError):
                    stats['malformed_lines'] += 1
                    continue
                when = stamp(row.get('timestamp'))
                if when is None or not cutoff <= when <= now:
                    continue
                p = row.get('payload') or {}
                if row.get('type') == 'response_item' and p.get('type') == 'message' and p.get('role') == 'user':
                    active.add(int(when // 60) * 60)
                if row.get('type') == 'event_msg' and p.get('type') == 'token_count':
                    limits = p.get('rate_limits')
                    if isinstance(limits, dict):
                        wrapper = {'rateLimits': dict(limits, limitId=limits.get('limit_id', 'codex'))}
                        for w in windows(wrapper):
                            s = [w['id'], w['renewal'], int(when // 900) * 900, w['used']]
                            samples[tuple(s[:3])] = s
            cursors[key] = {'offset': f.tell(), 'signature': signature}
    state['active'] = sorted(t for t in active if cutoff <= t <= now)
    state['samples'] = sorted((s for s in samples.values() if cutoff <= s[2] <= now), key=lambda s: s[2])
    state['collection'] = stats


def profile(state, zone):
    local = [dt.datetime.fromtimestamp(t, zone) for t in state.get('active', [])]
    days = {t.date() for t in local}
    bins = {}
    dates_by_weekday = {}
    for day in days:
        dates_by_weekday.setdefault(day.weekday(), set()).add(day)
    # A bin records active dates, not message volume: long threads don't dominate.
    for t in local:
        bins.setdefault((t.weekday(), t.hour), set()).add(t.date())
    latest_day = max(days) if days else None
    recency = {day: math.exp(-(latest_day-day).days / 14) for day in days}
    weights = {f'{d}:{h}': sum(recency[x] for x in dates) / sum(recency[x] for x in dates_by_weekday[d]) for (d, h), dates in bins.items()}
    intervals = {}
    previous = {}
    samples = state.get('samples', [])
    recent_cutoff = max((s[2] for s in samples), default=0) - 7 * DAY
    for wid, renewal, when, used in samples:
        key = (wid, renewal)
        prev = previous.get(key)
        if prev:
            hours = (when - prev[0]) / 3600
            delta = used - prev[1]
            if when >= recent_cutoff and 0.25 <= hours <= 6 and 0 < delta <= 30:
                intervals.setdefault(wid, []).append(delta / hours)
        previous[key] = (when, used)
    rates = {}
    for wid, values in intervals.items():
        values = sorted(values)
        rates[wid] = {'typical': statistics.median(values), 'high': values[int((len(values)-1)*0.8)], 'intervals': len(values)}
    starts = [min(t.hour for t in local if t.date() == day) for day in days]
    hours = sorted({h for (d, h) in bins if weights[f'{d}:{h}'] >= 0.5})
    return {'active_days': len(days), 'usual_hours': hours,
            'suggested_daily_hour': int(statistics.median(starts)) if len(days) >= 7 else None,
            'weights': weights, 'rates': rates,
            'timezone': str(zone), 'coverage': 'Matching-account local Codex sessions only; other devices may contribute to allowance use.'}


def active_hours(p, now, end, zone):
    total = 0
    next_active = None
    at = now
    while at < min(end, now + 7 * DAY):
        local = dt.datetime.fromtimestamp(at, zone)
        weight = p['weights'].get(f'{local.weekday()}:{local.hour}', 0)
        span = min(3600 - at % 3600, end - at)
        total += weight * span / 3600
        if weight >= 0.25 and next_active is None:
            next_active = at
        at += span
    return total, next_active


def evaluate(raw, state, now, zone, working=False):
    result = {'outcome': 'needs_information', 'reason': '', 'notify': False, 'checked_at': now,
              'windows': [], 'resets': [], 'profile': profile(state, zone)}
    p = result['profile']
    ws = windows(raw)
    if not ws:
        result['reason'] = 'No valid current general Codex allowance windows.'
        return result
    if any(w['renewal'] <= now for w in ws):
        result['reason'] = 'Allowance renewal is already past; refresh the live tool.'
        return result
    inv = raw.get('rateLimitResetCredits')
    if not isinstance(inv, dict) or not isinstance(inv.get('credits'), list):
        result['reason'] = 'Reset inventory is unavailable; purchased credits are not resets.'
        return result
    credits = inv['credits']
    if not finite(inv.get('availableCount')) or int(inv['availableCount']) != inv['availableCount']:
        result['reason'] = 'Reset count is unknown or invalid.'
        return result
    available = [c for c in credits if c.get('status') == 'available']
    if len(available) != inv['availableCount']:
        result['reason'] = 'Reset count disagrees with inventory; refresh before advice.'
        return result
    if any(stamp(c.get('expiresAt')) is None for c in available):
        result['reason'] = 'A reset expiry is unknown; refresh before advice.'
        return result
    eligible = sorted((c for c in available if c.get('resetType') == 'codexRateLimits' and stamp(c['expiresAt']) > now), key=lambda c: (stamp(c['expiresAt']), str(c.get('id'))))
    result['resets'] = [{'expires_at': stamp(c['expiresAt']), 'type': c['resetType']} for c in eligible]
    risks = []
    confident = True
    for w in ws:
        rate = p['rates'].get(w['id'], {})
        learned = p['active_days'] >= 7 and rate.get('intervals', 0) >= 3
        confident &= learned
        hours, next_active = active_hours(p, now, w['renewal'], zone)
        next_day_hours, _ = active_hours(p, now, min(w['renewal'], now + DAY), zone)
        demand = hours * rate.get('typical', 0) if learned else None
        before_next_check = next_day_hours * rate.get('typical', 0) if learned else None
        high = hours * rate.get('high', 0) if learned else None
        item = dict(w, remaining=100-w['used'], predicted_demand=demand,
                    high_demand=high, demand_before_next_check=before_next_check,
                    next_active=next_active, confidence='learned' if learned else 'learning')
        result['windows'].append(item)
        if learned and before_next_check > item['remaining']:
            risks.append(item)
        elif working and w['used'] >= 90:
            risks.append(item)
    if not eligible:
        result.update(outcome='wait', reason='No unexpired supported full resets are available.')
    elif not risks:
        result.update(outcome='wait' if confident else 'learning', reason='Measured capacity covers expected use until the next daily check; save your resets for now.' if confident else 'Learning your active hours and allowance pace; no personalized spending claim yet.')
    else:
        # Full Codex resets affect both general windows; no reset-type guessing.
        soon = min(w['renewal'] for w in risks)
        next_active = min((w['next_active'] for w in risks if w['next_active'] is not None), default=None)
        if not working and next_active is not None and next_active >= soon:
            result.update(outcome='wait', reason='Natural renewal precedes the next expected useful session.')
        elif not working and soon - now <= 3600:
            result.update(outcome='wait', reason='Natural renewal is within an hour; saving a reset is preferable without urgent intent.')
        else:
            chosen = eligible[0]
            expiry = stamp(chosen['expiresAt'])
            if next_active is not None and expiry <= next_active and not working:
                # Consider later batches instead of discarding useful inventory.
                eligible = [c for c in eligible if stamp(c['expiresAt']) > next_active]
                if not eligible:
                    result.update(outcome='wait', reason='Available resets expire before predicted useful activity.')
                    return result
                chosen = eligible[0]
                expiry = stamp(chosen['expiresAt'])
            # Supply-v-demand after a full refill: reserve for a second full-capacity shortage.
            future_need = any((w['predicted_demand'] or 0) > (w['remaining'] + 100) for w in risks)
            if future_need and len(eligible) == 1 and expiry > soon and not working:
                result.update(outcome='save', reason='One reset may not cover predicted repeated shortages; choose which session matters most.')
            else:
                result.update(outcome='use_now', reason='A full reset can cover predicted useful activity before renewal.' if confident else 'You explicitly plan to work now and measured allowance is at least 90% used; timing is based on your intent, not a learned forecast.', selected_expiry=expiry)
                result['_credit_id'] = chosen['id']
    return result


def command(args):
    root = Path(args.state_dir).expanduser()
    zone = ZoneInfo(args.timezone)
    now = dt.datetime.now(UTC).timestamp()
    with lock(root):
        index = read_json(root / 'index.json', {})
        if args.command != 'check':
            key = index.get('current')
            if not key:
                return {'outcome': 'needs_information', 'reason': 'Run a fresh check first.'}
            path = root / (key + '.json')
            state = read_json(path, {})
            if args.command == 'snooze':
                state['snooze_until'] = now + args.hours * 3600
            elif args.command == 'clear-profile':
                for field in ('active', 'samples', 'cursors'):
                    state.pop(field, None)
                # Reimport is intentionally blocked through clear time.
                state['cleared_at'] = now
            save(path, state)
            return {'outcome': args.command, 'cached': True, 'last_result': state.get('last_result'), 'snooze_until': state.get('snooze_until')}
        raw = json.load(sys.stdin)
        account = raw.get('accountId')
        if not isinstance(account, str) or not account:
            return {'outcome': 'needs_information', 'reason': 'Live response lacks account identity.', 'notify': False}
        source = Path(args.sessions_dir).expanduser()
        creator = current_creator(source, account)
        key = hashlib.sha256((account + ':' + (creator or 'unresolved-user')).encode()).hexdigest()
        path = root / (key + '.json')
        state = read_json(path, {})
        prior_day = dt.datetime.fromtimestamp(state.get('last_scheduled', 0), zone).date()
        today = dt.datetime.fromtimestamp(now, zone).date()
        if args.scheduled and prior_day == today:
            return {'outcome': 'already_checked', 'notify': False, 'reason': 'Scheduled check already completed today in your timezone.'}
        collect(source if creator else root / 'no-identified-history', state, account, now, creator)
        if not creator:
            state['active'] = []
            state['samples'] = []
        if state.get('cleared_at'):
            state['active'] = [t for t in state['active'] if t > state['cleared_at']]
            state['samples'] = [s for s in state['samples'] if s[2] > state['cleared_at']]
        for w in windows(raw):
            state.setdefault('samples', []).append([w['id'], w['renewal'], now, w['used']])
        result = evaluate(raw, state, now, zone, args.working_now)
        result['collection'] = state['collection']
        urgent = result.get('selected_expiry', now + 2*DAY) - now <= DAY
        episode = [result['outcome'], result.get('_credit_id'), urgent, [w['renewal'] for w in result['windows']]]
        result['notify'] = result['outcome'] == 'use_now' and episode != state.get('last_alert') and now >= state.get('snooze_until', 0)
        previous = (state.get('last_result') or {}).get('outcome')
        result['health_change'] = previous is not None and ((previous == 'needs_information') != (result['outcome'] == 'needs_information'))
        if result['notify']:
            state['last_alert'] = episode
        result.pop('_credit_id', None)
        state['last_result'] = result
        if args.scheduled:
            state['last_scheduled'] = now
        save(path, state)
        save(root / 'index.json', {'current': key})
        return result


def main():
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('check', 'status', 'snooze', 'clear-profile'))
    parser.add_argument('--state-dir', default=str(home / 'usage-reset-state'))
    parser.add_argument('--sessions-dir', default=str(home / 'sessions'))
    parser.add_argument('--timezone', default='UTC')
    parser.add_argument('--scheduled', action='store_true')
    parser.add_argument('--working-now', action='store_true')
    parser.add_argument('--hours', type=float, default=24)
    args = parser.parse_args()
    if not finite(args.hours, 0, 24*30):
        parser.error('--hours must be between 0 and 720')
    try:
        print(json.dumps(command(args), separators=(',', ':')))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'outcome': 'needs_information', 'notify': False, 'reason': f'Cannot complete check: {type(exc).__name__}. Validate source data and local access.'}))
        sys.exit(1)


if __name__ == '__main__':
    main()
