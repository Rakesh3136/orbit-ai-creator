from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Autonomous AI Media Network API",
    version="0.1.0",
    description="Control plane for channels, agents, workflows, approvals, and media operations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health/live", tags=["system"])
async def liveness() -> dict[str, str]:
    """Process liveness only; dependency readiness is added with database wiring."""
    return {"status": "alive", "service": "aimn-api"}


@app.get("/api/v1/system", tags=["system"])
async def system_info() -> dict[str, str]:
    return {
        "name": "Autonomous AI Media Network",
        "api_version": "0.1.0",
        "stage": "foundation",
    }
