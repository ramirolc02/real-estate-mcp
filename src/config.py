"""Application configuration using pydantic-settings."""

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Type-safe application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Real Estate MCP Server"
    debug: bool = False

    # Authentication
    api_token: str = Field(..., description="Bearer token for MCP authentication")

    # Database
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/realestate"],
    )

    # Database Pool
    db_pool_size: int = Field(default=5, ge=1, le=20)
    db_max_overflow: int = Field(default=10, ge=0, le=50)

    @property
    def async_database_url(self) -> str:
        """Ensure URL uses asyncpg driver."""
        url = str(self.database_url)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


# Singleton instance - will be initialized when first imported
# For testing, you can override this or use dependency injection
def get_settings() -> Settings:
    """Get application settings (lazy initialization)."""
    return Settings()


settings = get_settings()
