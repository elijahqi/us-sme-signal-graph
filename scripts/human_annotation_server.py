#!/usr/bin/env python3
"""Local human annotation app. No model calls; separate private reviewer records."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import urlsplit
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments/long_tail_benchmark/private/formal_v0_3"
TEMPLATE = ROOT / "scripts/templates/human_annotation.html"
PROTOCOL = "human-core-annotation-ui-v0.1"
ENUMS = {
    "identity_status": ["yes", "no", "unclear"],
    "direct_producer_status": ["yes", "no", "unclear"],
    "capability_match": ["yes", "partial", "no", "unclear"],
    "production_presence": ["industrial_facility_confirmed", "job_shop_or_workshop_confirmed",
        "owner_or_home_production_confirmed", "us_made_claim_site_unresolved",
        "office_warehouse_or_lab_only", "foreign_only", "unknown"],
    "commercial_offering": ["yes", "no", "unclear"],
    "eqdp": ["yes", "no", "unclear"],
    "primary_exclusion_reason": ["none", "not_operating_business", "identity_conflict", "duplicate_entity",
        "distributor_reseller_or_broker", "nonmanufacturing_service", "hobby_or_noncommercial",
        "capability_mismatch", "generic_sector_claim_only", "wrong_state", "office_warehouse_or_lab_only",
        "foreign_production_only", "historical_or_inactive", "insufficient_evidence", "source_unavailable"],
    "source_current_status": ["current", "historical", "inactive", "unclear"],
    "confidence": ["high", "medium", "low"],
    "conflict_disclosed": ["false", "true"],
    "scale_band": ["owner_only_or_nonemployer_supported", "micro_employer_1_9_supported",
        "small_employer_10_99_supported", "mid_employer_100_499_supported", "large_500_plus_supported", "unknown"],
    "legal_form": ["sole_proprietor", "single_member_llc", "other_llc", "partnership", "corporation", "other", "unknown"],
    "web_visibility": ["dedicated_business_domain", "marketplace_or_social_only", "directory_or_registry_only", "mixed", "unknown"],
    "affiliate_status": ["resolved_none", "resolved_included", "unresolved", "not_checked"],
    "sba_small_evidence_status": ["sba_self_certified_small", "size_consistent_unverified", "not_small", "unknown"],
}
TEXT_FIELDS = {"canonical_business_name", "legal_or_parent_name", "production_city", "production_state",
    "capability_evidence_span", "production_evidence_span", "capability_evidence_url", "production_evidence_url",
    "scale_evidence_url", "candidate_naics_2022", "sba_threshold", "sba_threshold_retrieved_at",
    "sam_uei_or_sba_id", "supplemental_evidence_urls", "notes"}
REQUIRED = ("identity_status", "direct_producer_status", "capability_match", "production_presence",
    "commercial_offering", "eqdp", "primary_exclusion_reason", "source_current_status", "confidence", "conflict_disclosed")
SUPPLEMENTARY = ("scale_band", "legal_form", "web_visibility", "affiliate_status", "sba_small_evidence_status")


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n"); f.flush(); os.fsync(f.fileno())
    os.chmod(tmp, 0o600); tmp.replace(path)


class Store:
    def __init__(self, directory, rows, provenance):
        self.directory, self.rows, self.provenance = Path(directory), rows, provenance
        self.by_id = {r["review_id"]: r for r in rows}
        if len(self.by_id) != len(rows):
            raise ValueError("Duplicate material ID")
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.directory, 0o700)
        self.lock = threading.RLock()
        self.nonce = secrets.token_urlsafe(32)
        digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
        self.cookie_name = "human_review_" + digest[:12]
        self.session_path = self.directory / "sessions.json"
        self.sessions = json.loads(self.session_path.read_text()) if self.session_path.exists() else {}

    def reviewer(self, token):
        return self.sessions.get(hashlib.sha256(token.encode()).hexdigest()) if token else None

    def create_session(self, alias):
        if not isinstance(alias, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", alias):
            raise ValueError("代号请用 1–40 个英文字母、数字、横线或下划线。")
        with self.lock:
            if any(s["alias"] == alias for s in self.sessions.values()):
                raise ValueError("这个代号已经使用。请用原浏览器继续；新标注人请另选代号。")
            token = secrets.token_urlsafe(32)
            session = {"id": uuid.uuid4().hex, "alias": alias, "created_at": now(),
                       "independent_review_declared": True}
            self.sessions[hashlib.sha256(token.encode()).hexdigest()] = session
            write_json(self.session_path, self.sessions)
            return token, session

    def records(self, reviewer):
        root = self.directory / "reviewers" / reviewer["id"] / "records"
        return {p.stem: json.loads(p.read_text()) for p in root.glob("*.json")}

    def validate(self, answers, status):
        if not isinstance(answers, dict) or set(answers) - (set(ENUMS) | TEXT_FIELDS | {"review_minutes"}):
            raise ValueError("包含不支持的标注字段。")
        for key, value in answers.items():
            if key == "review_minutes":
                if isinstance(value, bool) or not isinstance(value, (float, int)) or not 0 <= value <= 10000:
                    raise ValueError("复核分钟数无效。")
            elif not isinstance(value, str) or len(value) > 16000:
                raise ValueError("标注文字无效或过长。")
            elif key in ENUMS and value and value not in ENUMS[key]:
                raise ValueError("无效的判断选项。")
        if status == "submitted":
            if any(not answers.get(k) for k in REQUIRED):
                raise ValueError("请完成 5 个分项、总体判断、排除理由、来源状态、把握程度和利益关系披露。")
            if not answers.get("notes", "").strip():
                raise ValueError("请简短记录理由或仍然缺少的证据。")
            if answers.get("identity_status") == "yes" and not answers.get("canonical_business_name", "").strip():
                raise ValueError("企业身份为“是”时，请填写企业名称。")
            if answers.get("eqdp") == "yes":
                if answers.get("primary_exclusion_reason") != "none":
                    raise ValueError("总体为“是”时，主要排除理由应选“无”。")
                if not all(answers.get(k, "").strip() for k in ("capability_evidence_span", "production_evidence_span", "production_state")):
                    raise ValueError("总体为“是”时，请补上工艺引句、地点引句和生产州。")
            elif answers.get("primary_exclusion_reason") == "none":
                raise ValueError("总体为“否／信息不足”时，请选择主要排除理由。")
            if answers.get("review_minutes", 0) <= 0:
                raise ValueError("请记录实际复核分钟数；可修改本页计时。")

    def save(self, reviewer, rid, answers, status, base_revision):
        if rid not in self.by_id or status not in {"draft", "submitted"}:
            raise ValueError("未知材料或保存状态。")
        self.validate(answers, status)
        with self.lock:
            root = self.directory / "reviewers" / reviewer["id"]
            path = root / "records" / (rid + ".json")
            old = json.loads(path.read_text()) if path.exists() else {}
            if base_revision != old.get("revision", 0):
                raise ValueError("这条记录已在另一页面更新。请刷新读取最新版本，以免覆盖。")
            row = self.by_id[rid]
            record = {"review_id": rid, "reviewer_id": reviewer["alias"], "status": status,
                "revision": old.get("revision", 0) + 1, "answers": answers,
                "created_at": old.get("created_at", now()), "updated_at": now(),
                "protocol": PROTOCOL, "provenance": self.provenance,
                "page_sha256": row["page_sha256"], "source_url": row["source_url"],
                "capability_id": row["capability_id"], "queried_state": row["queried_state"],
                "human_entered": True, "independent_second_review_completed": False,
                "supplementary_fields_missing": [k for k in SUPPLEMENTARY if not answers.get(k)],
                "validation_flags": []}
            if status == "submitted":
                record["submitted_at"] = now()
            # Preserve contradictory human decisions as flagged observations, not corrected labels.
            if answers.get("eqdp") == "yes" and (any(answers.get(k) != "yes" for k in (
                    "identity_status", "direct_producer_status", "capability_match", "commercial_offering"))
                    or answers.get("production_presence") not in ENUMS["production_presence"][:3]):
                record["validation_flags"].append("positive_component_inconsistency")
            root.mkdir(parents=True, exist_ok=True, mode=0o700)
            history = root / "history.jsonl"
            with history.open("a") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())
            os.chmod(history, 0o600)
            write_json(path, record)
            return record


def make_server(store, port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def session(self):
            cookies = SimpleCookie(self.headers.get("Cookie", ""))
            cookie = cookies.get(store.cookie_name)
            return store.reviewer(cookie.value if cookie else "")

        def local_request(self, mutation=False):
            expected = f"127.0.0.1:{self.server.server_port}"
            if self.headers.get("Host") != expected:
                raise ValueError("仅接受本机页面访问。")
            origin = self.headers.get("Origin")
            if origin and origin != "http://" + expected:
                raise ValueError("不接受其他网站的请求。")
            if mutation and (self.headers.get("X-Review-Nonce") != store.nonce or
                             self.headers.get("Content-Type", "").split(";")[0] != "application/json"):
                raise ValueError("页面校验已过期，请刷新。")

        def respond(self, value, status=200, cookie=None, download=False, html=False):
            body = value.encode() if html else json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8" if html else "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            if cookie:
                self.send_header("Set-Cookie", f"{store.cookie_name}={cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age=31536000")
            if download:
                self.send_header("Content-Disposition", 'attachment; filename="my-human-annotations.json"')
            self.end_headers(); self.wfile.write(body)

        def do_GET(self):
            try:
                self.local_request()
                path = urlsplit(self.path).path
                if path in {"/", "/human_review_preview.html"}:
                    data = json.dumps(store.rows, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
                    page = TEMPLATE.read_text().replace("__DATA__", data).replace("__NONCE__", store.nonce)
                    if store.provenance.get("synthetic_test"):
                        page = page.replace("<h1>人工标注材料</h1>", "<h1>功能测试 · 虚构材料，不计入研究</h1>")
                    return self.respond(page, html=True)
                reviewer = self.session()
                if path == "/api/state":
                    return self.respond({"reviewer": reviewer["alias"] if reviewer else None,
                                         "records": store.records(reviewer) if reviewer else {}})
                if path == "/api/export" and reviewer:
                    return self.respond({"protocol": PROTOCOL, "reviewer_id": reviewer["alias"],
                        "exported_at": now(), "provenance": store.provenance,
                        "records": list(store.records(reviewer).values())}, download=True)
                self.respond({"error": "未找到页面或尚未开始标注。"}, 404)
            except ValueError as e:
                self.respond({"error": str(e)}, 403)

        def do_POST(self):
            try:
                self.local_request(mutation=True)
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 128000:
                    raise ValueError("保存内容大小无效。")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("需要有效的标注对象。")
                path = urlsplit(self.path).path
                reviewer = self.session()
                if path == "/api/session":
                    if reviewer:
                        return self.respond({"reviewer": reviewer["alias"]})
                    if data.get("independent") is not True:
                        raise ValueError("请先确认独立标注。")
                    token, reviewer = store.create_session(data.get("alias"))
                    return self.respond({"reviewer": reviewer["alias"]}, cookie=token)
                if path == "/api/save" and reviewer:
                    record = store.save(reviewer, data.get("review_id"), data.get("answers"),
                                        data.get("status"), data.get("base_revision"))
                    return self.respond({"record": record})
                raise ValueError("请先输入自己的标注代号。")
            except (ValueError, TypeError) as e:
                self.respond({"error": str(e)}, 400)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def load_materials():
    folder = PRIVATE / "human_review_preview_v0_1"
    manifest = json.loads((folder / "manifest.json").read_text())
    raw = (folder / "human_review_preview.html").read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest["output_sha256"]:
        raise ValueError("Material preview fingerprint changed")
    rows = json.loads(re.search(r'<script type="application/json" id="dataset">(.*?)</script>', raw.decode(), re.S).group(1))
    return rows, {"sample_sha256": manifest["sample_sha256"], "material_sha256": manifest["output_sha256"],
                  "frozen_double_review_subset": True, "planned_rows": len(rows), "synthetic_test": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=63164)
    args = parser.parse_args()
    rows, provenance = load_materials()
    store = Store(PRIVATE / "human_annotations_v0_1", rows, provenance)
    server = make_server(store, args.port)
    write_json(store.directory / "server.json", {"pid": os.getpid(), "port": server.server_port,
               "url": f"http://127.0.0.1:{server.server_port}/human_review_preview.html", "started_at": now()})
    print(json.dumps({"status": "serving", "port": server.server_port, "rows": len(rows)}), flush=True)
    server.serve_forever()
