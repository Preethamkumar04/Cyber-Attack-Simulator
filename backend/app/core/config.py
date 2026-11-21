from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str
    OLLAMA_URL: str
    OLLAMA_MODEL: str
    SECRET_KEY: str
    DATABASE_URL: str
    ATTACK_ENGINE: str = "mock"
    DOCKER_ENABLED: bool = False
    DOCKER_NETWORK_PREFIX: str = "cybersim"
    DOCKER_LAB_TIMEOUT: int = 30
    DOCKER_LAB_IMAGE: str = "cybersim-training-lab:latest"
    DOCKER_LAB_CONTEXT: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
