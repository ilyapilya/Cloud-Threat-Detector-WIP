import os
import boto3
from dotenv import load_dotenv

load_dotenv()

class BaseScanner:
    """
    Base class for cloud scanning operations. Purpose of scanning is
    to fetch data from cloud platforms for further analysis to detect
    potential security threats.
    """

    def __init__(self, provider_name):
        self.provider_name = provider_name

        # Credential loading from .env
        self.aws_credentials = {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        }

        self.azure_credentials = {
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "tenant_id": os.getenv("AZURE_TENANT_ID"),
            "client_id": os.getenv("AZURE_CLIENT_ID"),
            "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
        }

        self.gcp_credentials = {
            "credentials_file": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "project_id": os.getenv("GCP_PROJECT_ID"),
            "region": os.getenv("GCP_REGION", "us-central1"),
        }

        

    def scan(self):
        raise NotImplementedError("Scan method must be implemented in subclass")
    
        
        