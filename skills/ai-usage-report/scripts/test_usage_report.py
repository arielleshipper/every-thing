"""Behavioral regression fixtures. No external accounts or personal source data."""
import csv
from datetime import timezone
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location('usage_report', Path(__file__).with_name('usage_report.py'))
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)

START, END = '2026-01-05T00:00:00Z', '2026-01-12T00:00:00Z'
AT = '2026-01-06T12:00:00Z'


def usage(i, o=5, cached=0, writes=0, reasoning=0):
    return dict(input_tokens=i, cached_input_tokens=cached, cache_write_input_tokens=writes,
                output_tokens=o, reasoning_output_tokens=reasoning, total_tokens=i + o)


def record(typ, payload, at=AT):
    return dict(type=typ, payload=payload, timestamp=at)


class UsageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.c = u.Collector(u.parse_time(START), u.parse_time(END), timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def write_json(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return path

    def write_lines(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(''.join(json.dumps(r) + '\n' for r in data))
        return path

    def test_codex_canonical_response_beats_redundant_counter(self):
        sid = '11111111-1111-1111-1111-111111111111'
        token = usage(100, 10, 80)
        records = [record('session_meta', {'id': sid, 'timestamp': START}),
                   record('turn_context', {'turn_id': 'turn', 'model': 'test-model'}),
                   record('token_usage_record', {'thread_id': sid, 'turn_id': 'turn', 'response_id': 'r1', 'usage': token, 'thread_token_usage': token}),
                   record('event_msg', {'type': 'token_count', 'info': {'total_token_usage': token, 'last_token_usage': token}})]
        self.write_lines(f'codex/sessions/rollout-{sid}.jsonl', records + records[2:3])
        u.collect_codex(self.c, self.root / 'codex')
        r = u.make_report(self.c, '')
        self.assertEqual(r['totals']['total_tokens'], 110)
        self.assertEqual(r['totals']['requests'], 1)
        self.assertEqual(r['by_model']['test-model']['total_tokens'], 110)

    def test_codex_legacy_reset_and_fork_do_not_inherit_tokens(self):
        sid = '22222222-2222-2222-2222-222222222222'
        first, second = usage(100, 10), usage(20, 2)
        self.write_lines(f'codex/sessions/{sid}.jsonl', [
            record('session_meta', {'id': sid, 'timestamp': START, 'parent_thread_id': 'parent'}),
            record('event_msg', {'type': 'token_count', 'info': {'total_token_usage': usage(1000, 100), 'last_token_usage': first}}),
            record('event_msg', {'type': 'token_count', 'info': {'total_token_usage': second, 'last_token_usage': second}}, '2026-01-07T12:00:00Z')])
        u.collect_codex(self.c, self.root / 'codex')
        self.assertEqual(u.aggregate(self.c.events)['total_tokens'], 132)
        self.assertEqual(u.aggregate(self.c.events)['requests'], 2)

    def test_shortened_multiday_review_recovery_is_unallocated(self):
        root = self.root / 'codex'
        sid = '33333333-3333-3333-3333-333333333333'
        path = self.write_lines(f'codex/sessions/{sid}.jsonl', [
            record('session_meta', {'id': sid, 'timestamp': '2026-01-06T23:00:00Z'}),
            record('event_msg', {'type': 'token_count', 'info': {'total_token_usage': usage(90, 9), 'last_token_usage': usage(0, 0)}}, '2026-01-06T23:00:00Z'),
            record('token_usage_record', {'thread_id': sid, 'response_id': 'last', 'usage': usage(10, 1), 'thread_token_usage': usage(100, 10)}, '2026-01-07T01:00:00Z')])
        with sqlite3.connect(root / 'state_99.sqlite') as db:
            db.execute('CREATE TABLE threads(id,rollout_path,created_at,updated_at,source,thread_source,model)')
            db.execute('INSERT INTO threads VALUES(?,?,?,?,?,?,?)', (sid, str(path), u.parse_time('2026-01-06T23:00:00Z'), u.parse_time('2026-01-07T01:00:00Z'), 'guardian', 'guardian_review', 'codex-auto-review'))
        u.collect_codex(self.c, root)
        r = u.make_report(self.c, '')
        self.assertEqual(r['totals']['total_tokens'], 110)
        self.assertEqual(r['totals']['requests'], 1)
        self.assertTrue(r['totals']['requests_is_lower_bound'])
        self.assertEqual(r['by_day']['Unallocated']['total_tokens'], 99)

    def test_claude_streaming_copies_and_cache_components(self):
        msg = dict(type='assistant', timestamp=AT, sessionId='private-session', requestId='req',
                   message=dict(id='message', model='claude-test', content='PRIVATE PROMPT', usage=dict(input_tokens=10, cache_read_input_tokens=100, cache_creation_input_tokens=20, output_tokens=2)))
        later = json.loads(json.dumps(msg))
        later['message']['usage']['output_tokens'] = 5
        self.write_lines('claude/projects/project/subagents/transcript.jsonl', [msg, later])
        u.collect_claude_code(self.c, self.root / 'claude', self.root)
        r = u.make_report(self.c, 'Someone Else')
        self.assertEqual(r['totals']['total_tokens'], 135)
        self.assertEqual(r['totals']['input_tokens'], 130)
        self.assertEqual(r['totals']['requests'], 1)
        self.assertEqual(r['by_category']['subagent / sidechain']['requests'], 1)
        self.assertNotIn('PRIVATE PROMPT', json.dumps(r))
        self.assertNotIn('private-session', json.dumps(r))

    def test_chatgpt_split_zip_branches_dedup_and_unknown_tokens(self):
        conv = dict(id='private-conversation', title='SECRET TITLE', mapping={
            'a': dict(message=dict(id='u1', create_time=u.parse_time(AT), author={'role': 'user'}, content={'parts': ['SECRET TEXT']})),
            'b': dict(message=dict(id='a1', create_time=u.parse_time(AT) + 1, author={'role': 'assistant'}, metadata={'model_slug': 'model-A'})),
            'c': dict(message=dict(id='a2', create_time=u.parse_time(AT) + 2, author={'role': 'assistant'}, metadata={'model_slug': 'model-B'}))})
        path = self.root / 'export.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('nested/conversations-000.json', json.dumps([conv]))
            archive.writestr('../conversations-001.json', json.dumps([conv]))
            archive.writestr('users.json', json.dumps({'email': 'PRIVATE EMAIL'}))
        u.import_chats(self.c, path, 'chatgpt')
        r = u.make_report(self.c, '')
        self.assertEqual(r['totals']['user_messages'], 1)
        self.assertEqual(r['totals']['assistant_messages'], 2)
        self.assertEqual(r['totals']['chat_conversations'], 1)
        self.assertIsNone(r['totals']['total_tokens'])
        self.assertIsNone(r['totals']['requests'])
        for private in ('SECRET TITLE', 'SECRET TEXT', 'PRIVATE EMAIL', 'private-conversation'):
            self.assertNotIn(private, json.dumps(r))
        self.assertFalse((self.root / 'conversations-001.json').exists())

    def test_claude_chat_export_and_timestamp_gap(self):
        path = self.write_json('conversations.json', [{'uuid': 'conv', 'chat_messages': [
            {'uuid': '1', 'sender': 'human', 'created_at': AT, 'text': 'private'},
            {'uuid': '2', 'sender': 'assistant', 'created_at': AT},
            {'uuid': '3', 'sender': 'assistant', 'created_at': None}]}])
        u.import_chats(self.c, path, 'claude')
        self.assertEqual(u.aggregate(self.c.events)['user_messages'], 1)
        self.assertEqual(u.aggregate(self.c.events)['assistant_messages'], 1)
        self.assertEqual(self.c.coverage[0]['status'], 'partial retained chats')

    def test_cursor_total_without_guessing_input_and_cost_labels(self):
        path = self.root / 'usage.csv'
        with path.open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['Date', 'Model', 'Input Tokens', 'Cache Read Tokens', 'Output Tokens', 'Total Tokens', 'Cost'])
            writer.writerow([AT, 'cursor-model', 20, 80, 5, 105, 'Included'])
        u.import_cursor(self.c, path, 'auto')
        total = u.aggregate(self.c.events)
        self.assertEqual(total['total_tokens'], 105)
        self.assertIsNone(total['input_tokens'])
        self.assertEqual(total['costs_usd'], {})
        self.assertFalse(total['input_composition_complete_for_measured_tokens'])
        self.assertTrue(total['requests_is_lower_bound'])

    def test_cursor_explicit_uncached_and_numeric_dashboard_cost(self):
        path = self.root / 'usage.csv'
        with path.open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['Date', 'Request ID', 'Input Tokens', 'Cache Read Tokens', 'Cache Write Tokens', 'Output Tokens', 'Cost (USD)'])
            writer.writerow([AT, 'req', 20, 80, 10, 5, '$0.42'])
        u.import_cursor(self.c, path, 'uncached')
        t = u.aggregate(self.c.events)
        self.assertEqual(t['total_tokens'], 115)
        self.assertEqual(t['costs_usd']['dashboard_usage']['amount'], '0.42')
        self.assertNotIn('billed', t['costs_usd'])

    def test_cursor_analytics_csv_is_rejected(self):
        path = self.root / 'analytics.csv'
        path.write_text('Date,Lines Added,Tab Accepts\n2026-01-06,100,10\n')
        u.import_cursor(self.c, path, 'auto')
        self.assertEqual(self.c.events, [])
        self.assertEqual(self.c.coverage[0]['status'], 'unsupported CSV schema')

    def test_any_provider_generic_dedup_validation_and_cost_bases(self):
        records = [dict(id='1', timestamp=AT, app='Perplexity', requests=2, total_tokens=100, cost_usd='1.25', cost_basis='billed', prompt='SECRET'),
                   dict(id='2', timestamp=AT, app='Grok', input_tokens=20, output_tokens=5, cost_usd='0.5', cost_basis='estimate'),
                   dict(id='bad', timestamp=AT, app='Gemini', input_tokens=20, output_tokens=5, total_tokens=30)]
        path = self.write_lines('provider.jsonl', records + [records[0]])
        u.import_generic(self.c, path)
        r = u.make_report(self.c, '')
        self.assertEqual(r['totals']['total_tokens'], 125)
        self.assertEqual(r['totals']['requests'], 2)
        self.assertEqual(r['totals']['costs_usd']['billed']['amount'], '1.25')
        self.assertEqual(r['totals']['costs_usd']['estimate']['amount'], '0.5')
        self.assertNotIn('SECRET', json.dumps(r))

    def test_bucket_boundary_and_multiday_allocation(self):
        path = self.write_json('buckets.json', [
            dict(id='bad-boundary', app='Copilot', period_start='2026-01-04T00:00:00Z', period_end='2026-01-06T00:00:00Z', total_tokens=999),
            dict(id='good', app='Copilot', period_start='2026-01-06T00:00:00Z', period_end='2026-01-08T00:00:00Z', total_tokens=100)])
        u.import_generic(self.c, path)
        r = u.make_report(self.c, '')
        self.assertEqual(r['totals']['total_tokens'], 100)
        self.assertEqual(r['by_day']['Unallocated']['total_tokens'], 100)
        self.assertEqual(self.c.coverage[0]['diagnostics']['boundary_crossing_buckets_excluded'], 1)

    def test_exclusive_cutoff_and_timezone(self):
        c = u.Collector(u.parse_time(START), u.parse_time(END), ZoneInfo('America/New_York'))
        self.assertFalse(c.add({'app': 'Test', 'requests': 1}, 'cutoff', u.parse_time(END)))
        self.assertTrue(c.add({'app': 'Test', 'requests': 1}, 'before', u.parse_time('2026-01-06T01:00:00Z')))
        self.assertEqual(c.events[0]['day'], '2026-01-05')

    def test_cli_missing_sources_stay_unknown_and_all_outputs_work(self):
        out = self.root / 'out'
        result = subprocess.run([sys.executable, str(Path(u.__file__)), '--home', str(self.root), '--codex-root', str(self.root / 'none-codex'), '--claude-root', str(self.root / 'none-claude'), '--start', START, '--end', END, '--output', str(out), '--expected-app', 'Gemini'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        r = json.loads((out / 'report.json').read_text())
        self.assertIsNone(r['totals']['total_tokens'])
        self.assertIsNone(r['totals']['requests'])
        self.assertTrue(any(v['app'] == 'Gemini' and v['status'] == 'source needed' for v in r['coverage']))
        self.assertEqual({p.name for p in out.iterdir()}, {'report.json', 'report.md', 'report.html', 'daily.csv'})

    def test_corrupt_local_usage_is_partial_and_does_not_crash(self):
        sid = '44444444-4444-4444-4444-444444444444'
        self.write_lines(f'codex/sessions/{sid}.jsonl', [
            record('event_msg', {'type': 'token_count', 'info': {'total_token_usage': {'input_tokens': -5}, 'last_token_usage': {}}}),
            record('token_usage_record', {'thread_id': sid, 'response_id': 'valid', 'usage': usage(10, 2)})])
        u.collect_codex(self.c, self.root / 'codex')
        self.assertEqual(u.aggregate(self.c.events)['total_tokens'], 12)
        self.assertEqual(self.c.coverage[0]['status'], 'partial')

    def test_readable_history_with_no_window_activity_is_observed_zero(self):
        sid = '55555555-5555-5555-5555-555555555555'
        self.write_lines(f'codex/sessions/{sid}.jsonl', [
            record('token_usage_record', {'thread_id': sid, 'response_id': 'old', 'usage': usage(10)}, '2025-01-01T12:00:00Z')])
        u.collect_codex(self.c, self.root / 'codex')
        r = u.make_report(self.c, '')
        self.assertEqual(r['totals']['total_tokens'], 0)
        self.assertEqual(r['by_app']['Codex']['requests'], 0)
        self.assertEqual(self.c.coverage[0]['status'], 'measured local records')


if __name__ == '__main__':
    unittest.main()
