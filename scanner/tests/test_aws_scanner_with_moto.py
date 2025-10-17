import os
import sys
import boto3
from moto import mock_aws

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scanner.aws_scanner import get_ec2_threat_report

@mock_aws
def test_get_ec2_threat_report_monkeypatched():
    # create fake EC2 instance
    ec2 = boto3.resource("ec2", region_name="us-west-2")
    inst = ec2.create_instances(ImageId="ami-1234", MinCount=1, MaxCount=1, InstanceType="t2.micro")[0]
    # give the instance a public IP – moto's create_instances may or may not set it, so optionally modify:
    ec2client = boto3.client("ec2", region_name="us-west-2")
    # Run the scanner's report function (it will internally call boto3.describe_instances but moto intercepts)
    report = get_ec2_threat_report()
    assert "findings" in report
