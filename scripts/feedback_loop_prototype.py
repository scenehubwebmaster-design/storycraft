#!/usr/bin/env python3
"""
Prototype feedback loop: collect git diff and send to LM Studio for review.
"""
import subprocess
import json
from lm_studio_client import LMStudioClient

MODEL = "gpt-4o-mini"


def get_git_diff():
    try:
        repo_root = r"e:\\storycraft"
        # show working tree changes first
        raw = subprocess.check_output(["git", "diff"], cwd=repo_root, text=False)
        diff = raw.decode('utf-8', errors='replace')
        if not diff.strip():
            # fallback to last commit diff
            raw = subprocess.check_output(["git", "diff", "HEAD~1..HEAD"], cwd=repo_root, text=False)
            diff = raw.decode('utf-8', errors='replace')
        return diff
    except subprocess.CalledProcessError:
        # fallback: show staged changes
        repo_root = r"e:\\storycraft"
        raw = subprocess.check_output(["git", "diff", "--staged"], cwd=repo_root, text=False)
        diff = raw.decode('utf-8', errors='replace')
        return diff


def main():
    diff = get_git_diff()
    if not diff:
        print("No local diffs found. Make a change or run from repo root.")
        return

    client = LMStudioClient()
    system = {
        "role": "system",
        "content": "You are a code reviewer assistant. Provide concise, prioritized feedback for the attached git diff. Give actionable items, risk assessment, and a suggested PR description. Respond in JSON with fields: issues:[{file, line_hint, severity, description, fix_suggestion}], pr_description, tests_to_add[]."
    }

    user = {"role": "user", "content": f"Here is the git diff:\n\n{diff[:15000]}"}

    resp = client.chat(MODEL, [system, user], max_tokens=800)
    print(json.dumps(resp, indent=2)[:8000])


if __name__ == '__main__':
    main()
