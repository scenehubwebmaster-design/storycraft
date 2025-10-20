#!/usr/bin/env python3
"""
Minimal feedback orchestrator.
- Calls `feedback_loop_normalized.py` to get the LM's next action.
- Writes the raw LM response and parsed JSON into `.feedback/audit/<timestamp>.json`.
- Supports --approve flag to optionally run low-risk commands listed in the LM response (dry-run by default).
"""
import argparse
import subprocess
import json
from executor import is_low_risk, run_command
import os
from datetime import datetime

AUDIT_DIR = os.path.join(os.path.dirname(__file__), '..', '.feedback', 'audit')
os.makedirs(AUDIT_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--approve', action='store_true', help='Execute low-risk commands suggested by LM (use with caution)')
parser.add_argument('--dry-run', action='store_true', help='Do not execute commands; just write audit')
args = parser.parse_args()

# Run the normalized feedback script and capture output
proc = subprocess.run(['python', os.path.join(os.path.dirname(__file__), 'feedback_loop_normalized.py')], capture_output=True, text=True)
raw_out = proc.stdout + '\n' + proc.stderr

# Try to parse the parsed JSON printed by the script
parsed = None
for line in raw_out.splitlines():
    if line.strip().startswith('{'):
        try:
            parsed = json.loads('\n'.join(raw_out.splitlines()[raw_out.splitlines().index(line):]))
        except Exception:
            parsed = None
        break

# Write audit
stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
path = os.path.join(AUDIT_DIR, f'{stamp}.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump({'raw': raw_out, 'parsed': parsed}, f, indent=2)

print('Wrote audit to', path)

# If approval and parsed contains commands, run or simulate
if args.approve and parsed and parsed.get('commands'):
    cmds = parsed.get('commands')
    for c in cmds:
        print('\nRunning:', c)
        if args.dry_run:
            print('(dry-run) would run:', c)
        else:
            if not is_low_risk(c):
                print('Refusing to run non-low-risk command:', c)
                continue
            try:
                res = run_command(c, timeout=300)
                print('Return code:', res.get('returncode'))
                print('Stdout:', res.get('stdout'))
                print('Stderr:', res.get('stderr'))
            except Exception as e:
                print('Command failed:', e)

print('Orchestration complete.')
