from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from api.routers.risk import router as risk_router
from api.routers.batch import batch_router


app = FastAPI(
    title="AI Risk Manager API",
    description="API for AI-powered payment dispute risk assessment",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router)
app.include_router(batch_router)