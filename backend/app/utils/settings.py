from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        extra = "ignore"
    )
    DB_CONNECTION:str
    SECRET_KEY:str
    ALGORITHM:str
    EXP_TIME : int
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

settings = Settings()