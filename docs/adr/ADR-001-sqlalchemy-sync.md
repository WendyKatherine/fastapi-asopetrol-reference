# ADR-001 — Synchronous SQLAlchemy

- **Date:** 2026-11-23
- **Status:** accepted
- **Decides:** Wendy Gómez

## Context

The repository needs a persistence layer for its first vertical slice with a database. That decision touches at least five things: the engine, the session per request, the tests, the signature of every use case, and how FastAPI routes are declared.

Two contradictions had to be resolved before writing the first model:

1. The dependencies initially copied from another project declared `sqlalchemy[asyncio]` and `asyncpg`, while the design described sync with `psycopg`. Two incompatible stacks in one `pyproject.toml`.
2. Async would leak into every layer: `async def` use cases, an async session, `pytest-asyncio`, and routes that cannot be plain functions.

The declared goal of the project is **understanding and judgement**, not unmeasured throughput. That constraint decides the trade-off.

## Decision

**SQLAlchemy 2.0 in synchronous mode**, with the `psycopg` 3 driver.

## Consequences

**Positive**

- One mental model. The session is an ordinary object, not an async context threaded through every function.
- Tests need no async plugin and no `await` in each assertion.
- FastAPI routes can be plain `def`: FastAPI runs them in a worker thread, so blocking I/O does not stall the event loop.
- Every line stays explainable in an interview, which is the point of the repository.

**Negative**

- Fewer concurrent connections per process. Mitigated by running more processes (gunicorn with uvicorn workers), which is the normal model in containers.
- Use cases are bound to a synchronous signature. Moving to async later means touching the whole application layer, not just the repository.

**Cost to reverse**

Medium. Going sync → async requires: swapping the driver, rewriting the session as an async generator, converting every use case to `async def`, adapting the tests, and adding `pytest-asyncio`. Roughly one branch of work, not a one-line change.

## What this already implies in the repository

| Element | Current state |
|---|---|
| `pyproject.toml` | `sqlalchemy` and `psycopg` only; no `asyncpg`, no `sqlalchemy[asyncio]` |
| `.env` / `DATABASE_URL` | `postgresql+psycopg://…@localhost:5433/asopetrol_dev` |
| Local infrastructure | PostgreSQL 17 in `docker-compose.yml`, port 5433 → 5432, named volume |
| Tests | `pytest` with no async plugin; one test, no `await` |
| Routes | `/healthz` declared with plain `def` |

## Alternatives rejected

**Async from the start (`asyncpg`).** Better throughput under high concurrency, which this project neither measures nor needs. It adds `await` to every layer and a second mental model competing with Clean Architecture in the same learning session.

**SQLModel.** Less duplicated code between model and schema, but it hides the domain/persistence separation the repository exists to demonstrate, and its lifecycle depends on a single maintainer.

**An ORM other than SQLAlchemy.** The job market asks for SQLAlchemy; choosing otherwise would reduce the transferability of the repository, which is its purpose.

## Review

Revisit if a use case appears with a measurable concurrency requirement, or if the AWS deployment hits a connection limit with several processes. At that point a new ADR supersedes this one; this file is not edited.
