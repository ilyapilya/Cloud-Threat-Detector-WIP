import pytest
from unittest.mock import Mock, patch
from scanner.azure_scanner import AzureScanner

@pytest.fixture
def mock_compute_client():
    with patch('azure.mgmt.compute.ComputeManagementClient') as mock:
        yield mock

@pytest.fixture
def azure_scanner():
    return AzureScanner(subscription_id="mock-subscription")

def test_list_instances_success(azure_scanner, mock_compute_client):
    # Mock VM data
    mock_vm = Mock()
    mock_vm.name = "test-vm"
    mock_vm.location = "eastus"
    mock_vm.hardware_profile.vm_size = "Standard_DS1_v2"
    mock_vm.network_profile.network_interfaces = [Mock()]
    mock_vm.provisioning_state = "Succeeded"

    # Setup mock response
    mock_compute_client.return_value.virtual_machines.list_all.return_value = [mock_vm]
    
    # Mock network interface client
    with patch('azure.mgmt.network.NetworkManagementClient') as mock_network:
        mock_nic = Mock()
        mock_nic.ip_configurations = [Mock()]
        mock_nic.ip_configurations[0].public_ip_address = Mock()
        mock_nic.ip_configurations[0].public_ip_address.ip_address = "20.123.123.123"
        
        mock_network.return_value.network_interfaces.get.return_value = mock_nic
        
        instances = azure_scanner.list_instances()
        
        assert len(instances) == 1
        assert instances[0]["name"] == "test-vm"
        assert instances[0]["public_ip"] == "20.123.123.123"
        assert instances[0]["location"] == "eastus"
        assert instances[0]["size"] == "Standard_DS1_v2"

def test_list_instances_no_public_ip(azure_scanner, mock_compute_client):
    # Mock VM without public IP
    mock_vm = Mock()
    mock_vm.name = "private-vm"
    mock_vm.location = "eastus"
    mock_vm.network_profile.network_interfaces = [Mock()]
    mock_vm.provisioning_state = "Succeeded"

    mock_compute_client.return_value.virtual_machines.list_all.return_value = [mock_vm]
    
    with patch('azure.mgmt.network.NetworkManagementClient') as mock_network:
        mock_nic = Mock()
        mock_nic.ip_configurations = [Mock()]
        mock_nic.ip_configurations[0].public_ip_address = None
        
        mock_network.return_value.network_interfaces.get.return_value = mock_nic
        
        instances = azure_scanner.list_instances()
        
        assert len(instances) == 1
        assert instances[0]["name"] == "private-vm"
        assert instances[0]["public_ip"] is None

def test_list_instances_api_error(azure_scanner, mock_compute_client):
    # Mock Azure API error
    mock_compute_client.return_value.virtual_machines.list_all.side_effect = \
        Exception("Azure API Error")
    
    with pytest.raises(Exception) as exc_info:
        azure_scanner.list_instances()
    
    assert "Azure API Error" in str(exc_info.value)

def test_authentication_error(azure_scanner, mock_compute_client):
    # Mock authentication error
    mock_compute_client.return_value.virtual_machines.list_all.side_effect = \
        Exception("Authentication failed")
    
    with pytest.raises(Exception) as exc_info:
        azure_scanner.list_instances()
    
    assert "Authentication failed" in str(exc_info.value)