from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SOL-LMS-ML"
    debug: bool = True

settings = Settings()