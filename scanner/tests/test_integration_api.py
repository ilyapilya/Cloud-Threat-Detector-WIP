import os
import requests

def test_integration_aws_endpoint():
    # Test if server running @ Port: 127.0.0.1:8000
    url = "http://127.0.0.1:8000/aws/threat-report"
    response = requests.get(url)

    assert response.status_code == 200
