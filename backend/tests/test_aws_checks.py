"""
Unit tests for backend/app/scanner/aws_checks.py

Every check has at minimum:
  - A "violation" test: mock AWS state that SHOULD produce a finding
  - A "clean" test:     mock AWS state that SHOULD produce no findings

Run with:
    cd backend
    pip install -r requirements-dev.txt
    pytest tests/ -v
"""
import os
import boto3
import pytest
from unittest.mock import MagicMock, patch
from moto import mock_aws

# conftest.py already sets the env vars, but re-assert here for clarity
REGION = "us-east-1"

# ── Import the module under test ──────────────────────────────────────────────
from app.scanner.aws_checks import (
    check_s3_public_access_block,
    check_s3_versioning,
    check_security_groups,
    check_iam_mfa,
    check_root_access_keys,
    check_iam_password_policy,
    check_cloudtrail,
    check_ebs_encryption,
    check_rds_public,
    check_guardduty,
    check_ec2_public_instances,
    check_root_mfa,
    calculate_score,
    run_aws_checks,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _s3():
    return boto3.client("s3", region_name=REGION)

def _iam():
    return boto3.client("iam", region_name=REGION)

def _ec2():
    return boto3.client("ec2", region_name=REGION)

def _ct():
    return boto3.client("cloudtrail", region_name=REGION)

def _rds():
    return boto3.client("rds", region_name=REGION)

def _gd():
    return boto3.client("guardduty", region_name=REGION)

FAKE_CREDS = {
    "access_key_id":     "testing",
    "secret_access_key": "testing",
    "region":            REGION,
}


# ═══════════════════════════════════════════════════════════════════════════════
# Check 1 — S3 Public Access Block
# ═══════════════════════════════════════════════════════════════════════════════

class TestS3PublicAccessBlock:

    @mock_aws
    def test_violation_no_public_access_block(self):
        """Bucket with no public access block config → critical finding."""
        s3 = _s3()
        s3.create_bucket(Bucket="unprotected-bucket")

        findings = check_s3_public_access_block(s3)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "critical"
        assert "unprotected-bucket" in f["title"]
        assert f["resource_type"] == "S3Bucket"
        assert f["resource_id"] == "arn:aws:s3:::unprotected-bucket"

    @mock_aws
    def test_violation_partial_public_access_block(self):
        """Bucket with only some block settings enabled → critical finding."""
        s3 = _s3()
        s3.create_bucket(Bucket="partial-bucket")
        s3.put_public_access_block(
            Bucket="partial-bucket",
            PublicAccessBlockConfiguration={
                "BlockPublicAcls":       True,
                "IgnorePublicAcls":      True,
                "BlockPublicPolicy":     False,  # missing!
                "RestrictPublicBuckets": False,  # missing!
            },
        )

        findings = check_s3_public_access_block(s3)

        assert len(findings) == 1
        assert findings[0]["severity"] == "critical"

    @mock_aws
    def test_clean_all_block_settings_enabled(self):
        """Bucket with all 4 settings enabled → no findings."""
        s3 = _s3()
        s3.create_bucket(Bucket="secure-bucket")
        s3.put_public_access_block(
            Bucket="secure-bucket",
            PublicAccessBlockConfiguration={
                "BlockPublicAcls":       True,
                "IgnorePublicAcls":      True,
                "BlockPublicPolicy":     True,
                "RestrictPublicBuckets": True,
            },
        )

        findings = check_s3_public_access_block(s3)

        assert findings == []

    @mock_aws
    def test_no_buckets(self):
        """No buckets at all → no findings."""
        findings = check_s3_public_access_block(_s3())
        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Check 2 — S3 Versioning
# ═══════════════════════════════════════════════════════════════════════════════

class TestS3Versioning:

    @mock_aws
    def test_violation_versioning_disabled(self):
        """Bucket with no versioning → low finding."""
        s3 = _s3()
        s3.create_bucket(Bucket="no-versioning")

        findings = check_s3_versioning(s3)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "low"
        assert "no-versioning" in f["title"]

    @mock_aws
    def test_clean_versioning_enabled(self):
        """Bucket with versioning enabled → no findings."""
        s3 = _s3()
        s3.create_bucket(Bucket="versioned-bucket")
        s3.put_bucket_versioning(
            Bucket="versioned-bucket",
            VersioningConfiguration={"Status": "Enabled"},
        )

        findings = check_s3_versioning(s3)

        assert findings == []

    @mock_aws
    def test_violation_versioning_suspended(self):
        """Bucket with versioning suspended → low finding."""
        s3 = _s3()
        s3.create_bucket(Bucket="suspended-bucket")
        s3.put_bucket_versioning(
            Bucket="suspended-bucket",
            VersioningConfiguration={"Status": "Suspended"},
        )

        findings = check_s3_versioning(s3)

        assert len(findings) == 1
        assert "suspended" in findings[0]["description"].lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Check 3/4/5 — Security Groups
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurityGroups:

    @mock_aws
    def test_violation_all_traffic_open(self):
        """SG with protocol=-1 open to 0.0.0.0/0 → critical finding."""
        ec2 = _ec2()
        sg = ec2.create_security_group(
            GroupName="open-all", Description="All traffic open"
        )
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{
                "IpProtocol": "-1",
                "IpRanges":   [{"CidrIp": "0.0.0.0/0"}],
            }],
        )

        findings = check_security_groups(ec2)

        assert any(
            f["severity"] == "critical" and sg["GroupId"] in f["resource_id"]
            for f in findings
        )

    @mock_aws
    def test_violation_ssh_open(self):
        """SG with port 22 open to 0.0.0.0/0 → high finding."""
        ec2 = _ec2()
        sg = ec2.create_security_group(
            GroupName="ssh-open", Description="SSH open to world"
        )
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort":   22,
                "ToPort":     22,
                "IpRanges":   [{"CidrIp": "0.0.0.0/0"}],
            }],
        )

        findings = check_security_groups(ec2)

        ssh_findings = [f for f in findings if "SSH" in f["title"]]
        assert len(ssh_findings) >= 1
        assert ssh_findings[0]["severity"] == "high"

    @mock_aws
    def test_violation_rdp_open(self):
        """SG with port 3389 open → high finding."""
        ec2 = _ec2()
        sg = ec2.create_security_group(
            GroupName="rdp-open", Description="RDP open"
        )
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort":   3389,
                "ToPort":     3389,
                "IpRanges":   [{"CidrIp": "0.0.0.0/0"}],
            }],
        )

        findings = check_security_groups(ec2)

        rdp_findings = [f for f in findings if "RDP" in f["title"]]
        assert len(rdp_findings) >= 1

    @mock_aws
    def test_clean_restricted_sg(self):
        """SG with only HTTPS open → no findings."""
        ec2 = _ec2()
        sg = ec2.create_security_group(
            GroupName="https-only", Description="HTTPS only"
        )
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort":   443,
                "ToPort":     443,
                "IpRanges":   [{"CidrIp": "0.0.0.0/0"}],
            }],
        )

        findings = check_security_groups(ec2)

        assert findings == []

    @mock_aws
    def test_clean_private_cidr_ssh(self):
        """SG with SSH restricted to private CIDR → no findings."""
        ec2 = _ec2()
        sg = ec2.create_security_group(
            GroupName="private-ssh", Description="SSH from VPC only"
        )
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort":   22,
                "ToPort":     22,
                "IpRanges":   [{"CidrIp": "10.0.0.0/8"}],
            }],
        )

        findings = check_security_groups(ec2)

        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Check 6 — IAM Users Without MFA
# ═══════════════════════════════════════════════════════════════════════════════

class TestIamMfa:

    @mock_aws
    def test_violation_console_user_no_mfa(self):
        """User with login profile but no MFA → high finding."""
        iam = _iam()
        iam.create_user(UserName="alice")
        iam.create_login_profile(UserName="alice", Password="TestPass123!")

        findings = check_iam_mfa(iam)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "high"
        assert "alice" in f["title"]
        assert f["resource_type"] == "IAMUser"

    @mock_aws
    def test_clean_user_no_console_access(self):
        """Programmatic-only user (no login profile) → no findings."""
        iam = _iam()
        iam.create_user(UserName="service-account")
        # No create_login_profile call

        findings = check_iam_mfa(iam)

        assert findings == []

    @mock_aws
    def test_clean_console_user_with_mfa(self):
        """Console user with MFA device → no findings."""
        iam = _iam()
        iam.create_user(UserName="bob")
        iam.create_login_profile(UserName="bob", Password="TestPass123!")
        iam.create_virtual_mfa_device(VirtualMFADeviceName="bob-mfa")
        # Enable the device — moto accepts any TOTP codes in test mode
        iam.enable_mfa_device(
            UserName="bob",
            SerialNumber=f"arn:aws:iam::123456789012:mfa/bob-mfa",
            AuthenticationCode1="123456",
            AuthenticationCode2="789012",
        )

        findings = check_iam_mfa(iam)

        assert findings == []

    @mock_aws
    def test_multiple_users_only_flags_no_mfa(self):
        """Two console users: one with MFA, one without → only one finding."""
        iam = _iam()

        iam.create_user(UserName="secure-user")
        iam.create_login_profile(UserName="secure-user", Password="Secure123!")
        iam.create_virtual_mfa_device(VirtualMFADeviceName="secure-mfa")
        iam.enable_mfa_device(
            UserName="secure-user",
            SerialNumber="arn:aws:iam::123456789012:mfa/secure-mfa",
            AuthenticationCode1="111111",
            AuthenticationCode2="222222",
        )

        iam.create_user(UserName="insecure-user")
        iam.create_login_profile(UserName="insecure-user", Password="Insecure123!")

        findings = check_iam_mfa(iam)

        assert len(findings) == 1
        assert "insecure-user" in findings[0]["title"]


# ═══════════════════════════════════════════════════════════════════════════════
# Check 7 — Root Access Keys
# ═══════════════════════════════════════════════════════════════════════════════

class TestRootAccessKeys:

    def test_violation_root_has_access_keys(self):
        """get_account_summary reports root keys present → critical finding."""
        mock_iam = MagicMock()
        mock_iam.get_account_summary.return_value = {
            "SummaryMap": {"AccountAccessKeysPresent": 1, "AccountMFAEnabled": 1}
        }

        findings = check_root_access_keys(mock_iam)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "critical"
        assert f["resource_id"] == "root-account"
        assert f["resource_type"] == "IAMRootAccount"

    def test_clean_no_root_access_keys(self):
        """get_account_summary reports no root keys → no findings."""
        mock_iam = MagicMock()
        mock_iam.get_account_summary.return_value = {
            "SummaryMap": {"AccountAccessKeysPresent": 0, "AccountMFAEnabled": 1}
        }

        findings = check_root_access_keys(mock_iam)

        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Check 8 — IAM Password Policy
# ═══════════════════════════════════════════════════════════════════════════════

class TestIamPasswordPolicy:

    @mock_aws
    def test_violation_no_password_policy(self):
        """No account password policy (moto default) → medium finding."""
        iam = _iam()

        findings = check_iam_password_policy(iam)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "medium"
        assert f["resource_type"] == "IAMPasswordPolicy"

    @mock_aws
    def test_violation_weak_password_policy(self):
        """Password policy below minimum thresholds → medium finding."""
        iam = _iam()
        iam.update_account_password_policy(
            MinimumPasswordLength=8,  # below 14
            RequireUppercaseCharacters=False,
            RequireLowercaseCharacters=False,
            RequireNumbers=False,
            RequireSymbols=False,
        )

        findings = check_iam_password_policy(iam)

        assert len(findings) == 1
        description = findings[0]["description"].lower()
        assert "minimum length" in description

    @mock_aws
    def test_clean_strong_password_policy(self):
        """Strong password policy meeting all requirements → no findings."""
        iam = _iam()
        iam.update_account_password_policy(
            MinimumPasswordLength=16,
            RequireUppercaseCharacters=True,
            RequireLowercaseCharacters=True,
            RequireNumbers=True,
            RequireSymbols=True,
            MaxPasswordAge=90,
            PasswordReusePrevention=24,
        )

        findings = check_iam_password_policy(iam)

        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Check 9 — CloudTrail
# ═══════════════════════════════════════════════════════════════════════════════

class TestCloudTrail:

    @mock_aws
    def test_violation_no_trails(self):
        """No CloudTrail trails → high finding."""
        ct = _ct()

        findings = check_cloudtrail(ct)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "high"
        assert f["resource_type"] == "CloudTrail"

    @mock_aws
    def test_clean_trail_logging(self):
        """Active CloudTrail trail → no findings."""
        # CloudTrail requires an S3 bucket for the log destination
        s3 = _s3()
        s3.create_bucket(Bucket="my-cloudtrail-logs")

        ct = boto3.client("cloudtrail", region_name=REGION)
        ct.create_trail(
            Name="my-trail",
            S3BucketName="my-cloudtrail-logs",
        )
        ct.start_logging(Name="my-trail")

        findings = check_cloudtrail(ct)

        assert findings == []

    @mock_aws
    def test_violation_trail_not_logging(self):
        """Trail exists but logging is stopped → high finding."""
        s3 = _s3()
        s3.create_bucket(Bucket="trail-logs-stopped")

        ct = boto3.client("cloudtrail", region_name=REGION)
        ct.create_trail(
            Name="stopped-trail",
            S3BucketName="trail-logs-stopped",
        )
        # Don't start logging

        findings = check_cloudtrail(ct)

        assert len(findings) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Check 10 — EBS Encryption
# ═══════════════════════════════════════════════════════════════════════════════

class TestEbsEncryption:

    @mock_aws
    def test_violation_unencrypted_volume(self):
        """Unencrypted EBS volume → medium finding."""
        ec2 = _ec2()
        vol = ec2.create_volume(
            AvailabilityZone=f"{REGION}a",
            Size=20,
            Encrypted=False,
        )

        findings = check_ebs_encryption(ec2)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "medium"
        assert vol["VolumeId"] in f["resource_id"]
        assert f["resource_type"] == "EBSVolume"

    @mock_aws
    def test_clean_encrypted_volume(self):
        """Encrypted EBS volume → no findings."""
        ec2 = _ec2()
        ec2.create_volume(
            AvailabilityZone=f"{REGION}a",
            Size=20,
            Encrypted=True,
        )

        findings = check_ebs_encryption(ec2)

        assert findings == []

    @mock_aws
    def test_mixed_volumes_only_flags_unencrypted(self):
        """Mix of encrypted and unencrypted → only unencrypted is flagged."""
        ec2 = _ec2()
        ec2.create_volume(AvailabilityZone=f"{REGION}a", Size=20, Encrypted=True)
        unenc = ec2.create_volume(AvailabilityZone=f"{REGION}a", Size=10, Encrypted=False)

        findings = check_ebs_encryption(ec2)

        assert len(findings) == 1
        assert unenc["VolumeId"] in findings[0]["resource_id"]


# ═══════════════════════════════════════════════════════════════════════════════
# Check 11 — RDS Publicly Accessible
# ═══════════════════════════════════════════════════════════════════════════════

class TestRdsPublic:

    @mock_aws
    def test_violation_public_rds(self):
        """RDS instance with PubliclyAccessible=True → high finding."""
        rds = _rds()
        rds.create_db_instance(
            DBInstanceIdentifier="public-db",
            DBInstanceClass="db.t3.micro",
            Engine="mysql",
            MasterUsername="admin",
            MasterUserPassword="password123",
            PubliclyAccessible=True,
        )

        findings = check_rds_public(rds)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "high"
        assert "public-db" in f["title"]
        assert f["resource_type"] == "RDSInstance"

    @mock_aws
    def test_clean_private_rds(self):
        """RDS instance with PubliclyAccessible=False → no findings."""
        rds = _rds()
        rds.create_db_instance(
            DBInstanceIdentifier="private-db",
            DBInstanceClass="db.t3.micro",
            Engine="mysql",
            MasterUsername="admin",
            MasterUserPassword="password123",
            PubliclyAccessible=False,
        )

        findings = check_rds_public(rds)

        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Check 12 — GuardDuty
# ═══════════════════════════════════════════════════════════════════════════════

class TestGuardDuty:

    @mock_aws
    def test_violation_guardduty_not_enabled(self):
        """No GuardDuty detectors → medium finding."""
        gd = _gd()

        findings = check_guardduty(gd)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "medium"
        assert f["resource_type"] == "GuardDuty"

    @mock_aws
    def test_clean_guardduty_enabled(self):
        """GuardDuty detector with ENABLED status → no findings."""
        gd = _gd()
        gd.create_detector(Enable=True)

        findings = check_guardduty(gd)

        assert findings == []

    @mock_aws
    def test_violation_guardduty_disabled_detector(self):
        """GuardDuty detector exists but is DISABLED → finding."""
        gd = _gd()
        gd.create_detector(Enable=False)

        findings = check_guardduty(gd)

        assert len(findings) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Check 13 — EC2 Public IP Instances
# ═══════════════════════════════════════════════════════════════════════════════

class TestEc2PublicInstances:

    @mock_aws
    def test_violation_instance_with_public_ip(self):
        """Running EC2 instance with a public IP → low finding."""
        ec2 = _ec2()
        # Find the default AMI that moto provides
        amis = ec2.describe_images(
            Filters=[{"Name": "name", "Values": ["amzn2-ami-hvm-2.0.*"]}]
        )["Images"]
        ami_id = amis[0]["ImageId"] if amis else "ami-12345678"

        # In moto, instances launched into the default VPC get public IPs
        reservation = ec2.run_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
        )
        instance_id = reservation["Instances"][0]["InstanceId"]

        # Manually patch the describe_instances call to include a PublicIpAddress
        # since moto may or may not assign one automatically
        original_ec2 = ec2
        mock_ec2 = MagicMock(wraps=ec2)

        def fake_paginator(operation):
            if operation == "describe_instances":
                pager = MagicMock()
                pager.__iter__ = MagicMock(return_value=iter([{
                    "Reservations": [{
                        "Instances": [{
                            "InstanceId":      instance_id,
                            "PublicIpAddress": "1.2.3.4",
                            "Tags":            [{"Key": "Name", "Value": "web-server"}],
                        }]
                    }]
                }]))
                pager.paginate = MagicMock(return_value=[{
                    "Reservations": [{
                        "Instances": [{
                            "InstanceId":      instance_id,
                            "PublicIpAddress": "1.2.3.4",
                            "Tags":            [{"Key": "Name", "Value": "web-server"}],
                        }]
                    }]
                }])
                return pager
            return original_ec2.get_paginator(operation)

        mock_ec2.get_paginator.side_effect = fake_paginator

        findings = check_ec2_public_instances(mock_ec2)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "low"
        assert f["resource_type"] == "EC2Instance"
        assert "1.2.3.4" in f["description"]

    @mock_aws
    def test_clean_instance_no_public_ip(self):
        """Running EC2 instance without public IP → no findings."""
        ec2 = MagicMock()
        ec2.get_paginator.return_value.paginate.return_value = [{
            "Reservations": [{
                "Instances": [{
                    "InstanceId": "i-abc123",
                    # No PublicIpAddress key
                    "Tags": [],
                }]
            }]
        }]

        findings = check_ec2_public_instances(ec2)

        assert findings == []

    @mock_aws
    def test_clean_no_running_instances(self):
        """No running instances → no findings."""
        ec2 = MagicMock()
        ec2.get_paginator.return_value.paginate.return_value = [
            {"Reservations": []}
        ]

        findings = check_ec2_public_instances(ec2)

        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Check 14 — Root MFA
# ═══════════════════════════════════════════════════════════════════════════════

class TestRootMfa:

    def test_violation_root_no_mfa(self):
        """get_account_summary reports no MFA → critical finding."""
        mock_iam = MagicMock()
        mock_iam.get_account_summary.return_value = {
            "SummaryMap": {"AccountMFAEnabled": 0, "AccountAccessKeysPresent": 0}
        }

        findings = check_root_mfa(mock_iam)

        assert len(findings) == 1
        f = findings[0]
        assert f["severity"] == "critical"
        assert f["resource_id"] == "root-account"

    def test_clean_root_mfa_enabled(self):
        """get_account_summary reports MFA enabled → no findings."""
        mock_iam = MagicMock()
        mock_iam.get_account_summary.return_value = {
            "SummaryMap": {"AccountMFAEnabled": 1, "AccountAccessKeysPresent": 0}
        }

        findings = check_root_mfa(mock_iam)

        assert findings == []


# ═══════════════════════════════════════════════════════════════════════════════
# Scoring
# ═══════════════════════════════════════════════════════════════════════════════

class TestCalculateScore:

    def test_perfect_score_no_findings(self):
        assert calculate_score([]) == (100, "A")

    def test_single_critical_deducts_20(self):
        findings = [{"severity": "critical"}]
        score, grade = calculate_score(findings)
        assert score == 80
        assert grade == "B"  # 80 is in B range (70–84)

    def test_grade_boundaries(self):
        # 85 → A
        assert calculate_score([{"severity": "low"}, {"severity": "low"},
                                 {"severity": "low"}])[1] == "A"  # 100-6=94
        # Force score to 70–84 → B
        highs = [{"severity": "high"}] * 3  # 100-30=70
        assert calculate_score(highs) == (70, "B")

        # Force score to 50–69 → C
        highs5 = [{"severity": "high"}] * 5  # 100-50=50
        assert calculate_score(highs5) == (50, "C")

        # Force score to 30–49 → D
        highs7 = [{"severity": "high"}] * 7  # 100-70=30
        assert calculate_score(highs7) == (30, "D")

        # Force score below 30 → F
        highs8 = [{"severity": "high"}] * 8  # 100-80=20
        assert calculate_score(highs8) == (20, "F")

    def test_score_floor_at_zero(self):
        """Extreme findings should floor at 0, not go negative."""
        findings = [{"severity": "critical"}] * 10  # would be -100
        score, grade = calculate_score(findings)
        assert score == 0
        assert grade == "F"

    def test_mixed_severities(self):
        findings = [
            {"severity": "critical"},  # -20
            {"severity": "high"},      # -10
            {"severity": "medium"},    # -5
            {"severity": "low"},       # -2
        ]
        score, grade = calculate_score(findings)
        assert score == 63   # 100 - 37
        assert grade == "C"


# ═══════════════════════════════════════════════════════════════════════════════
# Integration — run_aws_checks with a fully vulnerable mock environment
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunAwsChecks:

    @mock_aws
    def test_clean_account_returns_findings_from_missing_controls(self):
        """
        An empty AWS account has no GuardDuty, no CloudTrail, no password
        policy → run_aws_checks returns findings for each missing control.
        """
        findings = run_aws_checks(FAKE_CREDS, REGION)

        # Even a "clean" empty account is missing several controls
        severities = {f["severity"] for f in findings}
        resource_types = {f["resource_type"] for f in findings}

        assert len(findings) > 0
        # GuardDuty and CloudTrail are always missing in a fresh mock account
        assert "GuardDuty" in resource_types
        assert "CloudTrail" in resource_types
        # IAM password policy is missing by default
        assert "IAMPasswordPolicy" in resource_types

    @mock_aws
    def test_vulnerable_account_score(self):
        """
        Set up an account with multiple clear violations and verify score is
        well below 85 (not an A).
        """
        s3 = _s3()
        ec2 = _ec2()

        # Unprotected S3 bucket
        s3.create_bucket(Bucket="data-leak")

        # Open SSH security group
        sg = ec2.create_security_group(GroupName="open-ssh", Description="Open SSH")
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort":   22,
                "ToPort":     22,
                "IpRanges":   [{"CidrIp": "0.0.0.0/0"}],
            }],
        )

        # Unencrypted EBS volume
        ec2.create_volume(AvailabilityZone=f"{REGION}a", Size=20, Encrypted=False)

        findings = run_aws_checks(FAKE_CREDS, REGION)
        score, grade = calculate_score(findings)

        assert score < 85
        assert grade in ("B", "C", "D", "F")

    @mock_aws
    def test_finding_schema(self):
        """Every finding must have the required fields."""
        findings = run_aws_checks(FAKE_CREDS, REGION)

        required_keys = {"resource_id", "resource_type", "severity", "title", "description"}
        for f in findings:
            missing = required_keys - f.keys()
            assert not missing, f"Finding missing keys {missing}: {f}"

        valid_severities = {"critical", "high", "medium", "low", "info"}
        for f in findings:
            assert f["severity"] in valid_severities, f"Bad severity: {f['severity']}"
