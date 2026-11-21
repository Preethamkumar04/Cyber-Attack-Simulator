from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import logger
from app.database.connection import create_tables
from app.api.scenario_routes import router as scenario_router
from app.api.artifact_routes import router as artifact_router
from app.api.terminal_routes import router as terminal_router
from app.api.auth_routes import router as auth_router
from app.api.session_routes import router as session_router
from app.api.analytics_routes import router as analytics_router
from app.api.websocket_routes import router as websocket_router
from app.api.investigation_routes import router as investigation_router

app = FastAPI(
    title=settings.APP_NAME
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    scenario_router,
    prefix="/scenario",
    tags=["Scenario"]
)

app.include_router(
    investigation_router,
    prefix="/investigation",
    tags=["Investigation"]
)

app.include_router(
    artifact_router,
    prefix="/artifacts",
    tags=["Artifacts"]
)

app.include_router(
    terminal_router,
    prefix="/terminal",
    tags=["Terminal"]
)

app.include_router(
    session_router,
    prefix="/sessions",
    tags=["Sessions"]
)

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)

app.include_router(
    websocket_router,
    prefix="/ws",
    tags=["WebSocket"]
)


@app.on_event("startup")
async def startup_event():

    create_tables()

    logger.info("Database initialized")
    logger.info("Application started")


@app.get("/")
def home():

    logger.info("Home endpoint accessed")

    return {
        "status": "running",
        "model": settings.OLLAMA_MODEL,
        "attack_engine": settings.APP_NAME,
    }


@app.get("/health")
def health_check():
    from app.services.docker.engine_factory import get_attack_engine

    engine = get_attack_engine()

    return {
        "status": "healthy",
        "engine": engine.get_engine_type(),
        "model": settings.OLLAMA_MODEL,
    }
