import boto3
from botocore.exceptions import ClientError

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

if __name__ == "__main__":
    print(list_ec2_instances())
