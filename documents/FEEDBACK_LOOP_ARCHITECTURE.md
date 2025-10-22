# Feedback Loop Architecture & Implementation Plan

## Goal

Create a robust, safe, and auditable automated feedback loop driven by your LM Studio instance that iteratively guides development and testing of Storycraft.
The system will let an LM (via LM Studio) recommend the single next action, allow human approvals, run low-risk commands automatically, and progressively build tests, CI workflows, and automation to support fully automated story/DnD campaign generation pipelines.

## High-level objectives

- Make development decisions and next steps reproducible and auditable.
- Keep human-in-the-loop for any code-changing or high-risk actions.
- Automate low-risk operations (linters, unit tests, E2E tests) under explicit approval.
- Provide a safe path to create PRs with LM-suggested patches (drafts only, require human review before merging).
- Build a modular architecture so components can be replaced (e.g., LM providers).

## Architecture overview

Components:

1. Collector

   - Gathers normalized context for the LM: recent commits, open tasks, failing tests, CI status, runtime logs, and key artifacts (last portrait, sample structured_data).
   - Outputs a compact JSON summary used by the planner.

2. Planner (LM Studio)

   - Receives normalized summaries and returns a single, structured next action in JSON (keys: next_action, rationale, commands[], files_to_edit[], risk).
   - Uses system prompts enforcing JSON-only responses and strict schema.

3. Approver (Human or Policy Bot)

   - Gate that inspects LM output and decides to (a) auto-execute low-risk commands, (b) create a draft PR with suggested edits, or (c) request clarification.
   - Requires explicit approval for medium/high risk tasks.

4. Executor

   - Safely executes approved commands locally in an isolated environment; supports dry-run, logging, timeout, and resource limits.
   - Generates artifacts (test results, patches) for reporting back to the LM.

5. Reporter

   - Collects results (stdout, test results, diff/patch) and feeds them back to the LM for the next iteration.

6. CI Integration

   - Runs feedback loop in CI for PRs (read-only by default). A CI job can run the Planner to produce suggestions and then open a draft PR; merging remains manual.

7. Observability & Cost Control
   - Tracks LM usage per-call (tokens, estimated cost), call frequency, failures and latency.

## Security & Safety

- Secrets: LM Studio URL and credentials stored in environment variables or a secrets manager; never logged.
- Approval gates: by default, the loop runs in read-only/dry-run mode until a human explicitly sets an `APPROVE=true` environment variable or uses the CLI `--approve` flag.
- Low-risk classification: only run commands the project owner has explicitly labeled "safe" (lint, tests, formatters) without approval.
- Audit logging: every suggestion, approval decision, command output, and generated patch is written to a local audit directory.

## Data shapes and interfaces

- Normalized summary (example):
  {
  "project": "storycraft",
  "branch": "sd-integration",
  "recent_changes": ["..."],
  "open_tasks": ["..."],
  "failing_tests": [{"name":"...","error":"..."}],
  "sample_artifacts": {"last_portrait":"scripts/last_portrait.png"}
  }

- Planner response (schema enforced):
  {
  "next_action": "string",
  "rationale": "string",
  "commands": ["string"],
  "files_to_edit": [{"path":"string","change_description":"string"}],
  "risk": "low|medium|high"
  }

## Development roadmap (phased)

Phase 0 — Preparation (0.5 day)

- Create plan doc (this file).
- Ensure LM client util exists and works (we added `scripts/lm_studio_client.py`).
- Acceptance: plan checked in and LM client passes a probe call.

Phase 1 — Minimal feedback loop & safe executor (1-2 days)

- Implement `orchestrator.py` that:
  - builds the normalized summary (collector),
  - asks LM Studio via `feedback_loop_normalized.py` (or calls LM client directly),
  - writes response to `./.feedback/audit/`.
- Implement `executor` with dry-run and `--approve` flag to run low-risk commands
  (lint, unit tests). Support `--simulate` mode that returns what would have been run.
- Unit tests: test orchestrator dry-run, executor dry-run.
- Acceptance: run orchestrator -> LM suggests next step -> executor dry-run produces predictable outputs.

Phase 2 — Patch generation & PR creation (1-2 days)

- LM suggests file edits (change_description) -> orchestrator prepares a patch file and opens a draft PR via GitHub API (requires token). The PR body is the LM-provided rationale + tests to run.
- Add labels and reviewers.
- Acceptance: PR created in draft state; tests are executed on the PR via CI.

Phase 3 — CI integration & schedule (2 days)

- Add a GitHub Action that runs the feedback loop on a schedule or on PRs and posts suggestions as PR comments.
- Ensure that any auto-execution in CI is read-only; only creates PR drafts.
- Acceptance: Feedback loop job runs and creates a draft PR or comment.

Phase 4 — E2E automation for story creation (3-5 days)

- Implement test harness and fixtures: headless browsers, mocked LM responses for deterministic runs, and mocked SD responses.
- Add a `generate_story_pipeline.py` orchestrator that runs the LM-based generator -> SD portrait generation -> persistence -> review loop.
- Acceptance: End-to-end pipeline can generate a story + portrait and store it as a character in the DB under test mode.

Phase 5 — Monitoring, metrics, and guardrails (1-2 days)

- Add token/cost logging, error alerts and a dashboard (simple JSON log + scripted report).
- Implement rate-limiting per provider and per workspace.
- Acceptance: logs capture LM calls and cost estimates; rate-limits enforced in orchestrator.

## Testing strategy

- Unit tests for clients and small utilities (pytest for backend). Add tests for:
  - LM client retries and timeout
  - JSON parsing of LM responses
  - Executor dry-run semantics
- Integration tests:
  - Playwright E2E for create->review (we added test scaffold)
  - A backend pytest that mocks LM and SD responses to confirm structured_data persistence
- CI: run unit tests, lint, then optionally run Playwright tests against a deployed preview environment.

## Operational notes

- Default mode: dry-run / read-only. Use `--approve` only when explicitly intended.
- Audit: `.feedback/audit/` will contain timestamped planner responses and executor outputs.
- Secrets: `LM_STUDIO_URL` and `LM_MODEL` should be set for LM access.

## Immediate next actions (this sprint)

1. Commit this plan to the repo (done now).
2. Implement orchestrator CLI `scripts/feedback_orchestrator.py` that calls `feedback_loop_normalized.py` and writes the plan into `.feedback/audit/`.
3. Implement executor: add `--approve` flag to `feedback_loop_normalized.py` (or create `executor.py`) to execute low-risk commands (lint/test) in a sandbox with timeouts.
4. Run orchestrator -> LM -> executor dry-run cycle and capture outputs.

## Acceptance criteria for iteration

- Orchestrator returns LM-specified next action and writes it to the audit directory.
- Executor simulates (dry-run) and on `--approve` can run lint/test commands and record outputs.
- New unit tests cover the executor dry-run and LM JSON parsing.

## FAQs

Q: Will the LM be allowed to make commits/PR merges automatically?
A: Not by default. The system will create draft PRs or patches; merging requires explicit human approval.

Q: How to prevent cost overruns?
A: Add token usage logging and a soft quota per day/week. Alert if quota approaches limit.

## Appendix: Example orchestration flow

1. Collector builds normalized JSON.
2. Orchestrator sends it to LM Studio (Planner).
3. Planner replies with JSON specifying `commands`.
4. Approver approves low-risk commands (or denies).
5. Executor runs commands, writes outputs to `.feedback/audit/`.
6. Reporter sends outputs back as next iteration's input to Planner.

---

This plan is intentionally modular and incremental — we'll implement the orchestrator and safe executor next, run them in dry-run mode, and let LM Studio drive the prioritized next actions, while keeping human control for code changes.
