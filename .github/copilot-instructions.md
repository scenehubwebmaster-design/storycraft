<!-- Copilot/AI agent instructions for StoryCraft repository -->

This file tells an automated coding assistant how to be immediately productive in the StoryCraft monorepo.

Keep instructions short, factual and specific to this repository. When you recommend code edits, always: (1) write tests (Vitest / Playwright) if feasible, (2) add audit entries under `.feedback/audit/` for any planner or executor actions, and (3) never push or merge changes without human approval.

Repository overview (big picture)

- Monorepo: frontend (React + Vite + MUI + react-leaflet) and backend (FastAPI + SQLAlchemy).
- Frontend serves UI at http://localhost:3000; backend runs at http://localhost:8000 with OpenAPI at /docs.
- Key data flow: frontend constructs character structured output (stored as `structured_data`), posts to backend which persists structured JSON and can call LLMs or SD for images.

Important files and entry points (quick reference)

- Root scripts: `scripts/feedback_loop_normalized.py` — builds a normalized summary and queries LM Studio (JSON-only response required).
- LM client: `scripts/lm_studio_client.py` — use this client for programmatic LM calls (it implements retry).
- Orchestrator / executor: `scripts/feedback_orchestrator.py`, `scripts/executor.py` — audit planner responses to `.feedback/audit/` and run only whitelisted low-risk commands in dry-run unless `--approve` is specified.
- Frontend cluster component: `frontend/src/components/MapClusterGroup.jsx` (options, events). Unit tests live in `frontend/src/__tests__` and run with Vitest.
- Playwright E2E: `frontend/tests/portrait_review.spec.js` (deterministic path via `?e2e_mocks=1`).

Developer workflows & useful commands

- Install root deps and workspace: `npm install` (root) then `cd frontend && npm install`.
- Start full dev: `npm run dev:all` from repo root (runs frontend + backend concurrently).
- Frontend only: `cd frontend && npm run dev` (Vite host listens on network by default).
- Backend only: `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
- Run frontend unit tests: `cd frontend && npm run test:unit` (Vitest). Watch: `npm run test:unit:watch`.
- Run Playwright E2E locally (requires @playwright/test installed): `npx playwright test frontend/tests/portrait_review.spec.js`.

Project-specific conventions and patterns

- Tests: unit tests use Vitest + React Testing Library. E2E uses Playwright. When adding a feature, include a small Vitest test and, when relevant, a Playwright spec using `?e2e_mocks=1` to avoid flaky LM/SD calls.
- React: repo is pinned to React 19.2.0. Avoid introducing additional React runtimes; always check `npm ls react react-dom` if adding packages that may bring alternative versions.
- Leaflet clustering: `leaflet.markercluster` is the chosen plugin; `MapClusterGroup.jsx` integrates it directly. Mock `leaflet` functions (markerClusterGroup, marker) in unit tests.
- LM interactions: planner must return strict JSON (keys: next_action, rationale, commands, files_to_edit, risk). Use `scripts/lm_studio_client.py` and `scripts/feedback_loop_normalized.py` as canonical examples.
- Audit trail: any automated planner/executor call must write raw and parsed outputs to `.feedback/audit/` with a UTC timestamped filename.

Safety & approval rules (enforced by humans/executor)

- Never auto-commit or merge LM-suggested edits. The orchestrator should produce patches or draft PRs but require human review before merging.
- The executor (`scripts/executor.py`) only runs whitelisted low-risk commands by default (lint, unit tests, Playwright tests). It runs in dry-run unless `--approve` is passed.

When you create or change code, follow these steps

1. Add/modify source code in small, focused commits.
2. Add/adjust Vitest tests under `frontend/src/__tests__` for UI components or utilities.
3. Run `cd frontend && npm run test:unit` and `npx playwright test` (if you changed E2E flows).
4. If LM or orchestrator is touched, add audit output to `.feedback/audit/` and keep the orchestrator dry-run by default.

Examples to copy/inspect

- See how `MapClusterGroup.test.jsx` mocks `leaflet` and `react-leaflet` for testing cluster behavior.
- See `feedback_loop_normalized.py` and `feedback_orchestrator.py` for LM prompts, response parsing and audit wiring.

If anything is unclear or you want the agent to adopt a different approval policy (auto-approve low-risk suggestions, or always require an explicit human CLI approval), ask the repo maintainer before making the change.

End of instructions — ask for clarification if any repository-specific behavior is missing.

LM interaction policy (MANDATORY)

- All automated planner / reviewer LM calls MUST be routed through `scripts/feedback_loop_normalized.py`.
  - Purpose: the script enforces the normalized summary shape, uses `scripts/lm_studio_client.py` with retries, extracts strict JSON, and prints & helps persist raw+parsed outputs for auditing.
  - Do not call LM Studio directly from ad-hoc scripts or embed API calls in new code unless a human maintainer approves and documents the exception.
  - Example (PowerShell):

```powershell
cd e:\storycraft\scripts
python .\feedback_loop_normalized.py
```

- When writing an orchestrator or automation, call the script (shell out) or call `LMStudioClient` through the same normalized flow and always write raw + parsed outputs to `.feedback/audit/` with a UTC timestamped filename.
- The orchestrator (`scripts/feedback_orchestrator.py`) should use `feedback_loop_normalized.py` as the canonical planner entrypoint. If you choose to call the LM client directly, add a clear comment and write audit artifacts in the same format.
- Never log secrets (keys, tokens) in audit files. Audit files should contain only planner outputs and parsing results.

If you'd like, I can add a small wrapper that enforces this policy (e.g., an orchestrator that always shells out to `feedback_loop_normalized.py` and refuses to run if ad-hoc LM calls are detected in changed files).
