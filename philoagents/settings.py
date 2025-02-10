from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    GROQ_API_KEY: str
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"

    MONGO_URI: str
    MONGO_DB_NAME: str = "philoagents"
    MONGO_STATE_CHECKPOINT_COLLECTION: str = "philosopher_state_checkpoints"
    MONGO_STATE_WRITES_COLLECTION: str = "philosopher_state_writes"
    MONGO_CONTEXT_COLLECTION: str = "philosopher_context"

    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 20
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5


settings = Settings()
