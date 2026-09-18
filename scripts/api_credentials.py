#!/usr/bin/env python3
"""Store project API keys in macOS Keychain; never print secret values."""
import argparse
import getpass
import re
import subprocess

SERVICE_PREFIX = "us-sme-signal-graph"
PROVIDERS = ("google", "zai")


def read_key(provider):
    if provider not in PROVIDERS:
        raise ValueError("unsupported provider")
    result = subprocess.run(
        ["/usr/bin/security", "find-generic-password", "-a", "api-key",
         "-s", f"{SERVICE_PREFIX}.{provider}", "-w"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode or not result.stdout.strip():
        raise RuntimeError(f"No accessible {provider} key in macOS Keychain")
    return result.stdout.strip()


def store_key(provider, secret):
    if provider not in PROVIDERS or not re.fullmatch(r"[A-Za-z0-9_.-]{16,512}", secret):
        raise ValueError("unsupported provider or malformed key")
    # Interactive stdin keeps the secret out of process arguments and shell history.
    command = (f'add-generic-password -U -a api-key -s {SERVICE_PREFIX}.{provider} '
               f'-l "Supplier research: {provider} API key" -w "{secret}"\n')
    subprocess.run(["/usr/bin/security", "-i"], input=command,
                   text=True, capture_output=True, timeout=60, check=True)
    if read_key(provider) != secret:
        raise RuntimeError("Keychain read-back verification failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=PROVIDERS)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        read_key(args.provider)
    else:
        store_key(args.provider, getpass.getpass("API key (hidden): ").strip())
    print(f"{args.provider}: Keychain credential verified; value not displayed.")
