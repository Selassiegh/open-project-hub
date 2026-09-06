from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./harvest_credit.db"
    admin_pin: str = "1234"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
