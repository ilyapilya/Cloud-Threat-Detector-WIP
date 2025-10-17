import os, boto3
from fastapi import FastAPI
from scanner.aws_scanner import list_ec2_instances
from backend.app.routes.cloud_routes import router as cloud_router

app = FastAPI(title="Cloud Attack Surface Analyzer")

@app.get("/aws/instances")
def list_instances():
    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_default_region=os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    )

    instances = ec2.describe_instances()
    return instances

@app.get("/")
def root():
    return {"message": "Cloud Attack Surface Analyzer API running"}

@app.get("/aws/instances")
def get_instances():
    instances = list_ec2_instances()
    return {"instances": instances}


