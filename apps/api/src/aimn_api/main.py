from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from aimn_api.api import router
from aimn_api.config import settings
from aimn_api.security import auth_router
from aimn_api.db import engine

app = FastAPI(title="Autonomous AI Media Network API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-AIMN-API-Key"],
)
app.include_router(auth_router)
app.include_router(router)

@app.get("/health/live", tags=["system"])
async def liveness():
    return {"status": "alive", "service": "aimn-api"}

@app.get("/health/ready", tags=["system"])
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is not ready")
    return {"status": "ready", "database": "reachable"}

@app.get("/api/v1/system", tags=["system"])
async def system_info():
    return {"name": "Autonomous AI Media Network", "api_version": "0.2.0", "stage": "channel-management-foundation"}
