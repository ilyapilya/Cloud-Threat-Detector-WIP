from google.cloud import compute_v1
from .base_scanner import BaseScanner
import os

class GCPScanner(BaseScanner):
    def __init__(self, project_id):
        super().__init__("GCP")
        self.project_id = project_id
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    def list_instances(self):
        instances = []
        try:
            client = compute_v1.InstancesClient()
            request = compute_v1.AggregatedListInstancesRequest(project=self.project_id)
            for zone, response in client.aggregated_list(request=request):
                if "instances" in response:
                    for instance in response["instances"]:
                        network_interfaces = instance.network_interfaces
                        public_ip = None
                        if network_interfaces and network_interfaces[0].access_configs:
                            public_ip = network_interfaces[0].access_configs[0].nat_i_p
                        instances.append({
                            "InstanceName": instance.name,
                            "Zone": zone,
                            "PublicIP": public_ip
                        })
            return instances
        except Exception as e:
            print("Error fetching GCP instances:", e)
            return []

    def scan(self):
        print("Starting GCP VM scan...")
        return self.list_instances()
