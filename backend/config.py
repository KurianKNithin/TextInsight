from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

# Path to the backend directory
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    anthropic_api_key: str = Field(default="", validation_alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", validation_alias="ANTHROPIC_MODEL")
    mock_mode: str = Field(default="auto", validation_alias="MOCK_MODE")
    cors_origins: list[str] = ["*"]

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def is_mock_enabled(self) -> bool:
        if self.mock_mode.lower() in ("true", "1", "yes"):
            return True
        if self.mock_mode.lower() == "auto":
            # Auto enable mock mode if no valid API key is configured
            return not self.anthropic_api_key or self.anthropic_api_key == "your_anthropic_api_key_here"
        return False

settings = Settings()
