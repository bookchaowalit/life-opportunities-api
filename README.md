# opportunities

The Opportunities cell: its own API (Railway, serverless) and its own Neon
database, described by `cell.yaml` and served by the code in `src/cellkit/`, which
this repository owns. It
reuses empire-platform for identity, authorization, executions and audit over
HTTP with the caller's token.

| | |
|---|---|
| API | Railway project `opportunities`, service `opportunities-api` (Serverless) |
| Data | Neon project `opportunities`, database `opportunities` |
| Registry | solo-empire `repository-catalog/registries/online-systems.yaml` (`opportunities`) |

## API

Every resource has list, stats, get, get-by-legacy-id, create, patch and delete
(see `cellkit/app.py`). Permissions are `opportunities.<resource>:read|write|delete`.

| Path | Resource | Filters |
|---|---|---|
| `/v1/opportunities` | opportunity | `type`, `status`, `window_status` |
| `/v1/opportunity-actions` | opportunity-action | `category`, `action` |

## Develop and operate

```bash
uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/pytest -q
NEON_API_KEY=... .venv/bin/opportunities-db provision
npm install && railway config apply && railway up --ci --service opportunities-api
railway scale --service opportunities-api asia-southeast1-eqsg3a=1 us-east4-eqdc4a=0   # next to Neon and the platform
```

Railway variables: `OPPORTUNITIES_DB_MODE=hosted`, `OPPORTUNITIES_DB_URL_API`,
`OPPORTUNITIES_JWT_PUBLIC_KEY_PEM`, `OPPORTUNITIES_JWT_ISSUER`, `EMPIRE_PLATFORM_URL`.
