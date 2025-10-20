#!/usr/bin/env python3
"""
Round 2: send a focused set of robust next tasks to LM Studio and ask it to pick one.
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))
from lm_studio_client import LMStudioClient

LM_URL = os.environ.get('LM_STUDIO_URL', 'http://100.120.44.114:1234/v1')
MODEL = os.environ.get('LM_MODEL', 'gpt-4o-mini')

SUGGESTIONS = [
    {
        "id": "implement_playwright_test",
        "title": "Implement the Playwright test and run it locally (with mocked portrait responses)",
        "description": "Use the scaffold at scripts/playwright_portrait_review.spec.js, install Playwright, and run the test in headless mode, mocking the portrait endpoint to return the saved test image. Fix any UI selector mismatches."
    },
    {
        "id": "ci_playwright_job",
        "title": "Add a CI job (GitHub Actions) to run Playwright E2E on PRs",
        "description": "Create a workflow that runs Playwright against a deployed preview or a dev server started in the job. Report results and optionally post status to PR."
    },
    {
        "id": "executor",
        "title": "Add a safe executor to run LM-suggested low-risk commands",
        "description": "Implement a CLI flag (--approve) in feedback_loop_normalized.py that will run low-risk commands (linters, tests) locally after user confirmation, logging outputs."
    },
    {
        "id": "sd_host_followup",
        "title": "Open issue/step list for SD WebUI PermissionError remediation",
        "description": "Create a minimal checklist and playbook for the host owner to fix the PermissionError (file perms, extension config), with commands to run on the SD host."
    }
]

client = LMStudioClient(base_url=LM_URL, timeout=120)

system = {"role":"system","content":"You are an engineering planner. Given candidate next tasks, select the single most valuable next task and return only JSON with keys: chosen_id, chosen_title, rationale, steps(array of short steps), commands (array), estimated_time_minutes(int), risk (low|medium|high)."}
user = {"role":"user","content": f"Project: storycraft (sd-integration). Candidate tasks:\n{json.dumps(SUGGESTIONS, indent=2)}\n\nPick one and reply with the JSON schema described."}

print('Sending round-2 suggestions to LM Studio...')
try:
    resp = client.chat(MODEL, [system, user], max_tokens=800)
    content = resp['choices'][0]['message']['content']
    print('Raw content:\n')
    print(content)
    # Clean code fences
    import re
    content_clean = re.sub(r"^\s*```(?:json)?\n", "", content)
    content_clean = re.sub(r"\n```\s*$", "", content_clean)
    try:
        parsed = json.loads(content_clean)
        print('\nParsed JSON:')
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print('\nFailed to parse JSON:', e)
except Exception as e:
    print('Request failed:', e)
