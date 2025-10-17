import os
import boto3
from fastapi import FastAPI
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the project root and backend directory to Python path
project_root = Path(__file__).resolve().parent.parent.parent
backend_root = Path(__file__).resolve().parent.parent
sys.path.extend([str(project_root), str(backend_root)])

from scanner.aws_scanner import list_ec2_instances
# Change the import to be relative to the current package
from .routes.cloud_routes import router as cloud_router

# Load environment variables
load_dotenv()

app = FastAPI(title="Cloud Attack Surface Analyzer")

@app.get("/")
def root():
    return {"message": "Cloud Attack Surface Analyzer API running"}

@app.get("/aws/instances")
async def get_instances():
    instances = list_ec2_instances()
    return {"instances": instances}


