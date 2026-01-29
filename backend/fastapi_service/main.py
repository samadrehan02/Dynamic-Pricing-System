from fastapi import FastAPI

from backend.fastapi_service.routers import health, alerts, skus
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pricing System API",
    description="Read-only APIs for pricing monitoring and explainability",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(skus.router, prefix="/skus", tags=["skus"])
