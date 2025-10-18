from analyzers.base_analyzer import BaseAnalyzer

class AWSAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(provider_name="AWS")
    
    def analyze_ec2_instances(self, instances):
        threats = []

        for i in instances:
            if i.get("PublicIp") and i.get("State") == "running":
                threats.append(self._format_threat(
                    "Public EC2 instance running",
                    "High",
                    i["InstanceId"]
                ))
        
        return threats

