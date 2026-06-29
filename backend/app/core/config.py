from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    port: int = 5001
    mongodb_uri: str
    mongodb_db_name: str = "ticket_classifier"
    db_required_on_startup: bool = False

    jwt_secret: str = "change-me"
    jwt_expires_in_hours: int = 24 * 7
    widget_jwt_expires_in_hours: int = 40

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "ticket_knowledge"
    qdrant_tickets_collection: str = "ticket_queries"

    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"

    cloudinary_url: str | None = None
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    cloudflare_account_id: str | None = None
    cloudflare_images_token: str | None = None


settings = Settings()
