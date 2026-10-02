#!/usr/bin/env python3
"""Read-only, metadata-only AI usage collection. Python 3.10+, no network calls."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import csv
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import zipfile
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TOKEN_FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
                'output_tokens', 'reasoning_output_tokens', 'total_tokens')
COUNT_FIELDS = ('requests', 'user_messages', 'assistant_messages', 'code_tracking_events')
METRICS = TOKEN_FIELDS + COUNT_FIELDS
KNOWN_APPS = ('Codex', 'Claude Code', 'ChatGPT', 'Claude', 'Cursor')


def parse_time(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        if isinstance(value, (int, float)) or re.fullmatch(r'\d+(?:\.\d+)?', str(value)):
            n = float(value)
            return (n / 1000 if n > 100_000_000_000 else n) if math.isfinite(n) else None
        d = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return d.timestamp() if d.tzinfo is not None else None
    except (ValueError, TypeError, OverflowError):
        return None


def iso(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace('+00:00', 'Z')


def number(value):
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        raise ValueError('boolean metric')
    n = float(str(value).replace(',', ''))
    if not math.isfinite(n) or n < 0 or not n.is_integer():
        raise ValueError('invalid metric')
    return int(n)


def vector(value, missing_zero=False):
    return {k: number(value.get(k, 0 if missing_zero else None)) for k in TOKEN_FIELDS}


def valid_vector(v):
    i, o, t = v.get('input_tokens'), v.get('output_tokens'), v.get('total_tokens')
    if all(x is not None for x in (i, o, t)) and i + o != t:
        return False
    caches = [v.get('cached_input_tokens'), v.get('cache_write_input_tokens')]
    if i is not None and sum(x or 0 for x in caches) > i:
        return False
    r = v.get('reasoning_output_tokens')
    return not (o is not None and r is not None and r > o)


def signature(v):
    return tuple(v.get(k) or 0 for k in TOKEN_FIELDS)


def readonly_db(path):
    return sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)


def json_lines(path, diagnostics, types=None):
    pattern = re.compile(r'"type"\s*:\s*"(?:' + '|'.join(re.escape(t) for t in types) + ')"') if types else None
    try:
        with Path(path).open(encoding='utf-8', errors='replace') as handle:
            for line in handle:
                if not line.strip():
                    continue
                if pattern and not pattern.search(line):
                    continue
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        yield data
                except (ValueError, TypeError):
                    diagnostics['invalid_json_records'] += 1
    except OSError:
        diagnostics['unreadable_files'] += 1


def json_documents(path, prefix=None):
    """Read JSON members without extraction; never follow ZIP paths."""
    path = Path(path)
    if path.is_dir():
        files = sorted(path.rglob('*.json'))
        if prefix:
            files = [p for p in files if p.name.startswith(prefix)]
        for file in files:
            yield json.loads(file.read_text(encoding='utf-8'))
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for item in archive.infolist():
                name = Path(item.filename).name
                if name.endswith('.json') and (not prefix or name.startswith(prefix)):
                    yield json.loads(archive.read(item).decode('utf-8'))
    else:
        yield json.loads(path.read_text(encoding='utf-8'))


class Collector:
    def __init__(self, start, end, tz, excluded=()):
        self.start, self.end, self.tz = start, end, tz
        self.excluded = set(excluded)
        self.events, self.seen, self.coverage = [], set(), []

    def in_window(self, at):
        return at is not None and math.isfinite(at) and self.start <= at < self.end

    def day(self, at):
        return datetime.fromtimestamp(at, self.tz).date().isoformat()

    def add(self, event, event_id, at=None, day=None):
        if event.get('session') in self.excluded:
            return False
        if day is None and not self.in_window(at):
            return False
        if not valid_vector(event):
            raise ValueError('contradictory token vector')
        key = (event['app'], str(event_id))
        if key in self.seen:
            return False
        self.seen.add(key)
        clean = {k: event[k] for k in METRICS if event.get(k) is not None}
        for k in ('app', 'model', 'category', 'surface', 'session', 'source', 'cost_usd',
                  'cost_basis', 'requests_lower_bound'):
            if k in event:
                clean[k] = event[k]
        clean['day'] = day or self.day(at)
        self.events.append(clean)
        return True

    def covered(self, app, source, status, metrics, notes, diagnostics=None, latest=None):
        row = dict(app=app, source=source, status=status, metrics=metrics, notes=notes)
        if diagnostics:
            row['diagnostics'] = dict(diagnostics)
        if latest is not None:
            row['latest_observed_timestamp_utc'] = iso(latest)
        self.coverage.append(row)


def codex_category(row):
    source, kind = str(row.get('source') or ''), row.get('thread_source')
    if row.get('model') == 'codex-auto-review' or kind == 'guardian_review' or 'guardian' in source:
        return 'approval review'
    if kind == 'automation':
        return 'automation'
    if kind == 'realtime_voice':
        return 'voice'
    if kind == 'subagent' or source.startswith('{'):
        return 'subagent'
    return 'noninteractive CLI' if source == 'exec' else 'user-directed'


def codex_surface(row):
    source = str(row.get('source') or '')
    if 'guardian' in source:
        return 'approval review'
    if source.startswith('{'):
        return 'subagent'
    return {'vscode': 'desktop / editor', 'exec': 'noninteractive CLI', 'cli': 'interactive CLI'}.get(source, 'unknown')


def collect_codex(c, root):
    root, diag = Path(root), Counter()
    rows, indexed, recovery = {}, set(), {}
    index_available = False
    databases = sorted(root.glob('state_*.sqlite'), key=lambda p: int(re.search(r'_(\d+)', p.name)[1]), reverse=True)
    for database in databases:
        try:
            with readonly_db(database) as db:
                db.row_factory = sqlite3.Row
                columns = {r[1] for r in db.execute('PRAGMA table_info(threads)')}
                if not {'id', 'rollout_path', 'created_at', 'updated_at'} <= columns:
                    continue
                selected = ['id', 'rollout_path', 'created_at', 'updated_at'] + [k for k in ('source', 'thread_source', 'model') if k in columns]
                for r in db.execute('SELECT ' + ','.join(selected) + ' FROM threads'):
                    p = str(Path(r['rollout_path']).resolve())
                    indexed.add(p)
                    if r['updated_at'] >= c.start and r['created_at'] < c.end:
                        rows[p] = dict(r)
            index_available = True
            diag['indexed_candidate_threads'] = len(rows)
            break
        except (sqlite3.Error, OSError, ValueError):
            diag['index_read_errors'] += 1
    for directory in ('sessions', 'archived_sessions'):
        for file in (root / directory).rglob('*.jsonl'):
            p = str(file.resolve())
            if p not in indexed:
                match = re.search(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', file.name)
                rows[p] = dict(id=match[0] if match else file.stem, created_at=0, updated_at=0)
                diag['unindexed_files'] += 1
    latest = None
    for path, row in rows.items():
        if row['id'] in c.excluded:
            diag['excluded_sessions'] += 1
            continue
        if not Path(path).exists():
            diag['missing_files'] += 1
            continue
        diag['files_scanned'] += 1
        session, model, turn = row['id'], row.get('model') or 'unknown', None
        meta_at, parent, previous = row['created_at'], None, None
        direct_usage, direct_cumulative, legacy = {}, {}, []
        own_max, own_previous, own_decreased, baseline = None, None, False, False
        base = dict(app='Codex', session=session, category=codex_category(row), surface=codex_surface(row), source='local histories')
        for record in json_lines(path, diag, ('session_meta', 'turn_context', 'token_usage_record', 'token_count')):
            typ, p, at = record.get('type'), record.get('payload') or {}, parse_time(record.get('timestamp'))
            if typ == 'session_meta':
                if p.get('id') and p['id'] != session:
                    continue
                meta_at = meta_at or parse_time(p.get('timestamp')) or at or 0
                parent = p.get('parent_thread_id') or p.get('forked_from_id')
                if 'source' not in row:
                    row['source'] = p.get('source') if isinstance(p.get('source'), str) else json.dumps(p.get('source', ''))
                    row['thread_source'] = p.get('thread_source')
                    base.update(category=codex_category(row), surface=codex_surface(row))
                continue
            if typ == 'turn_context':
                model, turn = p.get('model') or model, p.get('turn_id') or turn
                continue
            eligible = c.in_window(at) and (at >= meta_at - 1 if meta_at else True)
            if typ == 'token_usage_record':
                try:
                    u = vector(p.get('usage') or {}, True)
                except ValueError:
                    diag['invalid_usage_records'] += 1
                    continue
                own = not p.get('thread_id') or p['thread_id'] == session
                direct_usage[(p.get('turn_id') or turn, signature(u))] = u
                for cumulative in (p.get('thread_token_usage'), p.get('turn_token_usage')):
                    if cumulative:
                        direct_cumulative[(p.get('turn_id') or turn, signature(cumulative))] = u
                if not own:
                    if eligible:
                        diag['copied_records_excluded'] += 1
                    continue
                cumulative = p.get('thread_token_usage')
                if cumulative:
                    try:
                        cur = vector(cumulative, True)
                    except ValueError:
                        diag['invalid_usage_records'] += 1
                        continue
                    own_decreased |= own_previous is not None and cur['total_tokens'] < own_previous
                    own_previous = cur['total_tokens']
                    if own_max is None or cur['total_tokens'] > own_max['total_tokens']:
                        own_max = cur
                if not eligible or not u['total_tokens']:
                    continue
                event_id = p.get('response_id') or f'{session}:{at}:{signature(u)}'
                try:
                    if c.add(dict(base, model=model, requests=1, **u), event_id, at):
                        diag['per_response_records'] += 1
                    else:
                        diag['duplicate_response_records'] += 1
                except ValueError:
                    diag['invalid_usage_records'] += 1
                latest = max(latest or at, at)
                continue
            if p.get('type') != 'token_count':
                continue
            info = p.get('info') or {}
            current, last = info.get('total_token_usage'), info.get('last_token_usage')
            if not current:
                if eligible:
                    diag['records_without_usage'] += 1
                continue
            try:
                cur, last = vector(current, True), vector(last or {}, True)
            except ValueError:
                diag['invalid_usage_records'] += 1
                continue
            if previous and cur['total_tokens'] == previous['total_tokens']:
                previous = cur
                continue
            reset = previous and cur['total_tokens'] < previous['total_tokens']
            inherited_first = not previous and parent and cur['total_tokens'] > last['total_tokens']
            u = {k: last[k] if reset or inherited_first else cur[k] - (previous[k] if previous else 0) for k in TOKEN_FIELDS}
            for k in TOKEN_FIELDS:
                if u[k] < 0:
                    u[k] = last[k]
                    if eligible:
                        diag['negative_component_fallbacks'] += 1
            previous = cur
            if eligible:
                if reset:
                    diag['counter_resets'] += 1
                legacy.append((at, model, turn, u, cur, last))
        for at, model, turn, u, cur, last in legacy:
            matched = direct_usage.get((turn, signature(last))) or direct_cumulative.get((turn, signature(cur)))
            if matched:
                diag['redundant_counter_records_excluded'] += 1
                if signature(matched) != signature(u):
                    diag['redundant_counter_disagreements'] += 1
                continue
            if not last['total_tokens'] or not valid_vector(last):
                baseline = True
                diag['baseline_snapshots_excluded'] += 1
                continue
            if not u['total_tokens']:
                continue
            try:
                if c.add(dict(base, model=model, requests=1, **u), f'counter:{session}:{at}:{signature(cur)}:{signature(last)}', at):
                    diag['cumulative_delta_records'] += 1
            except ValueError:
                diag['invalid_usage_records'] += 1
            latest = max(latest or at, at)
        if baseline and base['category'] == 'approval review' and own_max and not own_decreased and row.get('created_at', 0) >= c.start and row.get('updated_at', c.end) < c.end:
            old = recovery.get(session)
            if old is None or own_max['total_tokens'] > old[0]['total_tokens']:
                recovery[session] = (own_max, row, dict(base, model=row.get('model') or model))
        elif baseline:
            diag['unrecoverable_baseline_sessions'] += 1
    observed = defaultdict(Counter)
    for e in c.events:
        if e['app'] == 'Codex':
            for k in TOKEN_FIELDS:
                observed[e.get('session')][k] += e.get(k) or 0
    for session, (maximum, row, base) in recovery.items():
        u = {k: maximum[k] - observed[session][k] for k in TOKEN_FIELDS}
        if any(n < 0 for n in u.values()) or not valid_vector(u):
            diag['unrecoverable_baseline_sessions'] += 1
            continue
        if u['total_tokens']:
            start_day, end_day = c.day(row['created_at']), c.day(row['updated_at'])
            allocation = start_day if start_day == end_day else 'Unallocated'
            c.add(dict(base, requests=0, requests_lower_bound=True, **u), 'recovery:' + session, day=allocation)
            diag['recovered_sessions'] += 1
            diag['recovered_tokens'] += u['total_tokens']
            if allocation == 'Unallocated':
                diag['unallocated_recovered_tokens'] += u['total_tokens']
    partial = any(diag[k] for k in ('missing_files', 'unreadable_files', 'invalid_json_records', 'invalid_usage_records', 'unrecoverable_baseline_sessions'))
    status = 'partial' if partial else 'measured local records' if rows or index_available else 'not found'
    notes = ['Canonical responses and unmatched cumulative deltas; includes subagents, automations and approval reviews.', 'Local coverage excludes unlogged requests and other devices; billed cost is unavailable.']
    if diag['recovered_sessions']:
        notes.append('Shortened approval histories recovered from canonical cumulative usage; request counts are minimums. Multi-day recovery is unallocated.')
    if not rows and not index_available:
        notes.append('No supported local histories were found. This does not establish zero use.')
    c.covered('Codex', 'local histories', status, ['tokens', 'model requests', 'logged sessions'], notes, diag, latest)


def collect_claude_code(c, root, home):
    root, diag, requests = Path(root), Counter(), {}
    files = sorted((root / 'projects').rglob('*.jsonl'))
    desktop, cli = set(), set()
    appdata = Path(os.environ.get('APPDATA', Path(home) / 'AppData/Roaming'))
    desktop_roots = [Path(home) / 'Library/Application Support/Claude/claude-code-sessions', appdata / 'Claude/claude-code-sessions']
    for directory in desktop_roots:
        for file in directory.glob('*/*/local_*.json'):
            try:
                d = json.loads(file.read_text())
                if d.get('cliSessionId'):
                    desktop.add(d['cliSessionId'])
            except (OSError, ValueError):
                pass
    if (root / 'history.jsonl').exists():
        for r in json_lines(root / 'history.jsonl', Counter()):
            if r.get('sessionId'):
                cli.add(r['sessionId'])
    latest = None
    for file in files:
        diag['files_scanned'] += 1
        for r in json_lines(file, diag, ('assistant',)):
            if r.get('type') != 'assistant':
                continue
            message = r.get('message') or {}
            usage = message.get('usage')
            if not isinstance(usage, dict):
                continue
            at = parse_time(r.get('timestamp'))
            if at is None:
                diag['invalid_usage_timestamps'] += 1
                continue
            if not c.in_window(at):
                continue
            session = r.get('sessionId') or file.stem
            if session in c.excluded:
                continue
            diag['assistant_usage_records'] += 1
            mid = message.get('id') or r.get('uuid')
            if not mid:
                diag['missing_message_identity'] += 1
                continue
            key = str(r.get('requestId') or 'no-request') + ':' + str(mid)
            model = message.get('model') or 'unknown'
            category = 'subagent / sidechain' if r.get('isSidechain') or 'subagents' in file.parts else 'primary'
            surface = 'desktop' if session in desktop else 'interactive CLI' if session in cli else 'unlinked CLI/SDK'
            value = requests.setdefault(key, dict(app='Claude Code', model=model, session=session, category=category, surface=surface, source='local histories', requests=1, at=at, uncached=0, cached_input_tokens=0, cache_write_input_tokens=0, output_tokens=0, reasoning_output_tokens=0))
            value['at'] = min(value['at'], at)
            try:
                components = {}
                for dest, src in [('uncached', 'input_tokens'), ('cached_input_tokens', 'cache_read_input_tokens'), ('cache_write_input_tokens', 'cache_creation_input_tokens'), ('output_tokens', 'output_tokens')]:
                    components[dest] = number(usage.get(src, 0)) or 0
                components['reasoning_output_tokens'] = number((usage.get('output_tokens_details') or {}).get('thinking_tokens', 0)) or 0
                for key_component, component in components.items():
                    value[key_component] = max(value[key_component], component)
            except ValueError:
                diag['invalid_usage_records'] += 1
            latest = max(latest or at, at)
    for key, value in requests.items():
        value['input_tokens'] = value.pop('uncached') + value['cached_input_tokens'] + value['cache_write_input_tokens']
        value['total_tokens'] = value['input_tokens'] + value['output_tokens']
        if value['model'] == '<synthetic>' or value['total_tokens'] == 0:
            diag['synthetic_or_zero_requests_excluded'] += 1
            continue
        try:
            c.add(value, key, value.pop('at'))
        except ValueError:
            diag['invalid_usage_records'] += 1
    diag['duplicate_usage_records_collapsed'] = diag['assistant_usage_records'] - len(requests)
    partial = any(diag[k] for k in ('unreadable_files', 'invalid_json_records', 'invalid_usage_records', 'invalid_usage_timestamps', 'missing_message_identity'))
    c.covered('Claude Code', 'local histories', 'partial' if partial else 'measured local records' if files else 'not found', ['tokens', 'model requests', 'logged sessions'], ['Counts include desktop, CLI/SDK and sidechains; ordinary Claude chat and other devices are outside this source.', 'Billed cost is not available from these token histories.'], diag, latest)


def collect_chatgpt_catalog(c, root):
    file, diag, latest = Path(root) / 'sqlite/codex-dev.db', Counter(), None
    if not file.exists():
        c.covered('ChatGPT', 'local conversation catalog', 'export needed', [], ['Supply a ChatGPT export for retained message and conversation counts. Tokens and spend require an authoritative usage source.'])
        return
    try:
        with readonly_db(file) as db:
            db.row_factory = sqlite3.Row
            columns = {r[1] for r in db.execute('PRAGMA table_info(local_thread_catalog)')}
            kind = 'source_kind' if 'source_kind' in columns else 'host_kind'
            fields = {'thread_id', 'source_created_at', 'source_updated_at'}
            if not fields <= columns or kind not in columns:
                raise ValueError('unsupported catalog')
            where = f"{kind}='chatgpt'" + (' AND missing_candidate=0' if 'missing_candidate' in columns else '')
            for r in db.execute('SELECT thread_id,source_created_at,source_updated_at FROM local_thread_catalog WHERE ' + where):
                created, updated = parse_time(r['source_created_at']), parse_time(r['source_updated_at'])
                if updated is not None:
                    latest = max(latest or updated, updated)
                if c.in_window(created):
                    c.add(dict(app='ChatGPT', session=r['thread_id'], category='catalog new conversation', source='partial local catalog'), 'catalog-new:' + r['thread_id'], created)
                    diag['new_conversations'] += 1
                if c.in_window(updated):
                    diag['conversations_with_last_update_in_window'] += 1
        c.covered('ChatGPT', 'local conversation catalog', 'partial activity only', ['new catalog conversations'], ['Partial catalog, not a message ledger. Last-update dates cannot reconstruct all activity; no token, request, model or cost totals.'], diag, latest)
    except (sqlite3.Error, ValueError, OSError):
        c.covered('ChatGPT', 'local conversation catalog', 'unsupported or unreadable', [], ['Supply an account export; no usage totals inferred from this catalog.'])


def collect_cursor_tracking(c, home):
    file = Path(home) / '.cursor/ai-tracking/ai-code-tracking.db'
    if not file.exists():
        c.covered('Cursor', 'local code tracking', 'export needed', [], ['Supply a personal usage CSV for token/request/cost data.'])
        return
    diag, latest = Counter(), None
    try:
        with readonly_db(file) as db:
            for identity, timestamp in db.execute('SELECT hash,timestamp FROM ai_code_hashes'):
                at = parse_time(timestamp)
                if at is not None:
                    latest = max(latest or at, at)
                if c.in_window(at):
                    c.add(dict(app='Cursor', code_tracking_events=1, category='code tracking', source='local code tracking'), 'tracking:' + identity, at)
                    diag['events_in_window'] += 1
        c.covered('Cursor', 'local code tracking', 'stale activity source' if latest is not None and latest < c.start else 'partial activity only', ['code tracking events'], ['Code tracking is not a complete token/request/billing ledger. Zero observed events does not establish zero use.'], diag, latest)
    except (sqlite3.Error, ValueError, OSError):
        c.covered('Cursor', 'local code tracking', 'unsupported or unreadable', [], ['Supply a personal usage CSV; no token or spend totals inferred.'])


def import_chats(c, path, kind):
    app, diag, latest = ('ChatGPT' if kind == 'chatgpt' else 'Claude'), Counter(), None
    documents = list(json_documents(path, prefix='conversations'))
    for doc in documents:
        conversations = doc if isinstance(doc, list) else doc.get('conversations', [doc]) if isinstance(doc, dict) else []
        for conv in conversations:
            if not isinstance(conv, dict):
                continue
            session = conv.get('id') or conv.get('uuid') or conv.get('conversation_id')
            if not session:
                diag['conversations_without_identity'] += 1
                continue
            if kind == 'chatgpt':
                mapping = conv.get('mapping')
                if not isinstance(mapping, dict):
                    diag['unsupported_conversation_records'] += 1
                    continue
                messages = [node.get('message') for node in mapping.values() if isinstance(node, dict)]
            else:
                messages = conv.get('chat_messages')
                if not isinstance(messages, list):
                    diag['unsupported_conversation_records'] += 1
                    continue
            for m in messages:
                if not isinstance(m, dict):
                    continue
                role = (m.get('author') or {}).get('role') if kind == 'chatgpt' else m.get('sender')
                role = {'human': 'user'}.get(role, role)
                if role not in ('user', 'assistant'):
                    continue
                at = parse_time(m.get('create_time') if kind == 'chatgpt' else m.get('created_at'))
                if at is None:
                    diag['messages_without_timestamp'] += 1
                    continue
                if not c.in_window(at):
                    continue
                identity = m.get('id') or m.get('uuid')
                if not identity:
                    diag['messages_without_identity'] += 1
                    continue
                metadata = m.get('metadata') or {}
                model = metadata.get('model_slug') or m.get('model') or 'unknown'
                event = dict(app=app, session=session, model=model, category='retained chat', source='account export', **{role + '_messages': 1})
                if c.add(event, 'message:' + str(identity), at):
                    diag[role + '_messages'] += 1
                else:
                    diag['duplicate_messages_excluded'] += 1
                latest = max(latest or at, at)
            diag['conversations_scanned'] += 1
    status = 'partial retained chats' if diag['messages_without_timestamp'] or diag['messages_without_identity'] or diag['unsupported_conversation_records'] else 'measured retained chats'
    if not diag['conversations_scanned']:
        status = 'unsupported export'
    c.covered(app, 'account export', status, ['user messages', 'assistant messages', 'active retained conversations'], ['Only retained, timestamped exported messages. Regenerated ChatGPT branches are included once per message ID. Deleted or unexported chats remain outside coverage.', 'Tokens, model requests and cost are unavailable; message-level model attribution is shown only where recorded.'], diag, latest)


def column_name(value):
    return re.sub(r'[^a-z0-9]', '', str(value).lower())


def import_cursor(c, path, input_mode):
    diag, latest = Counter(), None
    aliases = {
        'date': 'timestamp', 'timestamp': 'timestamp', 'time': 'timestamp',
        'model': 'model', 'requestid': 'id', 'id': 'id',
        'inputtokens': 'input_tokens', 'cachedinputtokens': 'cached_input_tokens',
        'cachereadtokens': 'cached_input_tokens', 'cachewritetokens': 'cache_write_input_tokens',
        'cachecreationtokens': 'cache_write_input_tokens', 'outputtokens': 'output_tokens',
        'totaltokens': 'total_tokens', 'cost': 'cost_usd', 'costusd': 'cost_usd',
        'inputtokenswcachewrite': 'inclusive_write_input',
        'inputtokenswocachewrite': 'uncached_input',
    }
    with Path(path).open(encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        mapped = {h: aliases.get(column_name(h)) for h in reader.fieldnames or []}
        values = set(mapped.values())
        if 'timestamp' not in values or not values.intersection({'total_tokens', 'input_tokens', 'output_tokens', 'inclusive_write_input', 'cost_usd'}):
            c.covered('Cursor', 'usage CSV', 'unsupported CSV schema', [], ['This is not a recognized per-event usage export. Normalize documented fields into the generic import schema.'])
            return
        for raw in reader:
            r = {dest: raw[src] for src, dest in mapped.items() if dest is not None}
            at = parse_time(r.get('timestamp'))
            if at is None:
                diag['invalid_timestamps'] += 1
                continue
            if not c.in_window(at):
                continue
            event = dict(app='Cursor', model=r.get('model') or 'unknown', source='usage CSV', category='usage event', requests=1)
            try:
                v = vector(r)
                if r.get('inclusive_write_input') not in (None, ''):
                    base, uncached = number(r['inclusive_write_input']), number(r.get('uncached_input'))
                    cached = v['cached_input_tokens']
                    v['input_tokens'] = base + cached if cached is not None else None
                    if uncached is not None:
                        v['cache_write_input_tokens'] = base - uncached
                        if v['cache_write_input_tokens'] < 0:
                            raise ValueError('contradictory input columns')
                elif v['input_tokens'] is not None and input_mode == 'uncached':
                    if v['cached_input_tokens'] is None or v['cache_write_input_tokens'] is None:
                        v['input_tokens'] = None
                        diag['incomplete_input_components'] += 1
                    else:
                        v['input_tokens'] += v['cached_input_tokens'] + v['cache_write_input_tokens']
                elif v['input_tokens'] is not None and input_mode == 'auto':
                    v['input_tokens'] = None
                    diag['ambiguous_input_components'] += 1
                if v['total_tokens'] is None and v['input_tokens'] is not None and v['output_tokens'] is not None:
                    v['total_tokens'] = v['input_tokens'] + v['output_tokens']
                event.update(v)
                cost = str(r.get('cost_usd', '')).strip().replace('$', '').replace(',', '')
                try:
                    amount = Decimal(cost)
                    if amount.is_finite() and amount >= 0:
                        event.update(cost_usd=str(amount), cost_basis='dashboard_usage')
                except InvalidOperation:
                    pass
                identity = r.get('id') or hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
                if not r.get('id'):
                    event['requests_lower_bound'] = True
                    diag['rows_without_request_identity'] += 1
                if c.add(event, identity, at):
                    diag['accepted_usage_rows'] += 1
                else:
                    diag['duplicate_rows_excluded'] += 1
                latest = max(latest or at, at)
            except (ValueError, TypeError):
                diag['invalid_usage_rows'] += 1
    c.covered('Cursor', 'usage CSV', 'partial usage export' if diag['invalid_usage_rows'] or diag['invalid_timestamps'] or diag['ambiguous_input_components'] or diag['incomplete_input_components'] else 'measured usage export', ['model requests', 'recorded token fields', 'dashboard usage values'], ['Numeric CSV Cost is a dashboard usage value, not an inferred invoice amount. Included/free labels remain unknown.', 'Generic input-token semantics need --cursor-input-mode; ambiguous components are omitted. Exact Total Tokens, when present, is retained.', 'Rows without request IDs deduplicate identical metadata; indistinguishable events make request counts minimums.'], diag, latest)


def import_generic(c, path):
    diag, labels = Counter(), set()
    if Path(path).suffix.lower() == '.jsonl':
        records = json_lines(path, diag)
    else:
        docs = list(json_documents(path))
        records = [r for doc in docs for r in (doc if isinstance(doc, list) else doc.get('records', []))]
    for r in records:
        if not isinstance(r, dict) or not isinstance(r.get('app'), str) or not r.get('id'):
            diag['invalid_identity_records'] += 1
            continue
        labels.add(r['app'])
        at, day = parse_time(r.get('timestamp')), None
        if 'period_start' in r or 'period_end' in r:
            lo, hi = parse_time(r.get('period_start')), parse_time(r.get('period_end'))
            if lo is None or hi is None or hi <= lo:
                diag['invalid_period_records'] += 1
                continue
            if hi <= c.start or lo >= c.end:
                continue
            if lo < c.start or hi > c.end:
                diag['boundary_crossing_buckets_excluded'] += 1
                continue
            at = lo
            day = c.day(lo) if c.day(lo) == c.day(hi - 0.001) else 'Unallocated'
        elif at is None:
            diag['invalid_timestamps'] += 1
            continue
        elif not c.in_window(at):
            continue
        try:
            event = dict(app=r['app'], model=r.get('model') or 'unknown', source='normalized import')
            for k in ('session', 'category', 'surface', 'requests_lower_bound'):
                if k in r:
                    event[k] = r[k]
            for k in METRICS:
                if r.get(k) is not None:
                    event[k] = number(r[k])
            if event.get('total_tokens') is None and event.get('input_tokens') is not None and event.get('output_tokens') is not None:
                event['total_tokens'] = event['input_tokens'] + event['output_tokens']
            if r.get('cost_usd') is not None:
                basis, amount = r.get('cost_basis'), Decimal(str(r['cost_usd']))
                if basis not in ('billed', 'dashboard_usage', 'estimate') or not amount.is_finite() or amount < 0:
                    raise ValueError('invalid cost basis')
                event.update(cost_usd=str(amount), cost_basis=basis)
            if c.add(event, r['id'], at, day):
                diag['accepted_records'] += 1
            else:
                diag['duplicate_records_excluded'] += 1
        except (ValueError, TypeError, InvalidOperation):
            diag['invalid_usage_records'] += 1
    bad = any(v for k, v in diag.items() if k.startswith('invalid') or k.startswith('boundary') or k == 'unreadable_files')
    for label in labels or {'Other AI'}:
        c.covered(label, 'normalized import', 'partial import' if bad else 'measured imported records', ['supplied fields only'], ['Source labels and scope must be checked against the original export. Avoid overlap with local or account usage sources.', 'Aggregate buckets crossing reporting boundaries are excluded; multi-day buckets are unallocated.'], diag)


def aggregate(events):
    out = {'records': len(events)}
    for k in METRICS:
        known = [e[k] for e in events if k in e]
        out[k] = sum(known) if known else None
        out[k + '_known_records'] = len(known)
    out['logged_sessions'] = len({(e['app'], e['session']) for e in events if e.get('session')})
    out['chat_conversations'] = len({(e['app'], e['session']) for e in events if e.get('session') and ('user_messages' in e or 'assistant_messages' in e)})
    out['catalog_new_conversations'] = len({e['session'] for e in events if e.get('category') == 'catalog new conversation'})
    out['requests_is_lower_bound'] = any(e.get('requests_lower_bound') for e in events)
    bases = defaultdict(list)
    for e in events:
        if e.get('cost_usd') is not None:
            bases[e['cost_basis']].append(Decimal(e['cost_usd']))
    out['costs_usd'] = {k: {'amount': str(sum(v, Decimal(0))), 'known_records': len(v)} for k, v in bases.items()}
    token_events = [e for e in events if e.get('total_tokens') is not None]
    inputs = [e for e in token_events if e.get('input_tokens') is not None]
    complete_input = bool(inputs) and len(inputs) == len(token_events) and all(e.get('cached_input_tokens') is not None and e.get('cache_write_input_tokens') is not None for e in inputs)
    out['input_composition_complete_for_measured_tokens'] = complete_input
    out['uncached_input_tokens'] = sum(e['input_tokens'] - e['cached_input_tokens'] - e['cache_write_input_tokens'] for e in inputs) if complete_input else None
    out['cache_read_share_of_input'] = out['cached_input_tokens'] / out['input_tokens'] if complete_input and out['input_tokens'] else None
    return out


def grouped(events, field):
    groups = defaultdict(list)
    for event in events:
        groups[str(event.get(field) or 'unknown')].append(event)
    return {k: aggregate(v) for k, v in sorted(groups.items(), key=lambda x: -(aggregate(x[1])['total_tokens'] or 0))}


def make_report(c, name):
    total = aggregate(c.events)
    groups = {field: grouped(c.events, field) for field in ('app', 'model', 'day', 'category', 'surface')}
    zero_fields = set()
    for coverage in c.coverage:
        app = coverage['app']
        if coverage['status'] == 'measured local records' and app not in groups['app']:
            empty = aggregate([])
            for metric in TOKEN_FIELDS + ('requests',):
                empty[metric] = 0
                zero_fields.add(metric)
            groups['app'][app] = empty
    for metric in zero_fields:
        if total[metric] is None:
            total[metric] = 0
    for field, group in groups.items():
        for metric in METRICS:
            known = [v[metric] for v in group.values() if v[metric] is not None]
            value = sum(known) if known else 0 if total[metric] == 0 else None
            assert value == total[metric], (field, metric)
        for basis, value in total['costs_usd'].items():
            amount = sum((Decimal(v['costs_usd'].get(basis, {}).get('amount', '0')) for v in group.values()), Decimal(0))
            assert amount == Decimal(value['amount'])
    return dict(schema_version=1, title=(name + ' — ' if name else '') + 'AI Usage Report',
                window=dict(start=iso(c.start), end_exclusive=iso(c.end), timezone=str(c.tz)),
                totals=total, by_app=groups['app'], by_model=groups['model'], by_day=dict(sorted(groups['day'].items())),
                by_category=groups['category'], by_surface=groups['surface'], coverage=c.coverage,
                validation=dict(all_breakdowns_reconcile=True, records_metadata_only=True),
                interpretation=['Totals are measured subtotals over known fields; unknown fields and uncovered apps remain outside those totals.',
                  'Processed tokens include reused cached context. Cache reads/writes are input subsets; reasoning is an output subset.',
                  'Model requests, retained user/assistant messages, conversations and code events are distinct units. Session counts do not measure hours.',
                  'Costs are separated by billed, dashboard usage value and estimate. Subscription fees are separate.',
                  'Only local histories or supplied imports are covered. No automatic account connection, publication or external sharing.'])


def fmt(n):
    return 'Unknown' if n is None else f'{n:,}'


def markdown_table(headers, rows):
    safe = lambda v: str(v).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join('| ' + ' | '.join(safe(v) for v in row) + ' |' for row in [headers, ['---'] * len(headers), *rows])


def report_markdown(r):
    t, w = r['totals'], r['window']
    lines = ['# ' + r['title'], f"{w['start']} to {w['end_exclusive']} (exclusive); daily timezone: {w['timezone']}.",
             f"Measured processed tokens: **{fmt(t['total_tokens'])}**. Observed model requests: **{fmt(t['requests'])}{' minimum' if t['requests_is_lower_bound'] else ''}**.",
             '## Totals', markdown_table(['Metric', 'Measured value', 'Records with known value'], [[k.replace('_', ' '), fmt(t[k]), t[k + '_known_records']] for k in METRICS]),
             f"Active retained chat conversations: {fmt(t['chat_conversations'])}; new conversations in partial catalogs: {fmt(t['catalog_new_conversations'])}; logged session IDs: {fmt(t['logged_sessions'])}."]
    if t['cache_read_share_of_input'] is not None:
        lines.append(f"{t['cache_read_share_of_input'] * 100:.1f}% of measured input tokens were cache reads. Uncached input: {fmt(t['uncached_input_tokens'])}.")
    headers = ['Group', 'Tokens', 'Model requests', 'User messages', 'Assistant messages']
    for field, title in [('by_app', 'By app'), ('by_model', 'By model'), ('by_day', 'By day'), ('by_category', 'By work type'), ('by_surface', 'By surface')]:
        rows = [[k, fmt(v['total_tokens']), fmt(v['requests']) + (' minimum' if v['requests_is_lower_bound'] else ''), fmt(v['user_messages']), fmt(v['assistant_messages'])] for k, v in r[field].items()]
        lines.extend(['## ' + title, markdown_table(headers, rows)])
    costs = [[basis, value['amount'], value['known_records']] for basis, value in t['costs_usd'].items()]
    lines.extend(['## Cost', markdown_table(['Basis', 'Measured USD subtotal', 'Records with known cost'], costs) if costs else 'Unknown: no authoritative numeric cost records were supplied.'])
    if costs:
        for field, title in [('by_app', 'Cost by app'), ('by_model', 'Cost by model'), ('by_day', 'Cost by day')]:
            rows = [[label, basis, value['amount'], value['known_records']] for label, group in r[field].items() for basis, value in group['costs_usd'].items()]
            lines.extend(['### ' + title, markdown_table(['Group', 'Basis', 'USD subtotal', 'Known records'], rows)])
    lines.append('## Coverage')
    for row in r['coverage']:
        lines.append('### ' + row['app'] + ' · ' + row['source'] + '\n\n' + row['status'] + '. ' + ' '.join(row['notes']))
        if row.get('latest_observed_timestamp_utc'):
            lines.append('Latest observed timestamp: ' + row['latest_observed_timestamp_utc'] + '.')
        if row.get('diagnostics'):
            lines.append('Collector diagnostics: ' + ', '.join(k.replace('_', ' ') + '=' + str(v) for k, v in row['diagnostics'].items()) + '.')
    lines.extend(['## Interpretation', '\n'.join('- ' + s for s in r['interpretation']), 'All app/model/day/work-type/surface breakdowns reconcile. No prompts, titles, source paths, credentials or session IDs are written into this report.'])
    return '\n\n'.join(lines) + '\n'


def report_html(r):
    esc = lambda value: html.escape(str(value))
    def table(headers, rows):
        return '<div class="scroll"><table><thead><tr>' + ''.join('<th>' + esc(v) + '</th>' for v in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + esc(v) + '</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table></div>'
    t, w, body = r['totals'], r['window'], []
    for key, title in [('by_app', 'By app'), ('by_model', 'By model'), ('by_day', 'By day'), ('by_category', 'By work type'), ('by_surface', 'By surface')]:
        rows = [[label, fmt(v['total_tokens']), fmt(v['requests']) + ('+' if v['requests_is_lower_bound'] else ''), fmt(v['user_messages']), fmt(v['assistant_messages'])] for label, v in r[key].items()]
        chart = ''
        if key in ('by_app', 'by_model'):
            maximum = max((v['total_tokens'] or 0 for v in r[key].values()), default=0)
            if maximum:
                chart = '<div class="chart">' + ''.join('<div class="bar"><span>' + esc(label) + '</span><div class="track"><div style="width:' + str((v['total_tokens'] or 0) / maximum * 100) + '%"></div></div><b>' + esc(fmt(v['total_tokens'])) + '</b></div>' for label, v in r[key].items() if v['total_tokens'] is not None) + '</div>'
        body.append('<section><h2>' + title + '</h2>' + chart + table(['Group', 'Tokens', 'Model requests', 'User messages', 'Assistant messages'], rows) + '</section>')
    body.append('<section><h2>Token composition & counts</h2>' + table(['Metric', 'Measured subtotal', 'Known records'], [[k.replace('_', ' '), fmt(t[k]), t[k + '_known_records']] for k in METRICS]) + '</section>')
    costs = [[k, v['amount'], v['known_records']] for k, v in t['costs_usd'].items()]
    cost_details = ''
    if costs:
        for field, title in [('by_app', 'By app'), ('by_model', 'By model'), ('by_day', 'By day')]:
            rows = [[label, basis, value['amount'], value['known_records']] for label, group in r[field].items() for basis, value in group['costs_usd'].items()]
            cost_details += '<h3>' + title + '</h3>' + table(['Group', 'Basis', 'USD subtotal', 'Known records'], rows)
    body.append('<section><h2>Cost</h2>' + (table(['Basis', 'Measured USD subtotal', 'Known records'], costs) + cost_details if costs else '<p>Unknown. No numeric cost records with a known basis were supplied.</p>') + '</section>')
    coverage = ''.join('<article><h3>' + esc(v['app'] + ' · ' + v['source']) + '</h3><p><strong>' + esc(v['status']) + '</strong></p><p>' + esc(' '.join(v['notes'])) + '</p>' + ('<p class="muted">Latest observed timestamp: ' + esc(v['latest_observed_timestamp_utc']) + '</p>' if v.get('latest_observed_timestamp_utc') else '') + '</article>' for v in r['coverage'])
    body.append('<section><h2>Coverage</h2>' + coverage + '<details><summary>Collector validation and diagnostics</summary>' + ''.join('<p>' + esc(v['app']) + ': ' + esc(json.dumps(v.get('diagnostics', {}), sort_keys=True)) + '</p>' for v in r['coverage']) + '</details></section>')
    body.append('<section><h2>How to read this report</h2><ul>' + ''.join('<li>' + esc(s) + '</li>' for s in r['interpretation']) + '</ul><p>All breakdowns reconcile.</p><p><a href="report.json">Full data (JSON)</a> · <a href="report.md">Markdown report</a> · <a href="daily.csv">Daily CSV</a></p></section>')
    cache = f"{t['cache_read_share_of_input'] * 100:.1f}% cache reads" if t['cache_read_share_of_input'] is not None else 'Cache share unknown'
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(r['title']) + '</title><style>body{margin:0;background:#f3f5fa;color:#192541;font:16px/1.6 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:36px 24px}h1{font:40px/1.15 Georgia,serif}h2{font-size:23px}h3{font-size:17px}a{color:#294aeb}section{padding:24px;background:white;border:1px solid #dce2ed;border-radius:8px;margin:22px 0}.muted{color:#62728b;font-size:14px}.metrics{display:flex;gap:16px;flex-wrap:wrap}.metric{background:#213ee6;color:white;flex:1;padding:22px;border-radius:8px;min-width:230px}.metric b{font-size:30px;display:block;overflow-wrap:anywhere}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #e4e9f2}td:not(:first-child){font-variant-numeric:tabular-nums}.bar{display:grid;grid-template-columns:minmax(120px,230px) 1fr 140px;gap:12px;align-items:center;margin:12px 0;font-size:14px}.bar span{overflow-wrap:anywhere}.bar b{text-align:right;font-variant-numeric:tabular-nums}.track{background:#eef1f8;height:14px}.track div{background:#294aeb;height:100%;min-width:2px}.chart{margin:20px 0}article{border-top:1px solid #e4e9f2;padding:14px 0}li{margin:10px 0}summary{cursor:pointer}details p{overflow-wrap:anywhere;font-size:14px}@media(max-width:650px){main{padding:24px 14px}section{padding:18px 14px}h1{font-size:32px}.bar{grid-template-columns:135px 1fr 88px;gap:8px;font-size:12px}.metric b{font-size:26px}}@media print{body{background:white}section{border:0;padding:12px 0}.metric{background:white;color:#192541;border:1px solid #dce2ed}}</style></head><body><main><p class="muted">Full usage report · ' + esc(w['timezone']) + '</p><h1>' + esc(r['title']) + '</h1><p class="muted">' + esc(w['start'] + ' to ' + w['end_exclusive'] + ' (exclusive)') + '</p><div class="metrics"><div class="metric">Measured processed tokens<b>' + esc(fmt(t['total_tokens'])) + '</b></div><div class="metric">Observed model requests<b>' + esc(fmt(t['requests'])) + ('+' if t['requests_is_lower_bound'] else '') + '</b></div></div><p>' + esc(cache) + ' · ' + str(t['chat_conversations']) + ' active retained chat conversations. Unknown fields remain outside measured subtotals.</p>' + ''.join(body) + '</main></body></html>'


def write_report(r, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'report.json').write_text(json.dumps(r, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (output / 'report.md').write_text(report_markdown(r), encoding='utf-8')
    (output / 'report.html').write_text(report_html(r), encoding='utf-8')
    with (output / 'daily.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['date'] + list(METRICS))
        for day, values in r['by_day'].items():
            writer.writerow([day] + [values[k] if values[k] is not None else '' for k in METRICS])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=float, default=7)
    parser.add_argument('--start', help='ISO timestamp with offset, or epoch')
    parser.add_argument('--end', help='Exclusive cutoff; defaults to now')
    parser.add_argument('--timezone', default='UTC', help='Daily timezone; default UTC')
    parser.add_argument('--name', default='', help='Optional report display name')
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--codex-root', type=Path)
    parser.add_argument('--claude-root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--import', dest='imports', action='append', default=[], metavar='KIND=PATH')
    parser.add_argument('--skip-local', action='store_true')
    parser.add_argument('--skip-app', action='append', default=[])
    parser.add_argument('--exclude-session', action='append', default=[])
    parser.add_argument('--expected-app', action='append', default=[])
    parser.add_argument('--cursor-input-mode', choices=['auto', 'inclusive', 'uncached'], default='auto')
    args = parser.parse_args(argv)
    try:
        tz = ZoneInfo(args.timezone)
    except ZoneInfoNotFoundError:
        parser.error('Named timezone data is unavailable. Use UTC or install Python tzdata.')
    end = parse_time(args.end) if args.end else datetime.now(timezone.utc).timestamp()
    start = parse_time(args.start) if args.start else end - args.days * 86400 if end is not None else None
    if start is None or end is None or not math.isfinite(start) or not math.isfinite(end) or start >= end:
        parser.error('Use valid offset-aware timestamps and an end later than start.')
    imports = []
    for spec in args.imports:
        kind, sep, path = spec.partition('=')
        if not sep or kind not in ('chatgpt', 'claude', 'cursor', 'generic') or not Path(path).exists():
            parser.error('Imports must be chatgpt, claude, cursor or generic plus an existing path.')
        imports.append((kind, Path(path)))
    c, skip = Collector(start, end, tz, args.exclude_session), set(args.skip_app)
    codex_root = args.codex_root or Path(os.environ.get('CODEX_HOME', args.home / '.codex'))
    claude_root = args.claude_root or Path(os.environ.get('CLAUDE_CONFIG_DIR', args.home / '.claude'))
    kinds = {kind for kind, _ in imports}
    if not args.skip_local:
        if 'Codex' not in skip:
            collect_codex(c, codex_root)
        if 'Claude Code' not in skip:
            collect_claude_code(c, claude_root, args.home)
        if 'ChatGPT' not in skip and 'chatgpt' not in kinds:
            collect_chatgpt_catalog(c, codex_root)
        if 'Cursor' not in skip and 'cursor' not in kinds:
            collect_cursor_tracking(c, args.home)
    if 'claude' not in kinds and 'Claude' not in skip:
        c.covered('Claude', 'account export', 'export needed', [], ['Ordinary Claude chat is separate from Claude Code. Supply a Claude account export for retained message counts.'])
    for kind, path in imports:
        try:
            if kind in ('chatgpt', 'claude'):
                import_chats(c, path, kind)
            elif kind == 'cursor':
                import_cursor(c, path, args.cursor_input_mode)
            else:
                import_generic(c, path)
        except (OSError, ValueError, TypeError, zipfile.BadZipFile, sqlite3.Error):
            c.covered({'chatgpt': 'ChatGPT', 'claude': 'Claude', 'cursor': 'Cursor', 'generic': 'Other AI'}[kind], kind + ' import', 'unreadable or unsupported import', [], ['The supplied source could not be parsed. Check its format; no usage was inferred.'])
    covered = {r['app'] for r in c.coverage}
    for app in args.expected_app:
        if app not in covered:
            c.covered(app, 'not configured', 'source needed', [], ['Provide a documented usage export, supported account connection or normalized import. This app is outside measured totals.'])
    report = make_report(c, args.name)
    write_report(report, args.output)
    print(json.dumps({'report_directory': str(args.output.resolve()), 'window': report['window'],
                      'measured_total_tokens': report['totals']['total_tokens'], 'observed_requests': report['totals']['requests'],
                      'requests_is_lower_bound': report['totals']['requests_is_lower_bound'],
                      'coverage': [{'app': r['app'], 'status': r['status']} for r in report['coverage']],
                      'all_breakdowns_reconcile': True}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
