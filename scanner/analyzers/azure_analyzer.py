from .base_analyzer import BaseAnalyzer

class AzureAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("Azure")

    def analyze(self, data):
        threats = []
        for vm in data:
            if vm.get("PublicIP"):
                threats.append(self._format_threat(
                    "Azure VM has a public IP assigned",
                    "High",
                    vm["VMName"]
                ))
        return threats
