from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5434/opportunity_engine"
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
