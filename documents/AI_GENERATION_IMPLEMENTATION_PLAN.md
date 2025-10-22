# AI Generation Implementation Plan

This plan describes a practical, incremental implementation roadmap for robust AI-driven story, world, and character generation for StoryCraft. It's written so the orchestrator and `scripts/feedback_loop_normalized.py` can drive each step iteratively.

Goals

- Provide stable, auditable backend endpoints to request story/world/character generations.
- Persist structured outputs (`structured_data`) and generated portraits (SD images) in the database and storage.
- Provide frontend flows for generation, preview, and human review with deterministic E2E tests.
- Keep human-in-the-loop for code changes; automate low-risk operations (tests, lint) only after approval.

Phased roadmap (short, incremental sprints)

Phase 0 — Prep (done / immediate)

- Ensure LM client `scripts/lm_studio_client.py` works and `scripts/feedback_loop_normalized.py` is the canonical planner entrypoint.
- Add `.feedback/audit/` directory and ensure scripts write raw+parsed outputs with UTC timestamps.

Phase 1 — Backend scaffolding (1-2 days)

- Add endpoints:
  - POST /api/generate/character (input: seed prompts, options) -> returns job id
  - POST /api/generate/world
  - POST /api/generate/story
- Implement synchronous MVP handlers that call `LMStudioClient` to request structured JSON outputs and persist to DB.
- Acceptance:
  - Endpoint returns 200 + saved `structured_data` id and basic validation (contains keys: name, appearance, summary).

Phase 2 — Portrait generation (1-2 days)

- Add image generation pipeline (backend) that accepts structured appearance and calls SD service (local WebUI or provider). Store image_base64 or URL in DB and return link.
- Harden SD client to accept multiple response shapes (image_base64, files, URLs).
- Add retry/backoff and sanitize image sizes.

Phase 3 — Frontend generator UI (2-3 days)

- Add pages/components for Character Builder, World Builder, Story Generator.
- Character flow:
  - Form for prompts/options -> POST /api/generate/character -> show preview -> request portrait -> review UI (NamePicker + appearance: skin/eyes/hair)
- Add dev-only deterministic hook: `?e2e_mocks=1` to return deterministic `generatedContent` for Playwright tests.

Phase 4 — Testing & E2E determinism (2-4 days)

- Unit tests (Vitest) for frontend components: NamePicker, PortraitReview, StoryPreview.
- Backend pytest unit tests for LM client and generate endpoints (mock LM & SD responses).
- Playwright E2E tests covering generate -> portrait -> review using `?e2e_mocks=1` and deterministic mocks for LM/SD.

Phase 5 — Orchestrator-driven implementation (ongoing)

- Use `scripts/feedback_loop_normalized.py` as the canonical planner. The orchestrator (`scripts/feedback_orchestrator.py`) should:
  - Build a normalized summary including failing tests, open tasks, and sample structured_data.
  - Call `feedback_loop_normalized.py` (or shell out to it) and save planner outputs to `.feedback/audit/`.
  - Create small actionable tasks (files_to_edit) and propose low-risk commands to run (unit tests, lint) in commands[].
- Human reviews audit output and uses `scripts/executor.py --approve` to run safe commands.

Data shapes (examples)

- Character structured_data (stored in DB JSON column):

```json
{
  "name": "Mira Taldin",
  "summary": "A wandering scholar from the coastal city of Eral",
  "appearance": {
    "skin": "olive",
    "eyes": "hazel",
    "hair": "dark brown",
    "height": "5'7"
  },
  "background": { "origin": "Eral", "skills": ["lore", "alchemy"] }
}
```

- LM planner response (must follow schema):

```json
{
  "next_action": "Add backend endpoint /api/generate/character and tests",
  "rationale": "Enables programmatic character generation for UI",
  "commands": ["cd backend && pytest -q"],
  "files_to_edit": [
    {
      "path": "backend/main.py",
      "change_description": "add /api/generate/character POST endpoint"
    }
  ],
  "risk": "low"
}
```

Testing strategy (must be automated)

- Backend: pytest for unit tests (LM client mock, SD client mock, DB persistence). Keep tests small & fast.
- Frontend: Vitest + React Testing Library. Add tests for NamePicker merged suggestions, MapClusterGroup behavior, and StoryPreview.
- E2E: Playwright tests using `?e2e_mocks=1` to enable deterministic flows; mock LM/SD responses for CI.

CI & orchestration

- CI workflow should run unit tests (backend + frontend) first, then run the orchestrator in dry-run and upload the planner JSON as an artifact for human review.
- Playwright E2E can be optional in CI (run on schedule or PRs with `e2e_mocks=1`).

Audit & safety

- All LM calls must be recorded to `.feedback/audit/` with raw and parsed outputs (UTC timestamped filenames).
- `scripts/executor.py` manages approved runs; default dry-run; `--approve` executes whitelisted commands only.
- Add token/cost logging in orchestrator and an optional daily quota guard.

How the feedback loop will drive work

- The orchestrator runs periodically or via CLI. It asks the LM for a single next action using `feedback_loop_normalized.py` and writes outputs to `.feedback/audit/`.
- Human inspects the recommended action. If low-risk commands are proposed, human may call `executor.py --approve` to run them. If files_to_edit are suggested, the orchestrator can prepare patches and open draft PRs for human review.

Acceptance Criteria for initial milestone (end of Sprint 1)

- Backend endpoints `/api/generate/character` exists and returns valid JSON for a sample prompt.
- Frontend Character Builder page exists with a generate -> preview -> review flow; unit tests covering NamePicker and PortraitReview added.
- Playwright E2E test runs in dry-run mode using deterministic mocks and passes locally.
- Orchestrator can call `feedback_loop_normalized.py` and write audit outputs to `.feedback/audit/`.

Run & test commands (dev)

```powershell
# Root install
npm install

# Frontend
cd frontend
npm install
npm run dev        # run frontend
npm run test:unit  # run Vitest

# Backend
cd ..\backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pytest -q

# Orchestrator (dry-run)
cd ..\scripts
python .\feedback_loop_normalized.py
```

Notes & next steps

- Start small: implement backend generate endpoints and backend tests first.
- Keep LM planner calls auditable and limited to the canonical script.
- After the initial milestone, iterate by adding SD generation, image storage, E2E tests, and CI automation.
