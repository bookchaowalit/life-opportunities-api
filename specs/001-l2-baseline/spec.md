# SPEC-001 — L2 baseline: locked dependencies, strict types, domain rules under test

Standard: ADR-0004 — TDD + SDD (architecture-docs, `docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md`).
Big Loop Plan Wave 2 (solo-empire `repository-catalog/roadmaps/BIG-LOOP-PLAN-2026-10-21.md`).

## Document control

| Field | Value |
|---|---|
| Spec ID / version | SPEC-001 / 1.0 |
| Status | in review (implemented; owner approval pending) |
| Repository / path | bookchaowalit/life-opportunities-api / `specs/001-l2-baseline/spec.md` |
| Owner (maker) | Claude Code (Wave 2 cells session) |
| Reviewer (checker) | Fresh Claude reviewer session (no maker context) |
| Approver | Owner (bookchaowalit): pending, see the Wave 2 report owner actions |
| Requirement links | Big Loop DoD L2: `PRODUCT.md`, ≥ 3 test files, Sentry, type check; L1 lockfile |
| Main-only | yes: committed straight to `main`, so the red run is local (ADR-0004 rule 2, v1.1) |
| Created / approved | 2026-10-22 / pending owner |

## 1. Problem and intent

- **Problem:** Dependencies were installed unpinned, there was no type check, and the only tests were the generic contract suite; none of this cell's own rules (required names and URLs, fixed enums, whole-number scores, defaults) were tested.
- **Outcome:** the image installs exactly `uv.lock` (`uv sync --frozen`), CI runs Ruff, mypy
  (strict on `src/`) and a coverage gate on shared CI v1.1.1, and the cell's own rules have
  tests of their own beyond the generic contract suite.
- **Why now:** Wave 2 of the Big Loop Plan; milestone M1 is 2026-11-15.

## 2. Scope

| In scope | Out of scope (non-goals) |
|---|---|
| `uv.lock`, Dockerfile, CI caller bump, Ruff/mypy config and fixes, domain tests, `PRODUCT.md` | New endpoints or fields; database migrations; a shared cellkit package (owner decision 2026-10-21: each service owns its code) |

## 3. Behaviour — scenarios

### AC-01 — An opportunity needs a non-empty name

- **Given** an owner with write permission
- **When** they create an opportunity without a name, with an empty name, or clear the name on update
- **Then** the API answers 422 and the stored name is unchanged
- **Test:** `tests/test_opportunity_validation.py::test_the_name_cannot_be_cleared_on_update` · level: integration (API + throwaway PostgreSQL)

### AC-02 — Type, status and window are fixed lists

- **Given** a create request for an opportunity
- **When** `type`, `status` or `window_status` is a value outside its list
- **Then** the API answers 422; every listed value is accepted
- **Test:** `tests/test_opportunity_validation.py::test_type_must_be_a_known_kind` · level: integration (API + throwaway PostgreSQL)

### AC-03 — Levels and tier are whole numbers

- **Given** a create request for an opportunity
- **When** a level, `tier` or `estimated_window_months` is text or a fraction
- **Then** the API answers 422; `total_score` accepts a decimal
- **Test:** `tests/test_opportunity_validation.py::test_scores_and_levels_must_be_numbers` · level: integration (API + throwaway PostgreSQL)

### AC-04 — A new opportunity starts as researching and unscored

- **Given** a create request with only a name
- **When** the opportunity is created
- **Then** `status` is researching, type, window and scores are empty and `version` is 1
- **Test:** `tests/test_opportunity_defaults.py::test_new_opportunity_starts_as_researching_with_nothing_scored` · level: integration (API + throwaway PostgreSQL)

### AC-05 — A new action is monitored with no revenue

- **Given** a create request with only a URL
- **When** the action is created
- **Then** `action` is monitor and both revenue fields are 0; the same URL can be recorded twice
- **Test:** `tests/test_opportunity_defaults.py::test_new_action_is_monitored_with_no_revenue` · level: integration (API + throwaway PostgreSQL)

### AC-06 — Opportunities list and group by declared filters

- **Given** opportunities of several types, statuses and windows
- **When** the owner lists by filter and asks for stats by each filter or by `tier`
- **Then** matching opportunities are listed, stats count per value, and grouping by `tier` is refused with 422
- **Test:** `tests/test_opportunity_queries.py::test_stats_count_opportunities_per_status_type_and_window` · level: integration (API + throwaway PostgreSQL)

### AC-07 — Scoring bumps the version once

- **Given** an unscored opportunity
- **When** the owner patches its levels and score, then repeats the same patch
- **Then** the first patch makes version 2 and the repeat keeps it at 2
- **Test:** `tests/test_opportunity_queries.py::test_scoring_an_opportunity_bumps_the_version_once` · level: integration (API + throwaway PostgreSQL)

### AC-08 — Numbers fit their columns

- **Given** an int field (PostgreSQL integer) or a real field
- **When** a client sends 2**31, or NaN / Infinity / 1e400 as raw JSON
- **Then** the API answers 422 naming the field (before: a 500 from PostgreSQL, or the value silently stored as null)
- **Test:** `tests/test_contract.py::test_numbers_fit_their_columns` · level: integration (API + throwaway PostgreSQL)

## 4. Interfaces and data

| Interface | Change | Contract |
|---|---|---|
| `/v1/*` (all resources) | unchanged | same routes and payloads; see README |

- **Data model / migration:** N/A — no schema change. Range rules are checked by the API on
  create and update; rows already stored are not rewritten.
- **Backward compatibility:** clients keep the same routes. A write that would store a range
  ending before it starts now gets `422 invalid_value` instead of `201/200`.

## 5. Non-functional requirements

| NFR | Target | How it is tested |
|---|---|---|
| Performance | N/A — no hot-path change beyond one comparison per declared range | — |
| Security / privacy | Same authorization, RLS and Sentry scrubbing as before | contract suite (`tests/test_contract.py`), `tests/test_sentry.py` |
| Reliability / observability | Reproducible image from `uv.lock`; failed inline publishes reach Sentry | image rehearsal before push; `test_inline_publish_failure_is_reported` |
| Accessibility / UX | N/A — API only | — |

## 6. Test plan (TDD)

- **Test levels:** integration tests against the FastAPI app with a throwaway local PostgreSQL
  (pgserver) and a fake platform; no hosted database or platform.
- **Test data:** generated in each test; no production data.
- **Coverage:** CI gate `coverage-threshold: "55"` (measured 57.07% on 2026-10-22, minus 2 points).
- **Not test-first (exceptions):** tests that pin behaviour the service already had
  (characterization tests, marked below) were written after the code by nature; tooling and
  config changes are covered by CI itself.

### Red / green log

| Scenario | Test | Red: commit / run + failure message | Green: commit / run | Refactor note |
|---|---|---|---|---|
| AC-01 | `tests/test_opportunity_validation.py::test_the_name_cannot_be_cleared_on_update` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-02 | `tests/test_opportunity_validation.py::test_type_must_be_a_known_kind` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-03 | `tests/test_opportunity_validation.py::test_scores_and_levels_must_be_numbers` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-04 | `tests/test_opportunity_defaults.py::test_new_opportunity_starts_as_researching_with_nothing_scored` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-05 | `tests/test_opportunity_defaults.py::test_new_action_is_monitored_with_no_revenue` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-06 | `tests/test_opportunity_queries.py::test_stats_count_opportunities_per_status_type_and_window` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-07 | `tests/test_opportunity_queries.py::test_scoring_an_opportunity_bumps_the_version_once` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-08 | `tests/test_contract.py::test_numbers_fit_their_columns` | 0e58ba4 · `.venv/bin/pytest -q -k numbers_fit` · `psycopg.errors.NumericValueOutOfRange: integer out of range` | CI run of the pushed tip | none |

## 7. Risks and open questions

| # | Risk or question | Impact | Owner | Resolution / date |
|---|---|---|---|---|
| 1 | Stored rows written before a range rule existed may already be inverted | a patch touching one of those dates is refused until both are fixed | owner | patches that do not touch the range still work |

## 8. Change log

| Version | Date | Change | Scenarios affected | Approved by |
|---|---|---|---|---|
| 1.0 | 2026-10-22 | Implemented with the Wave 2 baseline | all | pending owner |

## Approval

| Gate | Role | Name / date | Decision | Evidence |
|---|---|---|---|---|
| Implemented (DoD) | Reviewer (checker) | Fresh Claude reviewer / 2026-10-22 | see Wave 2 report | CI run of the pushed tip |
| Implemented (DoD) | Approver | Owner | pending | Wave 2 report |
