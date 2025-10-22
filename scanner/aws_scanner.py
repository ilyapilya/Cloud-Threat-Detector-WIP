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
        # create a session on the instance so other methods can use self.session.client(...)
        self.session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        )

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
        
    def fetch_s3_buckets(self):
        """
        Fetches the list of S3 buckets in the AWS account.
        """
        s3 = self.session.client('s3')
        try:
            buckets = s3.list_buckets()
            bucket_details = []
            for bucket in buckets['Buckets']:
                # Check bucket policy
                try:
                    policy = s3.get_bucket_policy(Bucket=bucket['Name'])
                    policy_status = 'public' if self._is_public_policy(policy) else 'private'
                except:
                    policy_status = 'no-policy'
                
                bucket_details.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'],
                    'policy_status': policy_status
                })
            return bucket_details
        except ClientError as e:
            print(f"S3 Error: {e}")
            return []

    def scan(self):
        return self.list_ec2_instances()

