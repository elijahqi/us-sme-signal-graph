import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_glm_cross_review import frozen, decision
import glm_cross_review as g
import glm_retry_supervisor as s


class RetryTest(unittest.TestCase):
    def setup_failure(self, work):
        frozen(work)
        g.save(work / 'automatic_retry_authorization.json', {
            'enabled': True, 'max_retries_per_batch': 2,
            'protocol_sha256': g.sha(g.encoded(g.protocol()))})
        g.save(work / 'responses/batch-0001/response.json', {
            'is_error': True, 'result': 'API Error: ECONNRESET'})
        g.save(work / 'journal/batch-0001.json', {
            'batch_id': 'batch-0001', 'status': 'failed_or_uncertain',
            'protocol_sha256': g.sha(g.encoded(g.protocol()))})
        return (work / 'journal/batch-0001.json').read_bytes()

    def retry(self, work, call):
        clock = [0.0]
        def sleep(seconds):
            clock[0] += seconds
        with patch.object(g, 'EDITORIAL_OUTPUT', work / 'lock'):
            return s.retry_batch('batch-0001', work, call, sleep, lambda: clock[0])

    def test_retry_classification_never_uses_label_quality(self):
        entry = {'status': 'failed_or_uncertain'}
        for code in [408, 429, 500, 502, 503, 504, 529]:
            self.assertIsNotNone(s.retry_reason(entry, {'is_error': True, 'api_error_status': code}))
        for code in [400, 401, 402, 403, 404, 422]:
            self.assertIsNone(s.retry_reason(entry, {'is_error': True, 'api_error_status': code}))
        self.assertIsNone(s.retry_reason(entry, {'is_error': True, 'api_error_status': 429,
                                               'result': 'quota exhausted'}))
        self.assertIsNone(s.retry_reason(entry, {'subtype': 'success', 'result': 'invalid labels ECONNRESET'}))
        self.assertIsNone(s.retry_reason({'status': 'started'}, {'is_error': True, 'result': 'ECONNRESET'}))
        self.assertIsNotNone(s.retry_reason({**entry, 'error_type': 'TimeoutExpired'}, {}))

    def test_server_retry_after_extends_backoff(self):
        self.assertEqual(s.retry_delay({}, 2), 30)
        self.assertEqual(s.retry_delay({}, 3), 60)
        self.assertEqual(s.retry_delay({'retry_after': '120'}, 2), 120)
        self.assertEqual(s.retry_delay({'headers': {'Retry-After': 'Thu, 01 Jan 1970 00:03:00 GMT'}},
                                      2, lambda: 0), 180)

    def test_success_preserves_failure_bytes_and_prevents_further_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            old = self.setup_failure(work)
            original_response = (work / 'responses/batch-0001/response.json').read_bytes()
            def success(batch, destination):
                response = {'result': json.dumps({'results': [decision()]})}
                g.save(destination / 'response.json', response)
                return response
            result = self.retry(work, success)
            self.assertEqual((result['attempt'], result['status']), (2, 'completed'))
            self.assertEqual((work / 'journal_history/batch-0001-attempt-01-before-auto-retry.json').read_bytes(), old)
            self.assertEqual((work / 'responses/batch-0001/response.json').read_bytes(), original_response)
            self.assertEqual(s.verify_history(work), 1)
            self.assertEqual(g.analyze(work)['valid_rows'], 1)
            with self.assertRaisesRegex(ValueError, 'Existing labels'):
                self.retry(work, lambda *args: self.fail('No replay'))
            (work / 'responses/batch-0001/response.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Previous attempt hash'):
                g.analyze(work)

    def test_two_retries_maximum_across_restart_and_attempts_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            self.setup_failure(work)
            def fail(batch, destination):
                g.save(destination / 'response.json', {'is_error': True, 'result': 'API Error: HTTP 503'})
                raise ValueError('Temporary failure')
            self.assertEqual(self.retry(work, fail)['attempt'], 2)
            self.assertEqual(self.retry(work, fail)['attempt'], 3)
            self.assertEqual(s.verify_history(work), 2)
            with self.assertRaisesRegex(ValueError, 'budget exhausted'):
                self.retry(work, lambda *args: self.fail('Attempt 4 forbidden'))

    def test_changed_authorization_cannot_enable_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            self.setup_failure(work)
            g.save(work / 'automatic_retry_authorization.json', {'enabled': True,
                   'max_retries_per_batch': 2, 'protocol_sha256': 'other'})
            with self.assertRaisesRegex(ValueError, 'Authorization protocol'):
                self.retry(work, lambda *args: self.fail('No request'))


class MaxProfileTest(unittest.TestCase):
    def test_old_frozen_protocol_is_preserved_and_max_is_separate(self):
        with patch.object(g, 'EFFORT', 'low'), patch.object(g, 'WORK', g.WORK):
            self.assertEqual(g.sha(g.encoded(g.protocol())),
                             '114a987d6356434fcc6aeaea42290ac81c6cea55fbbac110628fe062f55166dd')
            low = g.configure_profile('low')
            maximum = g.configure_profile('max')
            self.assertNotEqual(low, maximum)
            self.assertEqual(g.protocol()['wire_effort_required'], 'max')
            self.assertEqual(g.protocol()['model'], 'glm-5.3')

    def test_max_requires_actual_request_effort_and_a_completed_pacing_trace(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(g, 'EFFORT', 'max'):
            path = Path(directory) / 'transport.json'
            record = {'path': '/api/anthropic/v1/messages', 'model': 'glm-5.3', 'effort': 'max',
                      'started_monotonic': 1, 'finished_monotonic': 10}
            g.save(path, {'requests': [record]})
            g.verify_transport(path)
            for edits in [{'effort': 'low'}, {'model': 'glm-5.3-flash'}, {'finished_monotonic': None}]:
                g.save(path, {'requests': [{**record, **edits}]})
                with self.assertRaises(ValueError):
                    g.verify_transport(path)
            g.save(path, {'requests': [record, {**record, 'started_monotonic': 10.5, 'finished_monotonic': 15}]})
            with self.assertRaisesRegex(ValueError, 'pacing'):
                g.verify_transport(path)
