# scanner/tests/test_aws_analyzer.py
from scanner.analyzers.aws_analyzer import analyze_ec2_instances

def test_detects_public_instance():
    instance = {
        "InstanceId": "i-01234",
        "PublicIpAddress": "3.3.3.3",
        "SecurityGroups": [{"GroupId": "sg-1"}],
        "BlockDeviceMappings": [],
    }
    findings = analyze_ec2_instances([instance])
    assert any(f["id"] == "i-01234" and f["severity"] == "HIGH" for f in findings)
