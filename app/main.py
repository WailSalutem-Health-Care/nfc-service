import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.messaging.consumer import NfcEventConsumer
from app.nfc.router import router as nfc_router

# OpenTelemetry imports
from app.observability.telemetry import init_telemetry, shutdown_telemetry
from app.observability.logging_config import configure_logging
from app.observability.middleware import TelemetryMiddleware
from app.observability.database import instrument_database
from app.db.session import engine

# Load environment variables
load_dotenv()

# Configure structured logging with trace correlation
log_level = os.getenv("LOG_LEVEL", "INFO")
configure_logging(log_level)

logger = logging.getLogger(__name__)

# Initialize OpenTelemetry (tracing and metrics)
telemetry_initialized = init_telemetry()
if telemetry_initialized:
    logger.info("OpenTelemetry initialized successfully")
else:
    logger.warning("OpenTelemetry initialization failed - service will run without telemetry")

# Instrument database with tracing
instrument_database(engine)

# Create FastAPI application
app = FastAPI(
    title="NFC Service",
    description="NFC tag management service with OpenTelemetry observability",
    version="1.0.0",
)

# Initialize consumer
consumer = NfcEventConsumer()

# Add custom telemetry middleware (must be added before CORS)
app.add_middleware(TelemetryMiddleware)

# Configure CORS
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://wailsalutem-web-ui.netlify.app,https://wailsalutem-suite.netlify.app"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nfc_router)


@app.on_event("startup")
def startup_event():
    """Application startup event handler."""
    logger.info("NFC Service starting up...")
    consumer.start()
    logger.info("NFC Service startup complete")


@app.on_event("shutdown")
def shutdown_event():
    """Application shutdown event handler with telemetry cleanup."""
    logger.info("NFC Service shutting down...")
    
    # Stop consumer
    consumer.stop()
    logger.info("Consumer stopped")
    
    # Flush and shutdown telemetry
    shutdown_telemetry()
    logger.info("Telemetry shutdown complete")
    
    logger.info("NFC Service shutdown complete")


@app.get("/health")
def health():
    """
    Health check endpoint.
    
    This endpoint is excluded from telemetry to reduce noise.
    """
    return {"status": "ok"}

