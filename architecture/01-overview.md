# Architecture Overview

> Part of the [architecture documentation](./README.md). See also
> [Module Diagram](./02-modules.md) and [Database Schema](./03-database.md).

## What this system is

A clinical CRM/EMR for a Hepatitis C and HIV testing and treatment program,
together with the public marketing website (my420.ca) that feeds registrations
into it.

Two distinct user-facing products are built from one repository:

- **The CRM** — an internal application for clinical staff. Patient records,
  assessments, medications, dispensing, notes, activities, interactions,
  document attachments, telehealth video sessions, and an AI analytics
  assistant.
- **The public site** — a marketing and intake website with service
  information, SEO landing pages, a contact form, and a registration form.

Both ship from the same React bundle; a build-time flag decides which one a
given deployment serves. See [Two sites, one bundle](#two-sites-one-bundle).

## Deployment topology

The widest view: this is a **multi-tenant fleet of single-tenant deployments**.

Each organisation gets its own isolated instance — its own VPS, its own domain,
its own database, its own object storage. Nothing is shared at the application
or data layer. What *is* shared are two central services: HashiCorp Vault for
secrets and certificate issuance, and a Loki/Prometheus pair for observability.

```mermaid
graph TB
    org1["Org 1 staff"]
    org2["Org 2 staff"]
    pub["Public visitors<br/>my420.ca"]

    net(("Internet"))

    subgraph i1["Org 1 instance — org1.example.com"]
        c1["<b>Caddy</b><br/>:443, ACME"]
        a1["Frontend + Backend"]
        d1[("Postgres · MinIO<br/>Redis · MongoDB")]
        va1["Vault agent"]
        al1["Alloy agent"]
        c1 --> a1 --> d1
    end

    subgraph i2["Org 2 instance — org2.example.com"]
        c2["<b>Caddy</b><br/>:443, ACME"]
        a2["Frontend + Backend"]
        d2[("Postgres · MinIO<br/>Redis · MongoDB")]
        va2["Vault agent"]
        al2["Alloy agent"]
        c2 --> a2 --> d2
    end

    more["Additional tenants…<br/><i>same stack, own domain</i>"]

    subgraph central["Central services"]
        vault["<b>HashiCorp Vault</b><br/>KV secrets per CLIENT_ID<br/>PKI root CA · AppRole auth"]
        obs["<b>Loki + Prometheus</b><br/>logs and metrics<br/>labelled by INSTANCE_NAME"]
    end

    org1 --> net
    org2 --> net
    pub --> net
    net --> c1
    net --> c2
    net --> more

    va1 -.->|"secrets + certs<br/>mTLS"| vault
    va2 -.->|"secrets + certs<br/>mTLS"| vault
    more -.-> vault

    al1 -.->|"logs + metrics<br/>mTLS"| obs
    al2 -.->|"logs + metrics<br/>mTLS"| obs
    more -.-> obs

    classDef actor fill:#e8f0fe,stroke:#4285f4,color:#111
    classDef edge fill:#e6f4ea,stroke:#34a853,color:#111
    classDef centralC fill:#fce8e6,stroke:#ea4335,color:#111
    class org1,org2,pub actor
    class c1,c2 edge
    class vault,obs centralC
```

### What makes an instance a tenant

Three environment variables turn an otherwise identical stack into a specific
organisation's deployment:

| Variable | Effect |
|---|---|
| `CLIENT_ID` | Selects the tenant's secret path in Vault — `secret/data/{CLIENT_ID}`. The Vault agent renders it to `/etc/vault/secrets/.env`, which every service reads. |
| `PKI_ROLE` | Selects the PKI role Vault issues internal certificates from — `pki/issue/{PKI_ROLE}`, common name `{HOSTNAME}.internal`, 720-hour TTL. |
| `INSTANCE_NAME` | Stamped as a label on every log line and metric, so the central Grafana can filter one tenant's data out of the shared stream. |

Plus `DOMAIN_ROOT` / `DOMAIN_NAME` for the public hostname, and `IS_MY420`,
which distinguishes the original my420.ca deployment from a new tenant — it
controls both the public marketing routes and whether seeded reference data
survives installation.

### Two kinds of TLS

Worth separating, because they come from different authorities:

```mermaid
graph LR
    le["Let's Encrypt"] -->|"public certs<br/>Caddy ACME, automatic"| pubtls["Browser ↔ Caddy"]
    vca["Vault PKI root CA"] -->|"internal certs<br/>720h, agent-renewed"| privtls["Backend ↔ Postgres<br/>Agent ↔ Loki/Prometheus"]
```

- **Public traffic** — Caddy obtains and renews Let's Encrypt certificates
  itself, with no certbot involved. The `caddy_data` volume persists them.
- **Internal traffic** — Vault's PKI engine issues short-lived certificates for
  service-to-service mTLS: the backend to Postgres, and the Alloy agent to the
  central Loki and Prometheus endpoints.

### Certificate and secret rotation

Rotation is push-driven rather than polled. When Vault re-renders a template,
the agent touches a trigger file; a small host daemon notices and restarts only
the affected Compose profile:

```mermaid
sequenceDiagram
    participant V as Vault
    participant A as Vault agent
    participant F as Trigger file
    participant W as Host watcher<br/>(systemd)
    participant S as Compose services

    V-->>A: secret or cert changes
    A->>A: re-render template
    A->>F: touch .secret-trigger<br/>or .cert-trigger
    loop every 5s
        W->>F: exists?
    end
    W->>F: delete
    W->>S: docker compose --profile<br/>secret-reload / cert-reload restart
```

The watcher scripts are installed onto the host as systemd units by a
privileged one-shot container — see `scripts/setup-watcher.sh`,
`scripts/secret-reload.sh`, and `scripts/cert-reload.sh`.

### Replaces the old diagram

This section supersedes `assets/system_diagram.png`, which shows the same
multi-tenant shape but with **Nginx** reverse proxies. Nginx was replaced by
Caddy in commit `97201b7`, and the certbot flow it implied is gone — Caddy
handles ACME natively.

## System context

Zooming into a **single instance**: who talks to it, and what it talks to.

```mermaid
graph TB
    staff["Clinical staff<br/><i>CRM users</i>"]
    public["Public visitors<br/><i>my420.ca</i>"]
    guest["Video guests<br/><i>patients, passcode join</i>"]
    viewer["Share-link recipients<br/><i>external, tokenised</i>"]

    system["<b>CRM Platform</b><br/>React SPA + FastAPI"]

    anthropic["Anthropic API<br/><i>analytics assistant</i>"]
    zoom["Zoom Video SDK<br/><i>telehealth sessions</i>"]
    gmaps["Google Places<br/><i>address autocomplete</i>"]
    smtp["SMTP<br/><i>transactional email</i>"]
    obs["Loki + Prometheus<br/><i>external monitoring host</i>"]

    staff --> system
    public --> system
    guest --> system
    viewer --> system

    system --> anthropic
    system --> zoom
    system --> gmaps
    system --> smtp
    system --> obs

    classDef actor fill:#e8f0fe,stroke:#4285f4,color:#111
    classDef core fill:#fff4e5,stroke:#f59e0b,stroke-width:2px,color:#111
    classDef ext fill:#f1f3f4,stroke:#9aa0a6,color:#111
    class staff,public,guest,viewer actor
    class system core
    class anthropic,zoom,gmaps,smtp,obs ext
```

Note there are **four** classes of caller, not one. Three of them are not
logged-in staff, and each has its own authentication path — see
[Three parallel auth identities](./02-modules.md#three-parallel-auth-identities).

## Containers

Zooming in one more level — the runtime pieces **inside a single instance** and
how a request moves between them.

```mermaid
graph TB
    browser["Browser"]

    subgraph edge["Edge"]
        caddy["<b>Caddy</b><br/>:80 / :443<br/>ACME TLS, gzip<br/>10MB body limit"]
    end

    subgraph app["Application"]
        spa["<b>React SPA</b><br/>static build<br/><i>frontend_dist volume</i>"]
        api["<b>FastAPI</b><br/>backend:8000<br/>uvicorn, Python 3.11"]
    end

    subgraph data["Data"]
        pg[("<b>Postgres 16</b><br/>system of record")]
        minio[("<b>MinIO</b><br/>photos, attachments")]
        redis[("<b>Redis 7</b><br/>ephemeral only")]
        mongo[("<b>MongoDB</b><br/>legacy_data only")]
    end

    browser -->|HTTPS| caddy
    caddy -->|"handle /*<br/>try_files → index.html"| spa
    caddy -->|"handle_path /api/*<br/>prefix stripped"| api

    api -->|asyncpg pool, mTLS| pg
    api -->|aioboto3 S3| minio
    api -->|redis.asyncio| redis
    api -->|motor| mongo

    classDef edgeC fill:#e6f4ea,stroke:#34a853,color:#111
    classDef appC fill:#fff4e5,stroke:#f59e0b,color:#111
    classDef dataC fill:#e8f0fe,stroke:#4285f4,color:#111
    class caddy edgeC
    class spa,api appC
    class pg,minio,redis,mongo dataC
```

**Caddy is the only ingress.** It publishes ports 80 and 443 and nothing else
is exposed publicly — in production only the MinIO console is additionally
published, and it is bound to `127.0.0.1:9001` so it is reachable only through
an SSH tunnel.

The routing split is the important detail:

| Caddy rule | Destination | Effect |
|---|---|---|
| `handle_path /api/*` | `http://backend:8000` | **Strips the `/api` prefix.** The backend never sees it, which is why FastAPI routes are declared as `/auth/...`, not `/api/auth/...` |
| `handle /*` | `/srv/react` | Static SPA with `try_files {path} /index.html` so client-side routes resolve |

Config lives in [`prod.caddy`](../prod.caddy) and [`dev.caddy`](../dev.caddy).
The `nginx/` directory and `assets/system_diagram.png` are leftovers from the
pre-Caddy setup and no longer describe production.

## Datastore ownership

Four datastores, with sharply different roles. Getting this wrong is the most
common misreading of this codebase, so it is worth stating plainly:

| Store | What it owns | Durability | Wired up in |
|---|---|---|---|
| **Postgres 16** | **System of record.** Auth and users, patients and every clinical child record, object metadata, reference data, website form submissions. 19 application tables. | Authoritative | [`storage/postgres.py`](../backend/app/common/storage/postgres.py) |
| **MinIO** | Binary blobs only — buckets `photos` and `attachments`. Object keys are mirrored into Postgres (`patient_photos.photo_key`, `attachments.file_key`), so Postgres remains the index. | Authoritative for file bytes | [`storage/minio.py`](../backend/app/common/storage/minio.py) |
| **Redis 7** | Ephemeral state only: AI chat history (capped at 10 messages, 20-minute TTL) and Zoom session metadata hashes keyed `session:metadata:{patient_id}`. | Disposable — nothing here survives a flush | [`storage/redis.py`](../backend/app/common/storage/redis.py) |
| **MongoDB** | One collection, `legacy_data` — spreadsheet uploads for the analytics assistant, one document per user. | Re-uploadable | [`storage/mongodb.py`](../backend/app/common/storage/mongodb.py) |

MongoDB is **not** the patient database. An older project summary
(`.emergent/summary.txt`) describes it as such; that has not been true since the
Postgres migration.

All four are opened as module-level singletons during the FastAPI `lifespan`
startup in [`main.py`](../backend/app/main.py) and closed in reverse order on
shutdown.

## Request lifecycle

A typical authenticated read, end to end:

```mermaid
sequenceDiagram
    participant B as Browser (SPA)
    participant C as Caddy
    participant R as FastAPI router
    participant S as Service layer
    participant P as Postgres

    B->>B: api.js interceptor:<br/>token expiring within 2 min?
    B->>C: GET /api/patients<br/>Authorization: Bearer …
    C->>R: GET /patients (prefix stripped)
    R->>R: get_current_user → decode JWT,<br/>require auth == true
    R->>S: PatientService.get_patients(...)
    S->>P: asyncpg, pooled connection
    P-->>S: rows
    S-->>R: pydantic models
    R-->>C: JSON
    C-->>B: JSON
    B->>B: apiCall() → { success, data }
```

Two credentials are in play, and they live in deliberately different places:

- **Access token** — a JWT held **in memory only**, in
  [`tokenManager.js`](../frontend/src/tokenManager.js). Never written to
  `localStorage` or `sessionStorage`, so it does not survive a page reload and
  is not reachable by injected script through storage APIs. Lifetime 30 minutes.
- **Refresh token** — an **httpOnly cookie** (`secure`, `SameSite=strict`), so
  JavaScript cannot read it at all. Lifetime 7 days. Every axios request sets
  `withCredentials = true` so the cookie rides along.

On boot and on tab focus the SPA calls `POST /auth/refresh` to exchange the
cookie for a fresh access token. The axios request interceptor refreshes
proactively when the current token is within 2 minutes of expiry, using a mutex
and a queue so concurrent requests block on a single in-flight refresh rather
than stampeding.

## Two sites, one bundle

One React codebase produces two different websites, chosen at **build time**:

```mermaid
graph LR
    src["frontend/src/routes.jsx"]
    flag{"VITE_IS_MY420"}
    my420["my420 marketing site<br/>src/my420/<br/>/, /about, /services,<br/>/register, /contact, …"]
    crm["CRM application<br/>src/crm/<br/>/crm/login, /crm/dashboard,<br/>/crm/file/:id, …"]

    src --> flag
    flag -->|"true"| my420
    flag -->|"false"| crm
```

The backend mirrors the same flag: `IS_MY420` gates whether the `/my420` router
(the public contact and registration endpoints) is mounted at all, in
[`main.py`](../backend/app/main.py). A CRM-only deployment simply does not have
those routes.

The flag reaches even the database — the `app.legacy_instance` Postgres setting
is derived from it and decides whether seeded reference data survives a fresh
install. See
[clean-slate behaviour](./03-database.md#clean-slate-on-non-my420-deployments).

### A second flag worth knowing about

`DEBUG` mounts [`backend/app/testing/`](../backend/app/testing/), a set of test
helper endpoints that return **raw verification tokens, password-reset tokens,
and MFA codes** in plain JSON, and can create pre-verified admin users. They
exist so integration tests can run without a mail server.

**This router must never be mounted in production.** `DEBUG` also enables
uvicorn's `reload`.

## Technology summary

| Layer | Technology | Version | Entry point |
|---|---|---|---|
| Edge | Caddy | latest | [`prod.caddy`](../prod.caddy) |
| Frontend | React + Vite | 18.2 / 7.x | [`frontend/src/main.jsx`](../frontend/src/main.jsx) |
| Routing | react-router-dom | 7.7 | [`frontend/src/routes.jsx`](../frontend/src/routes.jsx) |
| Styling | Tailwind CSS | 4.x | [`frontend/tailwind.config.js`](../frontend/tailwind.config.js) |
| Frontend state | React Context (7 providers) | — | [`frontend/src/context/`](../frontend/src/context/) |
| HTTP client | axios | 1.12 | [`frontend/src/services/api.js`](../frontend/src/services/api.js) |
| Backend | FastAPI + uvicorn | 0.115 / 0.30 | [`backend/app/main.py`](../backend/app/main.py) |
| Validation | pydantic | 2.7 | `schemas.py` per module |
| Runtime | Python | 3.11 | [`backend/Dockerfile`](../backend/Dockerfile) |
| Postgres driver | asyncpg | 0.30 | no ORM — hand-written SQL |
| Object storage | aioboto3 (S3 API) | 15.1 | [`storage/minio.py`](../backend/app/common/storage/minio.py) |
| Mongo driver | motor | 3.3 | [`storage/mongodb.py`](../backend/app/common/storage/mongodb.py) |
| LLM | Anthropic SDK | 0.64 | [`analytics/rag.py`](../backend/app/core/analytics/rag.py) |
| Video | Zoom Video SDK | 2.3 | [`context/ZoomContext.jsx`](../frontend/src/context/ZoomContext.jsx) |
| Migrations | dbmate | latest | [`db/migrations/`](../db/migrations/) |

There is **no ORM**. Every query is hand-written SQL executed through asyncpg
with `$1` placeholders. This is a deliberate, consistent choice across all
modules — see [the layering convention](./02-modules.md#the-layering-convention).

## Environments

Four Compose configurations, selected by profile rather than by separate stacks:

| Environment | File | Secrets | TLS | Frontend |
|---|---|---|---|---|
| Production | [`compose.yml`](../compose.yml) | Vault agent renders `/etc/vault/secrets/.env` | Caddy ACME (public), Vault PKI (internal mTLS) | Pre-built static, served by Caddy |
| Staging | [`compose.staging.yml`](../compose.staging.yml) | Same as production | Same as production | Same as production |
| Development | [`compose.dev.yml`](../compose.dev.yml) | Repository `.env` | mkcert certs in `./certs`, Caddy on `:80` | Vite dev server, proxied |
| Test | [`compose.test.yml`](../compose.test.yml) | Hardcoded inline values | None — plain HTTP | Vite in the test container |

Staging is topologically identical to production; the difference is memory
limits, sized for a much smaller VM.

Readiness is handled imperatively rather than with Compose healthchecks —
`scripts/wait-for-db.sh` polls `pg_isready`, `scripts/wait-for-backend.sh` polls
`/health`, and dbmate's `--wait` flag blocks until Postgres accepts connections.
There are no `healthcheck:` blocks in any Compose file.

Full deployment mechanics — Vault PKI and the certificate hot-reload watchers,
the Grafana Alloy log and metric pipeline, and the GitHub Actions test and
deploy workflows — are **not** covered in this pass. See
[known gaps](./README.md#known-gaps).
