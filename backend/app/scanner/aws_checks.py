"""
AWS Security Checks
14 high-impact checks covering S3, EC2/SGs, IAM, CloudTrail, EBS, RDS, GuardDuty.
Each check returns a list of finding dicts; errors are caught per-check so one
failed check never aborts the rest of the scan.
"""

import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Any, Tuple


# ── Helpers ──────────────────────────────────────────────────────────────────

def _client(service: str, creds: dict, region: str):
    return boto3.client(
        service,
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
        region_name=region,
    )


def validate_credentials(creds: dict) -> Tuple[bool, str]:
    """Return (is_valid, caller_arn_or_error). Uses STS GetCallerIdentity."""
    try:
        sts = _client("sts", creds, creds.get("region", "us-east-1"))
        identity = sts.get_caller_identity()
        return True, identity.get("Arn", "")
    except ClientError as e:
        return False, str(e)


# ── Check 1: S3 — Public Access Block ────────────────────────────────────────

def check_s3_public_access_block(s3) -> List[Dict]:
    findings = []
    try:
        buckets = s3.list_buckets().get("Buckets", [])
    except ClientError:
        return findings

    for bucket in buckets:
        name = bucket["Name"]
        try:
            cfg = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
            if not all([
                cfg.get("BlockPublicAcls"),
                cfg.get("IgnorePublicAcls"),
                cfg.get("BlockPublicPolicy"),
                cfg.get("RestrictPublicBuckets"),
            ]):
                findings.append({
                    "resource_id":   f"arn:aws:s3:::{name}",
                    "resource_type": "S3Bucket",
                    "region":        "global",
                    "severity":      "critical",
                    "title":         f'S3 bucket "{name}" has public access partially unblocked',
                    "description":   (
                        f'Bucket "{name}" has an incomplete public access block. '
                        "One or more settings (BlockPublicAcls, IgnorePublicAcls, "
                        "BlockPublicPolicy, RestrictPublicBuckets) are disabled, "
                        "potentially exposing bucket contents to the internet."
                    ),
                })
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                findings.append({
                    "resource_id":   f"arn:aws:s3:::{name}",
                    "resource_type": "S3Bucket",
                    "region":        "global",
                    "severity":      "critical",
                    "title":         f'S3 bucket "{name}" has no public access block configured',
                    "description":   (
                        f'Bucket "{name}" has no public access block configuration. '
                        "Without this, bucket ACLs and policies may grant public access. "
                        "Enable all four public access block settings immediately."
                    ),
                })
    return findings


# ── Check 2: S3 — Versioning ─────────────────────────────────────────────────

def check_s3_versioning(s3) -> List[Dict]:
    findings = []
    try:
        buckets = s3.list_buckets().get("Buckets", [])
    except ClientError:
        return findings

    for bucket in buckets:
        name = bucket["Name"]
        try:
            status = s3.get_bucket_versioning(Bucket=name).get("Status", "")
            if status != "Enabled":
                findings.append({
                    "resource_id":   f"arn:aws:s3:::{name}",
                    "resource_type": "S3Bucket",
                    "region":        "global",
                    "severity":      "low",
                    "title":         f'S3 bucket "{name}" does not have versioning enabled',
                    "description":   (
                        f'Bucket "{name}" has versioning {"suspended" if status == "Suspended" else "disabled"}. '
                        "Without versioning, accidentally deleted or overwritten objects "
                        "cannot be recovered."
                    ),
                })
        except ClientError:
            pass
    return findings


# ── Check 3 & 4 & 5: Security Groups ─────────────────────────────────────────

_DANGEROUS_PORTS: Dict[int, Tuple[str, str]] = {
    22:    ("SSH",           "high"),
    3389:  ("RDP",           "high"),
    1433:  ("MSSQL",         "high"),
    3306:  ("MySQL",         "high"),
    5432:  ("PostgreSQL",    "high"),
    27017: ("MongoDB",       "high"),
    6379:  ("Redis",         "high"),
    9200:  ("Elasticsearch", "high"),
    9300:  ("Elasticsearch", "high"),
}
_OPEN_CIDRS = {"0.0.0.0/0", "::/0"}


def check_security_groups(ec2) -> List[Dict]:
    findings = []
    try:
        paginator = ec2.get_paginator("describe_security_groups")
        for page in paginator.paginate():
            for sg in page["SecurityGroups"]:
                sg_id   = sg["GroupId"]
                sg_name = sg.get("GroupName", sg_id)

                for rule in sg.get("IpPermissions", []):
                    protocol  = rule.get("IpProtocol", "-1")
                    from_port = rule.get("FromPort")
                    to_port   = rule.get("ToPort")

                    cidrs = (
                        [r["CidrIp"]   for r in rule.get("IpRanges", [])] +
                        [r["CidrIpv6"] for r in rule.get("Ipv6Ranges", [])]
                    )
                    open_cidrs = [c for c in cidrs if c in _OPEN_CIDRS]
                    if not open_cidrs:
                        continue

                    # All traffic from the internet (protocol = -1)
                    if protocol == "-1":
                        findings.append({
                            "resource_id":   sg_id,
                            "resource_type": "SecurityGroup",
                            "region":        None,
                            "severity":      "critical",
                            "title":         f'Security group "{sg_name}" allows all inbound traffic from the internet',
                            "description":   (
                                f"Security group {sg_id} ({sg_name}) permits all protocols and ports "
                                f"from {', '.join(open_cidrs)}. This is equivalent to no firewall. "
                                "Restrict inbound rules to only the ports and IP ranges your "
                                "application requires."
                            ),
                        })
                        continue

                    # Specific dangerous ports
                    for port, (service, severity) in _DANGEROUS_PORTS.items():
                        port_in_range = (
                            from_port is None or
                            (from_port <= port <= (to_port if to_port is not None else port))
                        )
                        if port_in_range:
                            findings.append({
                                "resource_id":   sg_id,
                                "resource_type": "SecurityGroup",
                                "region":        None,
                                "severity":      severity,
                                "title":         (
                                    f'Security group "{sg_name}" allows {service} '
                                    f"(port {port}) from the internet"
                                ),
                                "description":   (
                                    f"Security group {sg_id} ({sg_name}) allows inbound {service} "
                                    f"(port {port}) from {', '.join(open_cidrs)}. "
                                    "Restrict this rule to known, trusted IP ranges or use a bastion host."
                                ),
                            })
    except ClientError:
        pass
    return findings


# ── Check 6: IAM — Users Without MFA ─────────────────────────────────────────

def check_iam_mfa(iam) -> List[Dict]:
    findings = []
    try:
        paginator = iam.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page["Users"]:
                username = user["UserName"]
                try:
                    # Only flag users with console (password) access
                    iam.get_login_profile(UserName=username)
                except ClientError:
                    continue  # no console access, skip

                try:
                    mfa_devices = iam.list_mfa_devices(UserName=username)["MFADevices"]
                    if not mfa_devices:
                        findings.append({
                            "resource_id":   user["Arn"],
                            "resource_type": "IAMUser",
                            "region":        "global",
                            "severity":      "high",
                            "title":         f'IAM user "{username}" has console access but no MFA',
                            "description":   (
                                f'IAM user "{username}" can log into the AWS console but has '
                                "no MFA device registered. If credentials are leaked, the account "
                                "can be accessed with just a password. Enable MFA immediately."
                            ),
                        })
                except ClientError:
                    pass
    except ClientError:
        pass
    return findings


# ── Check 7: IAM — Root Access Keys ──────────────────────────────────────────

def check_root_access_keys(iam) -> List[Dict]:
    findings = []
    try:
        summary = iam.get_account_summary()["SummaryMap"]
        if summary.get("AccountAccessKeysPresent", 0) > 0:
            findings.append({
                "resource_id":   "root-account",
                "resource_type": "IAMRootAccount",
                "region":        "global",
                "severity":      "critical",
                "title":         "Root account has active access keys",
                "description":   (
                    "The AWS root account has active programmatic access keys. Root keys provide "
                    "unrestricted access to every service in your account and cannot be scoped "
                    "with IAM policies. Delete them immediately and use least-privilege IAM "
                    "roles instead."
                ),
            })
    except ClientError:
        pass
    return findings


# ── Check 8: IAM — Password Policy ───────────────────────────────────────────

def check_iam_password_policy(iam) -> List[Dict]:
    findings = []
    try:
        policy = iam.get_account_password_policy()["PasswordPolicy"]
        issues = []
        if policy.get("MinimumPasswordLength", 0) < 14:
            issues.append(f"minimum length is {policy.get('MinimumPasswordLength', 0)} (should be ≥ 14)")
        if not policy.get("RequireUppercaseCharacters"):
            issues.append("uppercase not required")
        if not policy.get("RequireLowercaseCharacters"):
            issues.append("lowercase not required")
        if not policy.get("RequireNumbers"):
            issues.append("numbers not required")
        if not policy.get("RequireSymbols"):
            issues.append("symbols not required")
        if not policy.get("MaxPasswordAge"):
            issues.append("no password rotation enforced")
        if not policy.get("PasswordReusePrevention"):
            issues.append("password reuse not prevented")
        if issues:
            findings.append({
                "resource_id":   "iam-password-policy",
                "resource_type": "IAMPasswordPolicy",
                "region":        "global",
                "severity":      "medium",
                "title":         "IAM password policy does not meet security best practices",
                "description":   f"Password policy weaknesses: {'; '.join(issues)}.",
            })
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            findings.append({
                "resource_id":   "iam-password-policy",
                "resource_type": "IAMPasswordPolicy",
                "region":        "global",
                "severity":      "medium",
                "title":         "No IAM password policy is configured",
                "description":   (
                    "No IAM account password policy is set. AWS uses a minimal default. "
                    "Configure a policy requiring length ≥ 14, mixed case, numbers, symbols, "
                    "expiry, and reuse prevention."
                ),
            })
    return findings


# ── Check 9: CloudTrail ───────────────────────────────────────────────────────

def check_cloudtrail(ct) -> List[Dict]:
    findings = []
    try:
        trails = ct.describe_trails(includeShadowTrails=False).get("trailList", [])
        active = False
        for trail in trails:
            try:
                if ct.get_trail_status(Name=trail["TrailARN"]).get("IsLogging"):
                    active = True
                    break
            except ClientError:
                pass
        if not active:
            findings.append({
                "resource_id":   "cloudtrail",
                "resource_type": "CloudTrail",
                "region":        None,
                "severity":      "high",
                "title":         "CloudTrail is not logging in this region",
                "description":   (
                    "No active CloudTrail trail found. Without CloudTrail you have no audit "
                    "log of API calls made in your account, making it impossible to detect "
                    "unauthorized activity or investigate security incidents after the fact."
                ),
            })
    except ClientError:
        pass
    return findings


# ── Check 10: EBS — Unencrypted Volumes ──────────────────────────────────────

def check_ebs_encryption(ec2) -> List[Dict]:
    findings = []
    try:
        paginator = ec2.get_paginator("describe_volumes")
        for page in paginator.paginate():
            for vol in page["Volumes"]:
                if not vol.get("Encrypted"):
                    attachments = vol.get("Attachments", [])
                    attached_to = attachments[0]["InstanceId"] if attachments else "unattached"
                    findings.append({
                        "resource_id":   vol["VolumeId"],
                        "resource_type": "EBSVolume",
                        "region":        None,
                        "severity":      "medium",
                        "title":         f'EBS volume "{vol["VolumeId"]}" is not encrypted',
                        "description":   (
                            f'Volume {vol["VolumeId"]} (state: {vol.get("State")}, '
                            f"attached to: {attached_to}) is unencrypted. "
                            "Unencrypted EBS volumes expose data if snapshots are inadvertently "
                            "shared or if the underlying hardware is accessed."
                        ),
                    })
    except ClientError:
        pass
    return findings


# ── Check 11: RDS — Publicly Accessible ──────────────────────────────────────

def check_rds_public(rds) -> List[Dict]:
    findings = []
    try:
        paginator = rds.get_paginator("describe_db_instances")
        for page in paginator.paginate():
            for db in page["DBInstances"]:
                if db.get("PubliclyAccessible"):
                    findings.append({
                        "resource_id":   db["DBInstanceArn"],
                        "resource_type": "RDSInstance",
                        "region":        None,
                        "severity":      "high",
                        "title":         f'RDS instance "{db["DBInstanceIdentifier"]}" is publicly accessible',
                        "description":   (
                            f'RDS instance "{db["DBInstanceIdentifier"]}" '
                            f'({db.get("Engine")} {db.get("EngineVersion", "")}) is reachable '
                            "from the public internet. Database instances should only be accessible "
                            "from within your VPC. Disable public accessibility and use a private "
                            "subnet with VPC security groups."
                        ),
                    })
    except ClientError:
        pass
    return findings


# ── Check 12: GuardDuty — Not Enabled ────────────────────────────────────────

def check_guardduty(gd) -> List[Dict]:
    findings = []
    try:
        detector_ids = gd.list_detectors().get("DetectorIds", [])
        active = any(
            gd.get_detector(DetectorId=d).get("Status") == "ENABLED"
            for d in detector_ids
        )
        if not active:
            findings.append({
                "resource_id":   "guardduty",
                "resource_type": "GuardDuty",
                "region":        None,
                "severity":      "medium",
                "title":         "AWS GuardDuty is not enabled in this region",
                "description":   (
                    "GuardDuty is not enabled. It provides intelligent threat detection by "
                    "continuously analyzing CloudTrail, VPC Flow Logs, and DNS logs for "
                    "malicious activity, credential compromise, and unauthorized behavior. "
                    "It has a 30-day free trial and costs pennies for most accounts."
                ),
            })
    except ClientError:
        pass
    return findings


# ── Check 13: EC2 — Instances with Public IPs ────────────────────────────────

def check_ec2_public_instances(ec2) -> List[Dict]:
    findings = []
    try:
        paginator = ec2.get_paginator("describe_instances")
        for page in paginator.paginate(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        ):
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    if inst.get("PublicIpAddress"):
                        name = next(
                            (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
                            inst["InstanceId"],
                        )
                        findings.append({
                            "resource_id":   inst["InstanceId"],
                            "resource_type": "EC2Instance",
                            "region":        None,
                            "severity":      "low",
                            "title":         f'EC2 instance "{name}" has a public IP address',
                            "description":   (
                                f'Instance {inst["InstanceId"]} ({name}) is running with public IP '
                                f'{inst["PublicIpAddress"]}. Public IPs increase attack surface. '
                                "Consider placing instances behind a load balancer or NAT gateway."
                            ),
                        })
    except ClientError:
        pass
    return findings


# ── Check 14: IAM — Root MFA ─────────────────────────────────────────────────

def check_root_mfa(iam) -> List[Dict]:
    findings = []
    try:
        summary = iam.get_account_summary()["SummaryMap"]
        if not summary.get("AccountMFAEnabled", 0):
            findings.append({
                "resource_id":   "root-account",
                "resource_type": "IAMRootAccount",
                "region":        "global",
                "severity":      "critical",
                "title":         "Root account does not have MFA enabled",
                "description":   (
                    "The AWS root account has no MFA device registered. Anyone who obtains "
                    "the root password can take full control of your account. Enable a virtual "
                    "or hardware MFA device on the root account immediately."
                ),
            })
    except ClientError:
        pass
    return findings


# ── Scoring ───────────────────────────────────────────────────────────────────

_WEIGHTS = {"critical": 20, "high": 10, "medium": 5, "low": 2, "info": 0}


def calculate_score(findings: List[Dict]) -> Tuple[int, str]:
    deductions = sum(_WEIGHTS.get(f["severity"], 0) for f in findings)
    score = max(0, 100 - deductions)
    grade = (
        "A" if score >= 85 else
        "B" if score >= 70 else
        "C" if score >= 50 else
        "D" if score >= 30 else
        "F"
    )
    return score, grade


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_aws_checks(creds: dict, region: str) -> List[Dict]:
    """
    Run all 14 checks against the given AWS credentials.
    Global resources (IAM, S3) always use us-east-1.
    Regional resources use the caller-specified region.
    Errors in individual checks are caught internally — a failed check
    returns an empty list rather than aborting the scan.
    """
    def mk(service: str, svc_region: str = None):
        return _client(service, creds, svc_region or region)

    s3  = mk("s3",  "us-east-1")
    iam = mk("iam", "us-east-1")
    ec2 = mk("ec2")
    ct  = mk("cloudtrail")
    rds = mk("rds")
    gd  = mk("guardduty")

    all_findings: List[Dict] = []
    all_findings += check_root_access_keys(iam)
    all_findings += check_root_mfa(iam)
    all_findings += check_iam_mfa(iam)
    all_findings += check_iam_password_policy(iam)
    all_findings += check_s3_public_access_block(s3)
    all_findings += check_s3_versioning(s3)
    all_findings += check_security_groups(ec2)
    all_findings += check_ec2_public_instances(ec2)
    all_findings += check_ebs_encryption(ec2)
    all_findings += check_cloudtrail(ct)
    all_findings += check_rds_public(rds)
    all_findings += check_guardduty(gd)

    return all_findings
