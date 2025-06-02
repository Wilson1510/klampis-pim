from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api"
    SECRET_KEY: str = "dev-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Parse and validate CORS origins configuration.

        Handles both string and list inputs:
        - If input is a string not starting with '[', splits it by commas
        - If input is a list or JSON string, returns it as-is

        Args:
            v: Input value which can be either a string or list of origins

        Returns:
            Union[List[str], str]: Processed list of origins or original value

        Example:
            >>> assemble_cors_origins("http://localhost,http://example.com")
            ["http://localhost", "http://example.com"]
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v

    # Database
    DATABASE_URI: str
    ADMIN_PARAMS: dict

    # Project Info
    PROJECT_NAME: str
    VERSION: str

    # General settings
    DEBUG: bool
    SYSTEM_USER_ID: int

    model_config = {
        "env_file": ".env",
        "env_file_encoding": 'utf-8',
        "case_sensitive": True
    }


settings = Settings()
