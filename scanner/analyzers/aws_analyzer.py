# Imports

def analyze_ec2_instances(instances):
    findings = []

    for instance in instances:
        if instance.get("PublicIpAddress"):
            findings.append({
                "id": instance["InstanceId"],
                "issue": "Publicly accessible EC2 instance",
                "severity": "HIGH"
            })

    return findings

