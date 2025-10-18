from analyzers.base_analyzer import BaseAnalyzer

class AWSAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(provider_name="AWS")
    
    def analyze_ec2_instances(self, instances):
        findings = []

        for instance in instances:
            if instance.get("PublicIpAddress"):
                findings.append({
                    "id": instance["InstanceId"],
                    "issue": "Publicly accessible EC2 instance",
                    "severity": "HIGH"
                })

        return findings

