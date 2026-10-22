# Product

<!-- impeccable:product-schema 1 -->

## Platform

api

## Users

- The Solo Empire owner, through the cell's own MCP server (`opportunities-mcp`) and the hosted
  tool hub (`platform-mcp-remote-worker`, which lists this service's host in its allow-list).
- Local tooling that reads the cell through `EMPIRE_OPPORTUNITIES_API`: `ops-toolkit`
  (`cell_store.py`) and `mcp-aggregator` (`cell-store.ts`), as recorded in the online-systems
  registry. The registry notes that the CRM's Frappe Lead projection still reads the old SQLite
  opportunities tables, not this cell.
- Automations with an `empire-platform` token (for example `owner-mcp`), within the permissions
  `opportunities.opportunity:read|write|delete` and
  `opportunities.opportunity-action:read|write|delete`.
- A web page that shows opportunities: [ต้องยืนยัน].

## Product Purpose

A list of business opportunities the owner is researching, each with a type, a status, seven
scored levels (pain, budget, frequency, AI leverage, competition, distribution, fit), a total
score and an estimate of how long the market window stays open; and a list of opportunity actions,
which are sightings (a URL with a trend score) marked act on, skip or monitor with expected and
actual revenue.

Success: each opportunity under review is recorded once with its score and status, and every
sighting that was acted on shows the revenue it brought.

## Positioning

One capability, one service: its own API (Railway, serverless), its own database (Neon) with
row-level security per workspace, and authorization, executions and audit through
`empire-platform`. It is workspace-scoped, so the same service can serve other tenants without
code changes. It has no publisher and emits no graph events.

## Operating Context

- Production: `https://opportunities-api-production.up.railway.app` (`/health`), deployed by
  merging to `main` after CI.
- The cell started empty (the domain had no rows when it left the control plane on 2026-10-11);
  imports keep old ids in `legacy_id`.
- Monitored by `platform-uptime-worker` (target `opportunities-api`); errors go to Sentry without
  personal data.

## Capabilities and Constraints

- `/v1/opportunities` (filters `type`, `status`, `window_status`) and `/v1/opportunity-actions`
  (filters `category`, `action`): list, stats (grouped by a filter only), get, get-by-legacy-id,
  create (with `Idempotency-Key`), patch (with `expected_version`), delete.
- Opportunity rules: `name` is required and cannot be empty; `type` (ai_automation, saas,
  service, content, consulting, product, other), `status` (researching, validating, active,
  paused, killed, completed) and `window_status` (opening, open, narrowing, closed) are fixed
  enums; `status` defaults to researching; `tier`, the seven levels and
  `estimated_window_months` are whole numbers and `total_score` a decimal number. No range is
  enforced on levels, tier or score, and the total is not computed from the levels.
- Action rules: `url` is required and cannot be empty; `action` is act_on, skip or monitor and
  defaults to monitor; `revenue_actual` and `revenue_expected` default to 0.
- No uniqueness rules: opportunities may share a name and the same URL may be recorded twice. An
  import with a `legacy_id` already used is refused with 409.
- Unknown fields are refused (422); an unchanged patch keeps the version.
- Out of scope: scoring or ranking opportunities, fetching the URLs, and the CRM lead projection.

## Measures

Proposed, nothing collects them yet:

- Opportunities by status (stats grouped by `status`).
- Share of actions marked act_on that have a non-zero `revenue_actual`.
- 5xx rate and p95 latency on `/v1/opportunities` (Sentry and uptime worker).
