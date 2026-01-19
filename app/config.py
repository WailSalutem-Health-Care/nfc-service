"""
Application configuration management.

Centralizes environment variable access and configuration defaults.
"""

import os
from typing import Optional


class Config:
    """Application configuration class."""
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "wailsalutem")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # RabbitMQ Configuration
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: str = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_CONSUME_EXCHANGE: str = os.getenv("RABBITMQ_CONSUME_EXCHANGE", "wailsalutem.events")
    RABBITMQ_CONSUME_QUEUE: str = os.getenv("RABBITMQ_CONSUME_QUEUE", "nfc-tag-events")
    RABBITMQ_CONSUMER_ENABLED: bool = os.getenv("RABBITMQ_CONSUMER_ENABLED", "true").lower() == "true"
    
    # OpenTelemetry Configuration
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://otel-collector.observability.svc.cluster.local:4317"
    )
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "nfc-service")
    OTEL_RESOURCE_ATTRIBUTES: str = os.getenv(
        "OTEL_RESOURCE_ATTRIBUTES",
        "service.namespace=wailsalutem,deployment.environment=production"
    )
    OTEL_TRACES_SAMPLER: str = os.getenv("OTEL_TRACES_SAMPLER", "parentbased_always_on")
    SERVICE_VERSION: str = os.getenv("SERVICE_VERSION", "1.0.0")
    SERVICE_NAMESPACE: str = os.getenv("SERVICE_NAMESPACE", "wailsalutem")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Application Configuration
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,https://wailsalutem-web-ui.netlify.app"
    )
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the database connection URL."""
        return (
            f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    @classmethod
    def get_allowed_origins_list(cls) -> list[str]:
        """Get the list of allowed CORS origins."""
        return [origin.strip() for origin in cls.ALLOWED_ORIGINS.split(",")]


# Singleton config instance
config = Config()
