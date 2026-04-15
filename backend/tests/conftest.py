"""
Pytest configuration for CloudGuard scanner tests.

Sets fake AWS credentials in the environment before any test module is
imported.  moto intercepts all boto3 calls when the @mock_aws decorator
(or context manager) is active, so these values never reach real AWS.
"""
import os

# Must be set before boto3 / botocore is imported by the scanner module.
os.environ.setdefault("AWS_ACCESS_KEY_ID",     "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SECURITY_TOKEN",    "testing")
os.environ.setdefault("AWS_SESSION_TOKEN",     "testing")
os.environ.setdefault("AWS_DEFAULT_REGION",    "us-east-1")
