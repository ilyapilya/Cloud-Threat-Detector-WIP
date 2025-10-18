from .base_analyzer import BaseAnalyzer

class GCPAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("GCP")

    def analyze(self, data):
        threats = []
        for instance in data:
            if instance.get("PublicIP"):
                threats.append(self._format_threat(
                    "GCP instance has a public IP assigned",
                    "High",
                    instance["InstanceName"]
                ))
        return threats
