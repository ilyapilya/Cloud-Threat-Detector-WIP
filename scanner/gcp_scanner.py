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
                if response.instances:
                    for instance in response.instances:
                        instances.append({
                            'name': instance.name,
                            'status': instance.status,
                            'external_ip': instance.network_interfaces[0].access_configs[0].nat_ip
                            if instance.network_interfaces and instance.network_interfaces[0].access_configs else None,
                            'network_tags': instance.tags.items if instance.tags else []
                        })
            return instances
        except Exception as e:
            print("Error fetching GCP instances:", e)
            return []
    
    def get_storage_buckets(self):
        """
        Fetches the list of GCP Storage buckets in the project.
        """
        client = storage.Client(credentials = self.credentials)
        
    def scan(self):
        print("Starting GCP VM scan...")
        return self.list_instances()
