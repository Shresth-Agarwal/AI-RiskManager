from fastapi import FastAPI

from api.routers.risk import router as risk_router


app = FastAPI(
    title="AI Risk Manager API",
    description="API for AI-powered payment dispute risk assessment",
    version="1.0.0",
)

app.include_router(risk_router)