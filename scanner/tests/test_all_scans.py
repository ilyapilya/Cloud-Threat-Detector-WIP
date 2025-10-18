import pytest
from scanner.aws_scanner import list_ec2_instances
from scanner.azure_scanner import list_azure_instances
from scanner.gcp_scanner import list_gcp_instances

def run_all_scans():
    results = {
        "aws": list_ec2_instances(),
        "azure": list_azure_instances(),
        "gcp": list_gcp_instances()
    }
    return results

def test_run_all_scans():
    results = run_all_scans()

    # Check each provider key exists
    assert "aws" in results
    assert "azure" in results
    assert "gcp" in results

    # Optionally check structure
    for provider, instances in results.items():
        assert isinstance(instances, list)
        for instance in instances:
            assert "InstanceId" in instance or "id" in instance
