# Architecture Documentation

Reference documentation for the CRM platform — a clinical CRM/EMR for a
Hepatitis C and HIV testing program, plus the public my420.ca website that feeds
registrations into it.

## The documents

| Document | Covers |
|---|---|
| **[01 — Architecture Overview](./01-overview.md)** | Three levels of zoom: the multi-tenant [deployment topology](./01-overview.md#deployment-topology), then a single instance's external actors, then the containers inside it. Plus which datastore owns what, how a request travels from browser to database, and the build-time flags that change the shape of a deployment. **Start here.** |
| **[02 — Module Diagram](./02-modules.md)** | The code map. Eight backend routers and the layering convention they share, the shared `app/common/` layer, the frontend's context nesting and route tree, and the three separate authentication identities the system supports. |
| **[03 — Database Schema](./03-database.md)** | Full Postgres reference: entity diagrams plus every table, column, type, default, constraint, index and trigger — as the schema stands after all migrations, not as the `CREATE TABLE`s read. |

## A few things worth knowing up front

- **Every organisation gets its own isolated instance** — own VPS, domain,
  database and object storage. Only Vault and the monitoring stack are shared.
  See [deployment topology](./01-overview.md#deployment-topology).
- **Postgres is the system of record.** MongoDB is present but holds only
  analytics spreadsheet uploads. Redis holds nothing durable. See the
  [datastore ownership table](./01-overview.md#datastore-ownership).
- **There is no ORM.** Every query is hand-written SQL through asyncpg.
- **One repository builds two websites** — the CRM and the public marketing
  site — selected by `VITE_IS_MY420` at build time.
- **The same flag reaches the database**, deciding whether seeded reference data
  survives a fresh install. See
  [clean slate](./03-database.md#clean-slate-on-non-my420-deployments).

## About the diagrams

Diagrams are written in [Mermaid](https://mermaid.js.org/) inside the Markdown —
GitHub, VS Code and most Markdown viewers render them automatically. To change a
picture, edit the text in the fenced ` ```mermaid ` block; there is no separate
drawing file and no image to regenerate.

That is the whole reason for the choice: a diagram you can fix in one line
during the same commit that changed the code is a diagram that stays true.

## Keeping this current

These docs go stale silently unless updated alongside the change that
invalidates them. Concrete triggers:

| When you… | Update |
|---|---|
| Add or remove a router in `backend/app/core/` | [02 — Module Diagram](./02-modules.md), the module map and table |
| Add a file to `db/migrations/` | [03 — Database Schema](./03-database.md), the affected table and the history section |
| Add a context provider or a top-level route in `frontend/src/` | [02 — Module Diagram](./02-modules.md), provider composition and route tree |
| Add or swap a datastore, or change the Caddy routing | [01 — Architecture Overview](./01-overview.md), the container diagram and ownership table |
| Change an authentication flow | [02 — Module Diagram](./02-modules.md), the authentication section |

For schema changes, verify against a live database rather than trusting a read
of the migration files — the final schema is the product of migrations that
alter each other:

```bash
docker compose -f compose.dev.yml --profile db up -d
docker compose -f compose.dev.yml exec postgres-dev \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\d+ patients'
```

## Known gaps

Deliberately not covered in this pass:

- **Deployment mechanics** — the fleet topology, tenant identity, TLS
  authorities and the rotation loop *are* covered in
  [deployment topology](./01-overview.md#deployment-topology). What is not:
  the full Compose profile matrix, per-service resource limits, and the GitHub
  Actions test and deploy workflows.
- **Authorisation in depth** — roles, the `permissions` array, and
  location-scoped access are described where they appear, but there is no single
  document tracing the whole model.
- **Sequence diagrams for key flows** — public registration becoming a patient
  record, document upload and retrieval, and the analytics query loop are
  described in prose rather than stepped through.

## Outdated material elsewhere in the repo

Two artifacts predate the current architecture and will mislead you:

- **`.emergent/summary.txt`** — describes the app as React + FastAPI + MongoDB
  with PIN-based 2FA. The system of record has since moved to Postgres.
- **`assets/system_diagram.png`** — shows Nginx reverse proxies. Nginx was
  replaced by Caddy in commit `97201b7`; the `nginx/` directory is likewise
  legacy. Its multi-tenant picture is otherwise still accurate and has been
  redrawn, current, as
  [deployment topology](./01-overview.md#deployment-topology).

Neither file has been changed as part of writing these docs — the PNG can be
deleted once you are happy the Mermaid version replaces it.
