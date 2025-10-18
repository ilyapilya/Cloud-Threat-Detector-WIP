import pytest
from unittest.mock import Mock, patch
from scanner.gcp_scanner import GCPScanner

@pytest.fixture
def mock_compute_client():
    with patch('google.cloud.compute_v1.InstancesClient') as mock:
        yield mock

@pytest.fixture
def gcp_scanner():
    return GCPScanner(project_id="test-project", credentials_path="fake-creds.json")

def test_list_instances_success(gcp_scanner, mock_compute_client):
    # Mock instance data
    mock_instance = {
        "name": "test-vm",
        "status": "RUNNING",
        "networkInterfaces": [
            {
                "accessConfigs": [
                    {"natIP": "34.123.123.123"}
                ]
            }
        ],
        "machineType": "n1-standard-1",
        "creationTimestamp": "2025-10-17T10:00:00.000-07:00"
    }
    
    mock_response = Mock()
    mock_response.instances = [mock_instance]
    
    # Setup mock response
    mock_compute_client.return_value.aggregated_list.return_value = [
        ("zones/us-central1-a", mock_response)
    ]
    
    instances = gcp_scanner.list_instances()
    
    assert len(instances) == 1
    assert instances[0]["InstanceName"] == "test-vm"
    assert instances[0]["PublicIP"] == "34.123.123.123"

def test_list_instances_no_public_ip(gcp_scanner, mock_compute_client):
    # Mock instance without public IP
    mock_instance = {
        "name": "private-vm",
        "status": "RUNNING",
        "networkInterfaces": [{}],
        "machineType": "n1-standard-1",
        "creationTimestamp": "2025-10-17T10:00:00.000-07:00"
    }
    
    mock_response = Mock()
    mock_response.instances = [mock_instance]
    
    mock_compute_client.return_value.aggregated_list.return_value = [
        ("zones/us-central1-a", mock_response)
    ]
    
    instances = gcp_scanner.list_instances()
    
    assert len(instances) == 1
    assert instances[0]["InstanceName"] == "private-vm"
    assert instances[0]["PublicIP"] is None

def test_list_instances_api_error(gcp_scanner, mock_compute_client):
    # Mock API error
    mock_compute_client.return_value.aggregated_list.side_effect = Exception("API Error")
    
    with pytest.raises(Exception) as exc_info:
        gcp_scanner.list_instances()
    
    assert "API Error" in str(exc_info.value)