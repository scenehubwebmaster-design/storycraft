#!/usr/bin/env python3
"""
Send a normalized project summary to LM Studio and ask for a single next action in JSON.
"""
import os
import sys
import json
# Ensure scripts/ is on sys.path when running as a script
sys.path.insert(0, os.path.dirname(__file__))
from lm_studio_client import LMStudioClient

LM_URL = os.environ.get('LM_STUDIO_URL', 'http://100.120.44.114:1234/v1')
MODEL = os.environ.get('LM_MODEL', 'gpt-4o-mini')

SUMMARY = {
    "project": "storycraft",
    "branch": "sd-integration",
    "recent_changes": [
        "Persisted e2e portrait test and save script",
        "Hardened Stable Diffusion client to accept image_base64",
        "Backend: persist fallback physical traits to structured_data",
        "Frontend: merge name suggestions from top-level and structured_data",
        "Fixed CreateCharacter.jsx syntax artifacts",
    "Added Playwright test scaffold for portrait/traits review at scripts/playwright_portrait_review.spec.js",
    "Implemented Playwright test at frontend/tests/portrait_review.spec.js"
    ],
    "open_tasks": [
        
        "Confirm NamePicker receives merged suggestions in review UI",
        "Add E2E frontend test to validate portrait + traits display",
        "Address SD WebUI host PermissionError (host-level)"
    ],
    "constraints": [
        "Do not push code to remote without human approval",
        "Limit changes to low-risk edits (tests, small fixes) unless approved",
        "Keep commit history small and reviewable"
    ]
}

client = LMStudioClient(base_url=LM_URL, timeout=60)

system = {"role":"system","content":"You are a disciplined engineering reviewer that replies only in JSON. Always respond with a single JSON object containing exactly these keys: next_action (string), rationale (string), commands (array of shell commands to run locally, optional), files_to_edit (array of objects {path, change_description}), risk (low|medium|high)."}
user = {"role":"user","content": f"Here is the project summary:\n{json.dumps(SUMMARY, indent=2)}\n\nQuestion: Given the summary and constraints, what is the SINGLE next action you recommend for the developer? Respond with the required JSON structure only."}

print('Sending normalized summary to LM Studio...')
try:
    resp = client.chat(MODEL, [system, user], max_tokens=400)
    content = resp['choices'][0]['message']['content']
    print('Raw content:\n')
    print(content)
    try:
        # extract JSON
        import re
        # Remove triple-backtick fences if present
        content_clean = re.sub(r"^\s*```(?:json)?\n", "", content)
        content_clean = re.sub(r"\n```\s*$", "", content_clean)
        m = re.search(r"\{[\s\S]*\}$", content_clean)
        json_text = m.group(0) if m else content_clean
        parsed = json.loads(json_text)
        print('\nParsed JSON:')
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print('Failed to parse JSON:', e)
except Exception as e:
    print('Request failed:', e)
