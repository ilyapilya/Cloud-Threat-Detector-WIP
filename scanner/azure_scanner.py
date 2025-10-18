from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from botocore.exceptions import ClientError  # optional for structure parity
from .base_scanner import BaseScanner

class AzureScanner(BaseScanner):
    def __init__(self, subscription_id):
        super().__init__("Azure")
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)

    def list_vms(self):
        instances = []
        try:
            for vm in self.compute_client.virtual_machines.list_all():
                public_ip = None
                nic_id = vm.network_profile.network_interfaces[0].id
                nic_name = nic_id.split('/')[-1]
                rg_name = nic_id.split('/')[4]

                nic = self.resource_client.resources.get(rg_name, '', '', '', nic_name)
                instances.append({
                    "VMName": vm.name,
                    "ResourceGroup": rg_name,
                    "Location": vm.location,
                    "PublicIP": public_ip,
                })
            return instances
        except Exception as e:
            self._log(f"Error fetching Azure VMs: {e}")
            return []

    def scan(self):
        self._log("Starting Azure VM scan...")
        return self.list_vms()
