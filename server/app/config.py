from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/aivoa_complaints"

    groq_api_key: str = ""
    groq_model: str = "gemma2-9b-it"

    cors_origins: str = "http://localhost:5173"

    default_page_size: int = 20
    max_page_size: int = 100

    max_upload_size_mb: int = 10
    allowed_upload_extensions: str = ".pdf,.docx,.txt,.eml"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_upload_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_upload_extensions.split(",") if ext.strip()]


settings = Settings()
