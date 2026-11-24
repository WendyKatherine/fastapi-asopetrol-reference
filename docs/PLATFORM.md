# Platform roadmap

What this repository demonstrates as a platform engineering artifact, level by level, and the reasoning behind each piece.

**What "platform" means here:** It is the set of practices that let *someone else* run, change and trust this software without asking its author. Environments, configuration, permissions, delivery, observability, data safety, infrastructure as code, and cost guardrails.

---

## Level 1 — Foundations (already in place)

| Piece | Platform concept it proves |
|---|---|
| Settings validated at boot, from environment | 12-factor config: the same image runs anywhere, behaviour lives in the environment |
| `/healthz` with no dependencies | Liveness probe: distinguishes "process alive" from "can serve traffic" |
| JSON logs via structlog | Logs are data: aggregable, filterable, alertable |
| `make check` as a single gate | One definition of quality, reused locally and in CI |
| CI on every push and PR | Nothing reaches `main` without passing the gate |
| `docker-compose` for PostgreSQL | Local parity: the dev database is the same engine and version as the target |
| ADRs for real decisions | Design rationale survives the person who made the decision |

## Level 2 — Data and permissions (this week)

| Item | Why it matters |
|---|---|
| **Two database roles**: `app` (DML only) and `migrator` (DDL) | The application cannot alter the schema. A compromised app cannot `DROP TABLE`. A migration user that only runs during deploys is the smallest privilege that still works |
| Alembic with an explicit `target_metadata` | Schema changes are versioned, reviewable and reproducible |
| Reversible migrations, tested both ways | A rollback that was never executed is not a rollback |
| Backup script + verified restore | A backup that was never restored is an assumption |
| Idempotent seed | Local and staging environments can be rebuilt from scratch |
| Tests against real PostgreSQL (testcontainers) | SQLite has no `FOR UPDATE`: the project's core rule cannot be tested on it |

## Level 3 — Delivery (week 2)

| Item | Why it matters |
|---|---|
| Multi-stage Dockerfile, non-root user, `--frozen` | The image is reproducible and the process runs without root |
| CI job that builds the image | "Works locally" stops being the acceptance criterion |
| Image and dependency scanning | Vulnerabilities are found before production, not after |
| pre-commit hooks | Cheap problems never enter the history |
| Version tag + changelog | Deployments are identifiable and revertible |

## Level 4 — AWS (weeks 3–4)

| Item | Why it matters |
|---|---|
| Terraform for VPC, subnets, SG, RDS, S3, Secrets, ECR | Infrastructure is code: reviewable, repeatable, destroyable |
| **GitHub OIDC → AWS** | No long-lived AWS keys anywhere. The workflow assumes a role for minutes |
| ECS Express + ALB | A real running service behind a load balancer |
| CloudWatch logs + 5xx alarm + billing alarm | You learn about failures before users report them, and cost cannot run away silently |
| `terraform destroy` at the end of every demo | The environment is disposable by design |

## Level 5 — Operations (optional, high signal)

| Item | Why it matters |
|---|---|
| Runbook: symptoms → checks → mitigation → rollback | Anyone on call can act without the author |
| Simple SLO: availability and p95 latency | Reliability becomes a number, not an opinion |
| Chaos check: stop the database and observe | `/healthz` stays up, readiness fails, the app degrades instead of crashing |

---

## Decisions taken

| # | Decision | Reasoning |
|---|---|---|
| P-01 | One PostgreSQL container, two databases (`app_dev`, `app_test`) | Isolation of test data without paying for a second server. Separate *databases*, not separate clusters |
| P-02 | Two roles: `app` (no DDL) and `migrator` | Least privilege with a real operational reason: migrations run in deployment, not in the request path |
| P-03 | Tests run against real PostgreSQL | The concurrency rule depends on row-level locking; SQLite would test a different program |
| P-04 | Environments named `local` and `staging`; no `production` | A portfolio does not need a production tier. Naming it honestly is part of the point |
| P-05 | Staging is created and destroyed on demand | Cost control and evidence that the environment is reproducible from code |
| P-06 | **Kubernetes is on the roadmap, not excluded**: local cluster in Phase 3, once the API has a database and a migration to run | Orchestration teaches nothing without a workload that benefits from it. Deferring is sequencing, not rejection |

## Deferred, not excluded

| Item | Status |
|---|---|
| **Kubernetes** | **Planned.** Local cluster (`kind`/`k3d`) after the data layer is in place, so there is a real workload to orchestrate: probes on `/healthz`, migrations as a `Job` with the `migrator` role, resource limits, secrets |
| Service mesh | Not planned. No multi-service traffic to justify it |
| Multi-region | Not planned. Needs an availability requirement this demo does not have |
| Hand-rolled secret store | Not planned. Secrets Manager is the answer; writing one is a distraction |
| Microservices | Not planned. One deployable until a boundary is proven by a real constraint |

Each of these needs an operational reason. Being able to explain *why not yet* is part of the artifact — but "not yet" is a schedule, not a verdict.
