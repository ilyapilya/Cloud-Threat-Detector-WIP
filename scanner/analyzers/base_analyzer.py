
class BaseAnalyzer:
    def __init__(self, provider_name):
        self.provider_name = provider_name

    def analyze(self, data):
        """Main method every analyzer must implement."""
        raise NotImplementedError("Subclasses must implement analyze()")

    def _format_threat(self, issue, severity, resource_id):
        return {
            "provider": self.provider_name,
            "issue": issue,
            "severity": severity,
            "resource_id": resource_id
        }
