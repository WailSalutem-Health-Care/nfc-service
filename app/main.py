import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.messaging.consumer import NfcEventConsumer
from app.nfc.router import router as nfc_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI()
    consumer = NfcEventConsumer()

    allowed_origins_str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,https://wailsalutem-web-ui.netlify.app",
    )
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(nfc_router)

    Instrumentator().instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )

    @app.on_event("startup")
    def start_consumer():
        consumer.start()

    @app.on_event("shutdown")
    def stop_consumer():
        consumer.stop()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

