#!/usr/bin/env python3
"""
Small CLI tool to exercise the references API endpoints.

Usage examples:
  python tools/test_references_api.py --base http://localhost:8000 --list --ref-type class
  python tools/test_references_api.py --base http://localhost:8000 --get 3
  python tools/test_references_api.py --base http://localhost:8000 --sync --token SECRET

This script uses only the Python standard library so it can run without extra packages.
"""
from __future__ import annotations

import argparse
import json
from urllib import request, parse, error


def http_get(url: str):
    try:
        with request.urlopen(url) as resp:
            data = resp.read()
            return resp.getcode(), data
    except error.HTTPError as he:
        return he.code, he.read()
    except Exception as e:
        print("Request failed:", e)
        return None, None


def http_post(url: str, headers: dict | None = None):
    req = request.Request(url, method="POST")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with request.urlopen(req) as resp:
            data = resp.read()
            return resp.getcode(), data
    except error.HTTPError as he:
        return he.code, he.read()
    except Exception as e:
        print("Request failed:", e)
        return None, None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Test references API endpoints")
    p.add_argument("--base", default="http://localhost:8000", help="Base URL for API")
    p.add_argument("--list", action="store_true", help="List references (uses --ref-type)")
    p.add_argument("--ref-type", default="class", help="Reference type to filter when listing")
    p.add_argument("--get", type=int, help="Get reference by ID")
    p.add_argument("--sync", action="store_true", help="Trigger sync-from-disk (requires --token)")
    p.add_argument("--token", help="Admin token for sync (X-Admin-Token header)")

    args = p.parse_args(argv)

    base = args.base.rstrip("/")

    if args.list:
        # Note: backend registers the list route at '/api/references/' and redirect_slashes=False
        url = f"{base}/api/references/?ref_type={parse.quote(args.ref_type)}"
        code, data = http_get(url)
        if code is None:
            return 2
        print("HTTP", code)
        try:
            print(json.dumps(json.loads(data), indent=2, ensure_ascii=False))
        except Exception:
            print(data.decode(errors="ignore"))
        return 0

    if args.get is not None:
        url = f"{base}/api/references/{args.get}"
        code, data = http_get(url)
        if code is None:
            return 2
        print("HTTP", code)
        try:
            print(json.dumps(json.loads(data), indent=2, ensure_ascii=False))
        except Exception:
            print(data.decode(errors="ignore"))
        return 0

    if args.sync:
        if not args.token:
            print("--sync requires --token")
            return 2
        url = f"{base}/api/references/sync-from-disk"
        headers = {"X-Admin-Token": args.token}
        code, data = http_post(url, headers=headers)
        if code is None:
            return 2
        print("HTTP", code)
        try:
            print(json.dumps(json.loads(data), indent=2, ensure_ascii=False))
        except Exception:
            print(data.decode(errors="ignore"))
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
