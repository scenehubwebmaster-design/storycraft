#!/usr/bin/env python3
"""
Send a set of robust suggested next tasks to LM Studio and ask it to pick one and return a structured plan.
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
        "id": "lint",
        "title": "Run lint/typecheck on CreateCharacter.jsx and fix any issues",
        "description": "Run frontend lint and TypeScript/JSX type checks, fix syntax or type errors found. Low risk."
    },
    {
        "id": "e2e",
        "title": "Add an E2E test for the create->review portrait + traits flow",
        "description": "Create a Playwright or Cypress test that runs generation, checks that physical traits and portrait are shown in the review step. Medium risk, moderate work."
    },
    {
        "id": "backend_tests",
        "title": "Add/expand backend tests for fallback persistence and SD client response handling",
        "description": "Add pytest cases that mock LLM fallback and Stable Diffusion responses to prevent regressions. Low-medium risk."
    },
    {
        "id": "sd_host_debug",
        "title": "Investigate and remediate SD WebUI host PermissionError",
        "description": "Host-side task: inspect extension logs and permissions for D:\\SD-Zluda\\models\\Lora; may require changing file perms or extension config. High risk (host-side)."
    }
]

client = LMStudioClient(base_url=LM_URL, timeout=60)

system = {"role":"system","content":"You are an engineering planner. Given a short list of suggestions, pick the single most valuable next suggestion and return a JSON object with keys: chosen_id, chosen_title, rationale, suggested_steps (array of short steps), estimated_time_minutes (integer), risk (low|medium|high), commands (array of shell commands if applicable). Respond only with JSON."}
user = {"role":"user","content": f"Project summary: storycraft on branch sd-integration. Recent work included backend fallback persistence, frontend name-merge, SD client hardening. Here are candidate next tasks:\n\n{json.dumps(SUGGESTIONS, indent=2)}\n\nPlease select the single most valuable next task and return the structured JSON as described."}

print('Sending suggestions to LM Studio...')
try:
    resp = client.chat(MODEL, [system, user], max_tokens=500)
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
