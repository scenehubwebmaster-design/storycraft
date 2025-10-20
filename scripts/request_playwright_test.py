#!/usr/bin/env python3
"""
Ask LM Studio to generate a Playwright test file for the create->review portrait + traits flow.
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))
from lm_studio_client import LMStudioClient

LM_URL = os.environ.get('LM_STUDIO_URL', 'http://100.120.44.114:1234/v1')
MODEL = os.environ.get('LM_MODEL', 'gpt-4o-mini')

client = LMStudioClient(base_url=LM_URL, timeout=120)

system = {"role":"system","content":"You are a test generator. Produce a Playwright test file (JavaScript) that navigates the storycraft frontend (running at http://localhost:5173) to create a DnD character using the existing UI, triggers portrait generation (mocking the backend portrait response if needed), and asserts that the review step shows skin/eyes/hair and the portrait image. Return only the raw file content enclosed in triple backticks as a code block."}
user = {"role":"user","content":"Return a Playwright test (e.g., tests/portrait_review.spec.js). Keep it focused: open the create page, fill minimal required fields, click generate, wait for review, assert traits text and an img with data-src or src containing 'data:image' is displayed. Use test.locators or selectors that are reasonably robust. Mention any test setup needed (install/playwright)."}

print('Requesting Playwright test from LM Studio...')
try:
    resp = client.chat(MODEL, [system, user], max_tokens=800)
    content = resp['choices'][0]['message']['content']
    print('Raw content:\n')
    print(content[:8000])
    # extract code block
    import re
    m = re.search(r"```(?:javascript|js)?\n([\s\S]*?)\n```", content)
    test_code = m.group(1) if m else content
    out_path = os.path.join(os.path.dirname(__file__), 'playwright_portrait_review.spec.js')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(test_code)
    print('\nWrote test to', out_path)
except Exception as e:
    print('Request failed:', e)
