from pydantic import BaseSettings
from typing import Optional

class CloudSettings(BaseSettings):
    # AWS Settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str = "us-west-2"
    
    # GCP Settings
    GCP_PROJECT_ID: str
    GCP_CREDENTIALS_PATH: Optional[str] = None
    GCP_REGION: str = "us-central1"
    
    # Azure Settings
    AZURE_SUBSCRIPTION_ID: str
    AZURE_TENANT_ID: str
    AZURE_CLIENT_ID: str
    AZURE_CLIENT_SECRET: str
    
    # General Settings
    SCAN_INTERVAL: int = 3600  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True