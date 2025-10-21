# StoryCraft Feature Set Roadmap

This document outlines a prioritized, industry-standard feature set to significantly improve the story generation experience in StoryCraft. It covers feature descriptions, API contracts, data shapes, acceptance criteria, rollout plans, testing strategy (deferred unit tests until wiring complete), and monitoring.

## Goals

- Make story generation robust across providers and models.
- Improve reproducibility and editing workflows for worlds, characters, and portraits.
- Provide safe fallbacks and clear telemetry for structured-output generation.
- Deliver a polished frontend experience for creating, reviewing, and exporting generated content.

## High-Level Priorities (MVP → Extended)

1. Structured Generation Stability (MVP)
   - Expand model capability registry and wire checks across all LLM call-sites.
   - Improve reactive fallback heuristics and add an audit log for fallback occurrences.
   - Add server-side validation and normalization of structured outputs against Pydantic schemas.
2. Storycraft Orchestration (MVP)
   - Implement a generation orchestrator that composes worlds, characters, and scenes with a single request and returns a strongly-typed package.
   - Include generation metadata: provider, model, tokens_estimate, response_mode (native/prompt-fallback), and generation warnings.
3. Portrait Pipeline Robustness (MVP)
   - Harden SD client with permission/quota handling, quarantined placeholder images, and async image generation status endpoints.
   - Add image metadata and storage references (S3/local) with clear cleanup/mirroring strategies.
4. UX Improvements (MVP)
   - Worlds and Characters pages: inline story/portrait generation controls, progress indicators, and result preview modals.
   - Structured data badges and quick-edit for generated structured data.
5. Export & Import (Extended)
   - Export stories/worlds/characters to JSON/Markdown/YAML and import tooling for sharing between users.
6. Observability & Telemetry (MVP)
   - Telemetry events for generation requests, fallback triggers, provider errors, and image generation failures.
   - Basic dashboard (logs & counts) for fallback rates and provider failure rates.

## Detailed Feature Specs

### 1) Structured Generation Stability

Description

- Prevent provider errors by proactively checking model capabilities and by falling back to prompt-based structured generation when needed.
- Keep an audit trail of when native structured output was used vs when fallback was used.

API Contracts

- call_llm_structured(provider, model, prompt, schema_model, options) -> { success: bool, mode: 'native'|'prompt_fallback', parsed: dict|null, raw: str, provider_meta: {...}, error: str|null }

Data Shapes

- schema_model: Pydantic model class used to generate JSON schema.
- parsed: Python dict conforming to schema_model on success.

Acceptance Criteria

- No provider 400 errors observed in standard generation flows when provider/model mapping is known.
- Fallback rate < 5% for supported models in staging.

Rollout

- Stage behind a feature flag `structured_guarding=true` and monitor.

### 2) Storycraft Orchestrator

Description

- Single endpoint `/api/generate/story/full-generate/` that composes a world, N characters, and a story package.
- Orchestrator should call call_llm_structured for each piece and handle images via SD client.

Request contract (POST)

- body: { world_themes?: string[], character_count?: int (1-6), tone?: string, seed?: string|null }

Response contract (200)

- { world: {...}, characters: [...], story: { content: str, scenes: [...] }, meta: { provider, model, mode, tokens_estimate, warnings: [...] } }

Acceptance Criteria

- Orchestrator returns at least a minimal, schema-valid package even if some image generations fail.
- All structured fields validated against Pydantic schemas.

### 3) Portrait Pipeline

Description

- Image generation should be async for heavy runs; store base64 or remote reference.
- Provide endpoints: POST `/api/portraits/generate/` -> job id, GET `/api/portraits/{job_id}/status/` and GET `/api/portraits/{job_id}/result/`.

Failure Modes

- PermissionError / 403 from SD -> store transparent 1x1 PNG placeholder with `error: 'permission'` metadata.
- Quota exhausted -> `error: 'quota'` and retry policy (exponential backoff + alert).

Acceptance Criteria

- Portrait requests do not block orchestrator success; skippable with placeholders.

### 4) UX Improvements

Worlds and Characters

- Add inline 'Generate' and 'Regenerate' controls; show progress and final structured data.
- Provide 'Accept & Save' and 'Save Draft' flows.

Structured Data Editor

- Allow editing parsed structured fields (forms auto-generated from schema) before saving to DB.

Accessibility

- Keyboard nav, ARIA labels for dialogs and progress indicators.

Acceptance Criteria

- Frontend displays generation progress, errors, and allows editing structured data before save.

### 5) Export & Import

Formats

- JSON, JSON-LD, markdown (with frontmatter), and simple YAML.

Use Cases

- Share generated worlds between team members, import into other projects.

Acceptance Criteria

- Round-trip: export → import → validate against Pydantic schemas.

### 6) Observability & Telemetry

Events to record

- generation.request (provider, model, requested_schema, timestamp)
- generation.result (success, mode, tokens, latency, warnings)
- generation.fallback (reason, provider_message)
- image.generation.status (job_id, status, error)

Storage

- Minimal file-based or DB-backed event sink (deferred to implementation choice). Start with a local append-only audit folder `.feedback/` with time-stamped JSON files for planner/audit and optionally telemetry.

Acceptance Criteria

- Dashboard/logs can show fallback counts per model and provider.

## Testing Strategy (deferred unit tests)

- Unit tests will be written after wiring front + backend features end-to-end.
- Tests to include: structured parsing happy path + fallback, orchestrator happy path + partial failures, portrait job lifecycle, and frontend E2E (Playwright) for generation workflows.

## Implementation Plan & Timeline (iterative)

1. Week 0: Agreement & scaffolding
   - Add `FEATURE_SET_ROADMAP.md` (this file)
   - Create feature flags and a small audit logging helper `.feedback/audit/`
2. Week 1: Structured stability & orchestrator core
   - Expand registry and wire capability checks (done partially)
   - Implement call_llm_structured contract and ensure server-side validation
   - Implement orchestrator endpoint (`/api/generate/story/full-generate/`) to return schema-validated package
3. Week 2: Portrait async pipeline
   - Add job endpoints and storage references
   - Wire images into orchestrator with placeholder behavior on failures
4. Week 3: Frontend UX polish
   - Integrate generation controls into Worlds & Characters pages
   - Structured-data quick edit UI
5. Week 4: Export/import + telemetry
   - Add export endpoints and telemetry event sink
6. Week 5: Tests and E2E
   - Implement unit tests and Playwright E2E tests; flake/CI polish

## Migration & Backwards Compatibility

- Schema changes: use versioned schema names (e.g., CharacterV1) and store `schema_version` with saved structured data.
- For existing structured_data strings, add migration function to detect and coerce into latest schema when reading.

## Security & Safety

- Sanitize any prompt/template inputs containing user-supplied content.
- Avoid logging secrets (keys) in audit files.
- Respect provider safety constraints and expose clear error messages to frontend.

## Rollout & Feature Flags

- Gate orchestration behind `FEATURE_FULL_ORCHESTRATOR` and portrait async behind `FEATURE_PORTRAIT_JOBS` for staged rollout.

## Acceptance Criteria Checklist (summary)

- Structured param sends only when registry permits.
- Orchestrator returns schema-validated package even with image failures.
- Portrait generation returns job id and result endpoints; placeholders used when SD fails due to permission/quota.
- Frontend has controls to generate & accept structured results.
- Telemetry tracks fallback events.

---

Next steps (if you approve):

1. I will run the internal planner `scripts/feedback_loop_normalized.py` with an updated summary that references this roadmap and ask for the LM's recommended single next action.
2. Based on planner output, I will follow its recommendation and start implementing the next step autonomously, updating the todo list as I progress.

Please confirm that you want me to run the planner now and proceed to act on its suggested next action. (You can also ask for changes to the roadmap before I run the planner.)
