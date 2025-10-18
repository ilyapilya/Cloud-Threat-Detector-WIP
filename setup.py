from setuptools import setup, find_packages

setup(
    name="cloud-threat-detector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "boto3",
        "python-dotenv",
    ],
)