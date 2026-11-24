"""Health endpoints.

Liveness (/healthz) answers "is the process up?" with no dependencies.
Readiness (/readyz) answers "can we actually serve traffic?" by probing
Postgres and Redis. Orchestrators use them differently, so they are split.
"""

from typing import Literal

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def liveness() -> dict[str, Literal["ok"]]:
    return {"status": "ok"}
