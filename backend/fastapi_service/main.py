from fastapi import FastAPI

from backend.fastapi_service.routers import health, alerts, skus

app = FastAPI(
    title="Pricing System API",
    description="Read-only APIs for pricing monitoring and explainability",
    version="0.1.0",
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(skus.router, prefix="/skus", tags=["skus"])
