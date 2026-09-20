#!/usr/bin/env python3
"""Resume the frozen GLM pass with user-authorized, bounded transport retries."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import time

import glm_cross_review as g

MAX_RETRIES = 2
BACKOFF_SECONDS = (30, 60)
RETRY_STATUSES = {408, 429, 500, 502, 503, 504, 529}
RETRY_POLICY = "20260920-user-authorized-bounded-automatic-retries"
CAPTURE_FILES = ("response.json", "events.jsonl", "stderr.txt", "timeout_events.jsonl", "timeout_stderr.txt", "transport.json")


def authorization(work):
    value = json.loads((work / "automatic_retry_authorization.json").read_text())
    g.require(value.get("enabled") is True and value.get("max_retries_per_batch") == MAX_RETRIES,
              "Bounded automatic retry authorization is required")
    g.require(value.get("protocol_sha256") == g.sha(g.encoded(g.protocol())), "Authorization protocol mismatch")
    return value


def retry_reason(entry, response):
    """Classify execution failures only; never retry based on research labels."""
    if entry.get("status") != "failed_or_uncertain":
        return None
    if response and not response.get("is_error") and response.get("subtype") == "success":
        return None
    text = str(response.get("result", "")).casefold()
    if response.get("transport_error"):
        text += " upstream connection failed"
    permanent = ("insufficient_quota", "insufficient balance", "quota exhausted", "quota exceeded",
                 "usage limit reached", "payment required", "subscription expired", "invalid api key",
                 "额度已耗尽", "余额不足", "套餐已用完")
    if any(word in text for word in permanent):
        return None
    status = response.get("api_error_status") or response.get("status_code")
    if status is None:
        match = re.search(r"(?:api error:|http(?: status)?:?|status(?:_code)?[=:]?)\s*(\d{3})\b", text)
        status = int(match.group(1)) if match else None
    try:
        status = int(status) if status is not None else None
    except (TypeError, ValueError):
        status = None
    if status in {400, 401, 402, 403, 404, 422}:
        return None
    if status in RETRY_STATUSES:
        return "temporary_http_" + str(status)
    if any(word in text for word in ("econnreset", "econnrefused", "etimedout", "eai_again", "enetunreach",
                                    "connection reset", "connection timed out", "connection timeout",
                                    "upstream connection failed", "socket hang up")):
        return "temporary_connection_error"
    if entry.get("error_type") in {"TimeoutExpired", "TimeoutError", "ConnectionResetError", "ConnectionError"}:
        return "transport_" + entry["error_type"]
    return None


def retry_delay(response, attempt, wall_time=time.time):
    delay = BACKOFF_SECONDS[attempt - 2]
    headers = {str(k).lower(): v for k, v in response.get("headers", {}).items()}
    raw = response.get("retry_after", headers.get("retry-after"))
    if raw is not None:
        try:
            delay = max(delay, float(raw))
        except (ValueError, TypeError):
            try:
                delay = max(delay, parsedate_to_datetime(str(raw)).timestamp() - wall_time())
            except (ValueError, TypeError, OverflowError):
                pass
    return max(1.0, delay)


def verify_history(work):
    attempts = 0
    for path in (work / "journal").glob("*.json"):
        entry = json.loads(path.read_text())
        for prior in entry.get("previous_attempts", []):
            for relative, expected in prior["files"].items():
                g.require(g.sha((work / relative).read_bytes()) == expected, "Previous attempt hash mismatch")
            attempts += 1
    return attempts


def retry_batch(batch_id, work=g.WORK, call=g.invoke, sleep=time.sleep, wall_time=time.time):
    authorization(work)
    manifest, batches = g.load_frozen(work)
    batch = next(b for b in batches if b["batch_id"] == batch_id)
    g.EDITORIAL_OUTPUT.mkdir(parents=True, exist_ok=True)
    with (g.EDITORIAL_OUTPUT / ".serial.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        journal = work / "journal" / (batch_id + ".json")
        old_bytes = journal.read_bytes()
        old = json.loads(old_bytes)
        g.require(old["protocol_sha256"] == manifest["protocol_sha256"], "Failed journal protocol mismatch")
        g.require(not (work / "results" / (batch_id + ".json")).exists(), "Existing labels must not be rerun")
        previous_dir = work / old.get("response_directory", "responses/" + batch_id)
        response_path = previous_dir / "response.json"
        response = json.loads(response_path.read_text()) if response_path.exists() else {}
        reason = retry_reason(old, response)
        g.require(reason is not None, "Failure is not eligible for automatic transport retry")
        attempt = int(old.get("attempt", 1)) + 1
        g.require(attempt <= MAX_RETRIES + 1, "Automatic retry budget exhausted for this batch")
        verify_history(work)
        destination = work / "responses" / batch_id / f"attempt-{attempt:02d}"
        g.require(not destination.exists(), "Attempt destination already exists; inspect without replay")
        schedule_path = work / "retry_schedule" / f"{batch_id}-attempt-{attempt:02d}.json"
        old_sha = g.sha(old_bytes)
        if schedule_path.exists():
            schedule = json.loads(schedule_path.read_text())
            g.require(schedule["previous_journal_sha256"] == old_sha, "Retry schedule changed")
        else:
            schedule = {"attempt": attempt, "previous_journal_sha256": old_sha,
                        "not_before_unix": wall_time() + retry_delay(response, attempt, wall_time),
                        "reason": reason, "policy": RETRY_POLICY}
            g.save(schedule_path, schedule)
        while schedule["not_before_unix"] > wall_time():
            sleep(min(30, schedule["not_before_unix"] - wall_time()))
        archive = work / "journal_history" / f"{batch_id}-attempt-{attempt-1:02d}-before-auto-retry.json"
        archive.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(archive.parent, 0o700)
        if archive.exists():
            g.require(archive.read_bytes() == old_bytes, "Archived attempt changed")
        else:
            with archive.open("xb") as handle:
                handle.write(old_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(archive, 0o600)
        paths = [archive] + [previous_dir / name for name in CAPTURE_FILES if (previous_dir / name).exists()]
        if old.get("transport_recovery"):
            paths += [work / "journal_history" / (batch_id + "-before-transport-recovery.json"),
                      work / "responses" / batch_id / "response.json"]
        history = old.get("previous_attempts", []) + [{"attempt": attempt - 1, "quota_usage": "unknown",
                  "files": {str(p.relative_to(work)): g.sha(p.read_bytes()) for p in paths}}]
        entry = {"batch_id": batch_id, "rows": len(batch["rows"]), "status": "started", "attempt": attempt,
                 "started_utc": g.now(), "protocol_sha256": manifest["protocol_sha256"],
                 "processing_rule": g.PROCESSING_RULE, "automatic_retry": True, "retry_policy": RETRY_POLICY,
                 "retry_reason": reason, "previous_attempts": history,
                 "response_directory": str(destination.relative_to(work)), "max_qps": 1, "concurrency": 1,
                 "retry_supervisor_sha256": g.sha(Path(__file__).read_bytes()),
                 "implementation_sha256": g.sha(Path(g.__file__).read_bytes()),
                 "pacer_sha256": g.sha(Path(g.glm_rate_limit.__file__).read_bytes())}
        g.save(journal, entry)
        started = time.monotonic()
        try:
            recovered = call(batch, destination)
            entry["elapsed_seconds"] = round(time.monotonic() - started, 2)
            g.record_response(batch, recovered, entry, manifest, work)
        except Exception as exc:
            if isinstance(exc, subprocess.TimeoutExpired):
                key = g.read_key("zai")
                destination.mkdir(parents=True, exist_ok=True)
                os.chmod(destination, 0o700)
                for name, raw in (("timeout_events.jsonl", exc.stdout), ("timeout_stderr.txt", exc.stderr)):
                    value = raw.decode(errors="replace") if isinstance(raw, bytes) else raw or ""
                    path = destination / name
                    path.write_text(value.replace(key, "[REDACTED]"))
                    os.chmod(path, 0o600)
            entry.update(status="failed_or_uncertain", finished_utc=g.now(), error_type=type(exc).__name__,
                         quota_usage="unknown")
            g.save(journal, entry)
        return {k: entry.get(k) for k in ("batch_id", "attempt", "status", "valid_rows", "invalid_rows", "omitted_rows")}


def main(work=g.WORK):
    authorization(work)
    work.mkdir(parents=True, exist_ok=True)
    with (work / ".auto_retry_supervisor.lock").open("a") as supervisor_lock:
        fcntl.flock(supervisor_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = {"pid": os.getpid(), "started_utc": g.now(), "status": "running", "max_qps": 1,
                 "concurrency": 1, "model": g.MODEL, "effort": g.EFFORT,
                 "max_retries_per_batch": MAX_RETRIES, "policy": RETRY_POLICY}
        def status(phase, **extra):
            state.update(phase=phase, updated_utc=g.now(), **extra)
            g.save(work / "retry_supervisor.json", state)
        try:
            while True:
                with (g.EDITORIAL_OUTPUT / ".serial.lock").open("a") as probe:
                    try:
                        fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        status("waiting_for_existing_worker")
                        time.sleep(10)
                        continue
                manifest, batches = g.load_frozen(work)
                verify_history(work)
                entries = [json.loads(p.read_text()) for p in sorted((work / "journal").glob("*.json"))]
                failed = [entry for entry in entries if entry["status"] not in g.RESOLVED_STATUSES]
                if failed:
                    entry = failed[0]
                    status("retrying_failed_batch", batch_id=entry["batch_id"])
                    g.save(work / "active_worker.json", state)
                    result = retry_batch(entry["batch_id"], work)
                    print(json.dumps(result), flush=True)
                elif len(entries) < len(batches):
                    status("processing_unattempted_batches")
                    g.save(work / "active_worker.json", state)
                    try:
                        g.run(len(batches), work)
                    except ValueError:
                        # The journal, not the exception string, decides retry eligibility.
                        continue
                else:
                    summary = g.analyze(work)
                    prior_attempts = verify_history(work)
                    g.save(work / "automatic_retry_summary.json", {"policy": RETRY_POLICY,
                           "generated_utc": g.now(), "archived_prior_attempts": prior_attempts,
                           "batches_with_auto_retry": sum(bool(e.get("automatic_retry")) for e in entries),
                           "max_retries_per_batch": MAX_RETRIES, "previous_failed_usage": "unknown",
                           "row_level_data_included": False})
                    status("analysis_complete", status="finished", analysis_status=summary["status"])
                    g.save(work / "active_worker.json", state)
                    return
        except Exception as exc:
            status("requires_diagnosis", status="stopped", error_type=type(exc).__name__, reason=str(exc))
            g.save(work / "active_worker.json", state)
            print(json.dumps({"status": "stopped", "reason": str(exc)}), flush=True)
            raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("low", "max"), default="max")
    args = parser.parse_args()
    main(g.configure_profile(args.profile))
