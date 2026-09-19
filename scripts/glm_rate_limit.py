"""Local pacing for Claude Code's Z.ai requests, including continuations.

One upstream request at a time; wait at least one second before the next.
The official client remains the caller. Credentials and payloads are not logged.
"""
from contextlib import contextmanager
import hmac
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import secrets
import threading
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

MAX_QPS = 1
MIN_GAP_SECONDS = 1.0
UPSTREAM_HOST = "api.z.ai"
ALLOWED_PATHS = {"/api/anthropic/v1/messages", "/api/anthropic/v1/messages/count_tokens"}
HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
               "te", "trailer", "transfer-encoding", "upgrade", "host", "content-length"}


class RequestPacer:
    def __init__(self, clock=time.monotonic, sleep=time.sleep):
        self.clock, self.sleep = clock, sleep
        # Also protect the boundary between distinct client processes.
        self.ready_at = clock() + MIN_GAP_SECONDS

    def wait(self):
        while True:
            remaining = self.ready_at - self.clock()
            if remaining <= 0:
                return
            self.sleep(remaining)

    def finished(self):
        self.ready_at = self.clock() + MIN_GAP_SECONDS


def handler_for(key, token, pacer, connect):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *args):
            pass

        def do_POST(self):
            supplied = self.headers.get("x-api-key", "")
            bearer = self.headers.get("Authorization", "")
            if not (hmac.compare_digest(supplied, token) or
                    hmac.compare_digest(bearer, "Bearer " + token)):
                self.send_error(403, "Local client authorization required")
                return
            parsed = urlsplit(self.path)
            if parsed.scheme or parsed.netloc or parsed.path not in ALLOWED_PATHS:
                self.send_error(404, "Unsupported API path")
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                length = -1
            if length < 0 or length > 32 * 1024 * 1024 or self.headers.get("Transfer-Encoding"):
                self.send_error(411, "A bounded content length is required")
                return
            body = self.rfile.read(length)
            if len(body) != length:
                self.send_error(400, "Incomplete client request")
                return
            headers = {name: value for name, value in self.headers.items()
                       if name.lower() not in HOP_HEADERS | {"authorization", "x-api-key"}}
            headers["x-api-key"] = key
            pacer.wait()
            upstream = None
            response_started = False
            try:
                upstream = connect(UPSTREAM_HOST, timeout=840)
                upstream.request("POST", self.path, body=body, headers=headers)
                response = upstream.getresponse()
                self.send_response(response.status)
                for name, value in response.getheaders():
                    if name.lower() not in HOP_HEADERS:
                        self.send_header(name, value)
                self.send_header("Connection", "close")
                self.end_headers()
                response_started = True
                while True:
                    data = response.read1(65536)
                    if not data:
                        break
                    self.wfile.write(data)
                    self.wfile.flush()
            except (OSError, http.client.HTTPException):
                if not response_started:
                    self.send_error(502, "Upstream connection failed; no proxy retry")
                # An interrupted stream is closed, never completed or replayed.
            finally:
                if upstream is not None:
                    upstream.close()
                pacer.finished()
                self.close_connection = True

    return Handler


@contextmanager
def rate_limited_endpoint(key, *, connect=http.client.HTTPSConnection, pacer=None):
    token = secrets.token_urlsafe(32)
    handler = handler_for(key, token, pacer or RequestPacer(), connect)
    # A single server thread also serializes the client's continuation requests.
    server = HTTPServer(("127.0.0.1", 0), handler)
    worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    worker.start()
    try:
        yield SimpleNamespace(url=f"http://127.0.0.1:{server.server_port}/api/anthropic", token=token)
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
