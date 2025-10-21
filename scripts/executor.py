#!/usr/bin/env python3
"""Safe local executor for running low-risk commands returned by the feedback loop.

Usage:
  python executor.py --commands "npm --prefix frontend run test:unit" --dry-run
  python executor.py --commands-file ./commands.json --approve

The executor supports a dry-run mode (default) and an --approve flag to actually run commands.
It enforces a whitelist of safe command patterns to avoid accidental destructive operations.
"""
import argparse
import subprocess
import shlex
import os
import json
from datetime import datetime
import re


SAFE_PATTERNS = [
    r"^npm(\s+--prefix\s+[^\s]+)?\s+run\s+(test|lint)",
    r"^npx\s+playwright\s+test",
    r"^pytest",
    r"^flake8",
    r"^python\s+-m\s+pytest",
]


def is_low_risk(cmd: str) -> bool:
    s = cmd.strip()
    for p in SAFE_PATTERNS:
        if re.search(p, s):
            return True
    return False


def run_command(cmd: str, timeout: int = 120) -> dict:
    """Run a shell command and return a dict with stdout/stderr/returncode."""
    parts = shlex.split(cmd)
    try:
        proc = subprocess.run(parts, capture_output=True, text=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "returncode": -1, "stdout": "", "stderr": f"Timeout after {timeout}s"}


def ensure_audit_dir():
    d = os.path.join(os.getcwd(), '.feedback', 'audit')
    os.makedirs(d, exist_ok=True)
    return d


def write_result(result: dict):
    d = ensure_audit_dir()
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    path = os.path.join(d, f'exec_{ts}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--commands', type=str, help='Single command to run')
    p.add_argument('--commands-file', type=str, help='JSON file with array of commands')
    p.add_argument('--approve', action='store_true', help='Actually run commands (otherwise dry-run)')
    p.add_argument('--timeout', type=int, default=120, help='Per-command timeout in seconds')
    args = p.parse_args()

    cmds = []
    if args.commands:
        cmds = [args.commands]
    elif args.commands_file:
        with open(args.commands_file, 'r', encoding='utf-8') as f:
            cmds = json.load(f)
            if not isinstance(cmds, list):
                print('commands-file must contain a JSON array of commands')
                return 2
    else:
        print('No commands provided. Use --commands or --commands-file')
        return 2

    results = {'approved': args.approve, 'runs': []}

    for cmd in cmds:
        allowed = is_low_risk(cmd)
        entry = {'cmd': cmd, 'allowed': allowed}
        if not allowed:
            entry['skipped'] = True
            entry['reason'] = 'Not in safe whitelist'
            print('Skipping unsafe command:', cmd)
            results['runs'].append(entry)
            continue

        if not args.approve:
            entry['skipped'] = True
            entry['reason'] = 'Dry-run (use --approve to execute)'
            print('Dry-run:', cmd)
            results['runs'].append(entry)
            continue

        print('Executing:', cmd)
        res = run_command(cmd, timeout=args.timeout)
        entry.update(res)
        results['runs'].append(entry)

    path = write_result(results)
    print('Wrote execution audit to', path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
import subprocess
import shlex
import sys
from typing import Tuple, Dict, Any

# Simple allowlist of low-risk commands (exact prefixes)
ALLOWED_PREFIXES = [
    "npm run lint",
    "npm run test",
    "pytest",
    sys.executable,  # allow python commands
]


def is_low_risk(cmd: str) -> bool:
    """Return True if the command is considered low-risk according to allowlist."""
    c = cmd.strip()
    for p in ALLOWED_PREFIXES:
        if isinstance(p, str) and c.startswith(p):
            return True
    return False


def run_command(cmd: str, timeout: int = 120) -> Dict[str, Any]:
    """Run a shell command safely and return a dict with stdout/stderr/rc.

    Accepts a command string; uses shell for convenience.
    """
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "returncode": None, "stdout": "", "stderr": f"Timeout: {e}"}
    except Exception as e:
        return {"cmd": cmd, "returncode": None, "stdout": "", "stderr": str(e)}
