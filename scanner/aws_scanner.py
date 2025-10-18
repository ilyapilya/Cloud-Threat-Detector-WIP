import os, boto3
from analyzers.base_analyzer import BaseAnalyzer
from .analyzers.aws_analyzer import analyze_ec2_instances
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

ec2 = boto3.client(
    "ec2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-west-2")
)

class AWSScanner(BaseAnalyzer):
    def __init__(self):
        super().__init__(provider_name="AWS")

    def list_ec2_instances(self, include_private=False):
        """
        Scans AWS EC2 instances and returns metadata for analysis.
        Optionally includes private instances.
        """
        ec2 = boto3.client("ec2")
        instances = []

        try:
            response = ec2.describe_instances()
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    public_ip = instance.get("PublicIpAddress")
                    private_ip = instance.get("PrivateIpAddress")

                    # Skip private-only instances unless requested
                    if not include_private and not public_ip:
                        continue

                    instance_data = {
                        "InstanceId": instance["InstanceId"],
                        "PublicIp": public_ip,
                        "PrivateIp": private_ip,
                        "State": instance["State"]["Name"],
                        "SecurityGroups": [
                            sg["GroupName"] for sg in instance.get("SecurityGroups", [])
                        ],
                        "Tags": instance.get("Tags", [])
                    }
                    instances.append(instance_data)

            return instances

        except ClientError as e:
            print("Error listing EC2 instances:", e)
            return []

    def get_ec2_threat_report(self):
        instances = self.list_ec2_instances()
        report = analyze_ec2_instances(instances)
        return {
            "total": len(instances),
            "findings": report
        }

