#!/usr/bin/env python3
"""Fail closed if a public release contains restricted local artifacts."""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TRACKED_PREFIXES = (
    "data/raw/",
    "data/processed/",
    "experiments/search_uplift/provider_payloads/",
    "release/private/",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"(?:BRAVE_API_KEY|YOU_API_KEY|X_SUBSCRIPTION_TOKEN)\s*[:=]\s*['\"][^'\"]+", re.I),
    re.compile(r"https?://[^\s)'\"]*(?:byted\.org|larkoffice\.com)", re.I),
    re.compile(r"/Users/bytedance/"),
)


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> None:
    tracked = tracked_files()
    blocked_paths = [path for path in tracked if path.startswith(FORBIDDEN_TRACKED_PREFIXES)]
    if blocked_paths:
        raise SystemExit("Restricted paths are tracked:\n" + "\n".join(blocked_paths))
    blocked_content = []
    for relative in tracked:
        if relative == "scripts/release_preflight.py":
            continue
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                blocked_content.append(f"{relative}: {pattern.pattern}")
    if blocked_content:
        raise SystemExit("Restricted content markers found:\n" + "\n".join(blocked_content))
    print(f"release preflight passed for {len(tracked)} tracked files")


if __name__ == "__main__":
    main()
