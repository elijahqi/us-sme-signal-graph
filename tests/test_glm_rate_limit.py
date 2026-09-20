import http.client
import io
import json
from pathlib import Path
import sys
import unittest
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from glm_rate_limit import RequestPacer, rate_limited_endpoint


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class FakeResponse:
    status = 200

    def __init__(self):
        self.data = io.BytesIO(b'data: {"type":"message_stop"}\n\n')

    def getheaders(self):
        return [("content-type", "text/event-stream"), ("transfer-encoding", "chunked")]

    def read1(self, size):
        return self.data.read(size)


class RateLimitTest(unittest.TestCase):
    def request(self, endpoint, path="/v1/messages?beta=true", token=None, body=None):
        parts = urlsplit(endpoint.url)
        client = http.client.HTTPConnection(parts.hostname, parts.port, timeout=5)
        client.request("POST", parts.path + path, body=body or b'{"model":"glm-5.3"}',
                       headers={"x-api-key": endpoint.token if token is None else token,
                                "Content-Type": "application/json"})
        response = client.getresponse()
        value = response.status, response.read(), dict(response.getheaders())
        client.close()
        return value

    def test_max_profile_blocks_wrong_effort_before_upstream_and_records_only_metadata(self):
        calls, records = [], []
        class Connection:
            def __init__(self, *args, **kwargs):
                pass
            def request(self, method, path, body, headers):
                calls.append(body)
            def getresponse(self):
                return FakeResponse()
            def close(self):
                pass
        with rate_limited_endpoint('synthetic-secret', connect=Connection,
                                   expected_model='glm-5.3', expected_effort='max', observe=records.append) as endpoint:
            for config in [{}, {'effort': 'low'}]:
                body = json.dumps({'model': 'glm-5.3', 'output_config': config}).encode()
                self.assertEqual(self.request(endpoint, body=body)[0], 400)
            body = json.dumps({'model': 'glm-5.3', 'output_config': {'effort': 'max'},
                               'messages': [{'role': 'user', 'content': 'synthetic-private-evidence'}]}).encode()
            self.assertEqual(self.request(endpoint, body=body)[0], 200)
        self.assertEqual(calls, [body])
        self.assertEqual(records[0]['effort'], 'max')
        self.assertNotIn('synthetic-secret', json.dumps(records))
        self.assertNotIn('synthetic-private-evidence', json.dumps(records))

    def test_actual_requests_and_continuations_wait_after_previous_response(self):
        clock, calls = FakeClock(), []
        class Connection:
            def __init__(self, host, timeout):
                self.host = host

            def request(self, method, path, body, headers):
                calls.append((clock.now, self.host, method, path, body, headers))
                clock.now += 5  # A long-running first request must also finish first.

            def getresponse(self):
                return FakeResponse()

            def close(self):
                pass

        with rate_limited_endpoint("synthetic-upstream-secret", connect=Connection,
                                   pacer=RequestPacer(clock.clock, clock.sleep)) as endpoint:
            for _ in range(2):
                status, body, headers = self.request(endpoint)
                self.assertEqual(status, 200)
                self.assertEqual(body, b'data: {"type":"message_stop"}\n\n')
                self.assertNotIn("Transfer-Encoding", headers)
        self.assertEqual([c[0] for c in calls], [1.0, 7.0])
        self.assertEqual(calls[0][1:4], ("api.z.ai", "POST", "/api/anthropic/v1/messages?beta=true"))
        self.assertEqual(calls[0][5]["x-api-key"], "synthetic-upstream-secret")
        self.assertNotEqual(endpoint.token, "synthetic-upstream-secret")

    def test_unapproved_path_and_wrong_local_token_do_not_contact_upstream(self):
        def forbidden(*args, **kwargs):
            self.fail("No upstream request expected")
        with rate_limited_endpoint("synthetic", connect=forbidden) as endpoint:
            self.assertEqual(self.request(endpoint, path="/other")[0], 404)
            self.assertEqual(self.request(endpoint, token="wrong")[0], 403)

    def test_upstream_error_is_not_retried_and_next_call_is_paced(self):
        clock, starts = FakeClock(), []
        def fail(*args, **kwargs):
            starts.append(clock.now)
            raise ConnectionResetError()
        with rate_limited_endpoint("synthetic", connect=fail,
                                   pacer=RequestPacer(clock.clock, clock.sleep)) as endpoint:
            for _ in range(2):
                status, body, _ = self.request(endpoint)
                self.assertEqual(status, 502)
                self.assertNotIn(b"synthetic", body)
        self.assertEqual(starts, [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
