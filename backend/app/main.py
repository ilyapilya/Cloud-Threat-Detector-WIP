from fastapi import FastAPI
from scanner.aws_scanner import list_ec2_instances

app = FastAPI(title="Cloud Attack Surface Analyzer")

@app.get("/")
def root():
    return {"message": "Cloud Attack Surface Analyzer API running"}

@app.get("/aws/instances")
def get_instances():
    instances = list_ec2_instances()
    return {"instances": instances}
