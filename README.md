# Cloud-Threat-Detector

## NOTE: 
### THIS IS A WORK IN PROGRESS, CURRENTLY IN THE BACKEND DEV AND DATABASE INTEGRATION PHASE

A tool that automatically scans and detects vulnerabilities in cloud platforms. This tool is intended to assess the security posture and detect anomalous behavior and threats with monitoring and alerting.

Cloud security is paramount in the ever-evolving transition from old infra to cloud computing. This tool will ensure cloud and infrastructural security within the cloud storage system.

# Architecture

### Scanning

The purpose of scanning is to collect raw data from cloud providers (EC2 instances, gathering metadata). This content is used in analyzers, to detect public-facing assets, vulnerabilities, etc.

# Roadmap
 - [x] AWS Public Instance Discovery
 - [x] Azure asset discovery
 - [ ] Database Integration (PostgreSQL)
 - [x] Vulnerability Scanning (Rough Skeleton)
 - [ ] Web Dashboard


# Testing

Local orchestration tests are done with Pytest. These tests verify functionality for:
- AWS EC2 Analyzation (done with Moto / local mock AWS credentials)
- Integration API (Port running on endpoint correctly)
