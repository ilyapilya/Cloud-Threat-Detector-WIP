import os, boto3
from .analyzers.aws_analyzer import analyze_ec2_instances
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

ec2 = boto3.client(
    "ec2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_default_region=os.getenv("AWS_DEFAULT_REGION", "us-west-2")
)

def list_ec2_instances():
    ec2 = boto3.client("ec2")
    instances = []
    try:
        response = ec2.describe_instances()
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                if instance.get("PublicIpAddress"):
                    instances.append({
                        "InstanceId": instance["InstanceId"],
                        "PublicIp": instance["PublicIpAddress"],
                        "State": instance["State"]["Name"]
                    })
        return instances
    except ClientError as e:
        print("Error:", e)
        return []

def get_ec2_threat_report():
    ec2 = boto3.client("ec2")
    instances = list_ec2_instances()
    all_instances = [
        i for r in instances["Reservations"] for i in r["Instances"]
    ]
    report = analyze_ec2_instances(all_instances)
    return {
        "total": len(all_instances),
        "findings": report
    }

