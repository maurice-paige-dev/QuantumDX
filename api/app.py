from fastapi import FastAPI
from .routes import router
from services.container import build_container
from observability.logging_config import configure_logging

def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="QuantumDX v2", version="2.2.0")
    app.state.container = build_container()
    app.include_router(router)
    @app.on_event("startup")
    def startup() -> None:
        app.state.container.bootstrap()
    return app
