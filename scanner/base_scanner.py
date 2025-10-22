import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def BaseScanner():
    """
    Base class for cloud scanning operations. Purpose of scanning is
    to fetch data from cloud platforms for further analysis to detect
    potential security threats.
    """

    def __init__(self, provider_name):
        self.provider_name = provider_name

    def scan(self):
        raise NotImplementedError("Scan method must be implemented in subclass")
    
    def load_credentials(self):
        """
        Loads credentials from .env file
        """
        