#!/usr/bin/env python3
"""Simple feedback loop orchestrator that asks LM Studio for the next action and writes an audit.

This reuses the LMStudioClient and the SUMMARY pattern from feedback_loop_normalized.py.
It stores the raw LM response and the parsed JSON into `.feedback/audit/` with timestamps.
"""
import os
import sys
import json
from datetime import datetime
from lm_studio_client import LMStudioClient

LM_URL = os.environ.get('LM_STUDIO_URL', 'http://100.120.44.114:1234/v1')
MODEL = os.environ.get('LM_MODEL', 'gpt-4o-mini')

SUMMARY = {
    "project": "storycraft",
    "branch": "sd-integration",
    "recent_changes": [],
    "open_tasks": [],
    "constraints": [
        "Do not push code to remote without human approval",
        "Limit changes to low-risk edits (tests, small fixes) unless approved",
    ],
}


def ensure_audit_dir():
    d = os.path.join(os.getcwd(), '.feedback', 'audit')
    os.makedirs(d, exist_ok=True)
    return d


def write_audit(raw_content, parsed=None):
    d = ensure_audit_dir()
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    raw_path = os.path.join(d, f'lm_raw_{ts}.txt')
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write(raw_content)
    if parsed is not None:
        parsed_path = os.path.join(d, f'lm_parsed_{ts}.json')
        with open(parsed_path, 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2)
    return raw_path


def run_orchestrator(extra_summary=None):
    client = LMStudioClient(base_url=LM_URL)
    system = {"role": "system", "content": "You are a disciplined engineering reviewer that replies only in JSON. Always respond with a single JSON object containing exactly these keys: next_action (string), rationale (string), commands (array of shell commands to run locally, optional), files_to_edit (array of objects {path, change_description}), risk (low|medium|high)."}
    user = {"role": "user", "content": f"Here is the project summary:\n{json.dumps(SUMMARY, indent=2)}\n\nQuestion: Given the summary and constraints, what is the SINGLE next action you recommend for the developer? Respond with the required JSON structure only."}

    print('Sending summary to LM...')
    resp = client.chat(MODEL, [system, user], max_tokens=400)
    content = resp['choices'][0]['message']['content']
    print('Raw content received from LM.')
    parsed = None
    try:
        import re
        content_clean = re.sub(r"^\s*```(?:json)?\n", "", content)
        content_clean = re.sub(r"\n```\s*$", "", content_clean)
        m = re.search(r"\{[\s\S]*\}$", content_clean)
        json_text = m.group(0) if m else content_clean
        parsed = json.loads(json_text)
        print('Parsed JSON from LM.')
    except Exception as e:
        print('Failed to parse LM JSON:', e)

    write_audit(content, parsed)
    return content, parsed


if __name__ == '__main__':
    content, parsed = run_orchestrator()
    print('Orchestrator finished. Check .feedback/audit for saved traces.')
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
