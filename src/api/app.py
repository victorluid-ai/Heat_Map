import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import admin, auth, heatmap, analytics, shops, stream
from .schemas import HealthResponse
from ..pipeline.coordinator import PipelineCoordinator
from ..storage.database import init_db
from ..utils.config import load_config
from ..utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    cfg = load_config()
    engine, session_factory = init_db(cfg["storage"]["db_url"])
    app.state.config = cfg
    app.state.session_factory = session_factory
    coordinator = PipelineCoordinator(cfg, session_factory)
    coordinator.start()
    app.state.coordinator = coordinator
    logger.info("Heat Map API started")
    yield
    coordinator.stop()
    engine.dispose()
    logger.info("Heat Map API shutdown complete")


app = FastAPI(title="Heat Map API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(shops.router)
app.include_router(stream.router)
app.include_router(heatmap.router)
app.include_router(analytics.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse)
async def health():
    coordinator: PipelineCoordinator | None = getattr(app.state, "coordinator", None)
    return HealthResponse(
        status="ok",
        cameras=list(coordinator.camera_ids) if coordinator else [],
        total_events_queued=coordinator._event_bus.qsize() if coordinator else 0,
    )
