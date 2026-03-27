from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CargoLink"
    app_env: str = "local"
    debug: bool = False
    log_level: str = "INFO"

    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    bot_token: str = ""
    export_dir: str = "storage/exports"
    provider_mode: str = "mock"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()