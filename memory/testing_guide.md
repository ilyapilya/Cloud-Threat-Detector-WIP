---
name: Testing Guide
description: How to run the moto-based AWS scanner test suite — commands, setup, and what each test covers
type: reference
---

# Running Tests

## Quick run (from repo root)

```bash
pytest -v
```

`pyproject.toml` has `testpaths = ["backend/tests"]` and `pythonpath = ["backend"]` so no path argument is needed.

## First-time setup

```bash
# Install dev dependencies into whichever Python pytest uses
C:/Python/Python311/python.exe -m pip install -r backend/requirements-dev.txt
```

Check which Python pytest is using if tests fail to import: look at the first line of pytest output — `python.exe --` shows the executable path. Install dependencies to that same interpreter.

## Targeted runs

```bash
pytest -v -k "S3"                  # only S3 checks
pytest -v -k "score"               # only scoring tests
pytest -v -k "violation"           # only violation cases
pytest -v backend/tests/test_aws_checks.py::TestGuardDuty
```

## Files

| File | Purpose |
|---|---|
| `backend/tests/conftest.py` | Sets fake AWS env vars (`AWS_ACCESS_KEY_ID=testing` etc.) before any import |
| `backend/tests/test_aws_checks.py` | 45 tests across all 14 checks + scoring + integration |
| `backend/requirements-dev.txt` | `pytest>=8.0.0`, `moto[all]>=5.0.0` |

## How moto works

`@mock_aws` intercepts all boto3 calls for the duration of the test — no real AWS credentials needed, no network calls made. Each test gets a fresh, empty mock AWS account. State does not leak between tests.

Root account checks (`check_root_access_keys`, `check_root_mfa`) use `unittest.mock.MagicMock` directly because moto's `get_account_summary` returns fixed defaults that can't be configured.

## Test structure per check

Every check has:
- **violation test** — mock AWS state that produces a finding; asserts severity, resource_type, and key title/description content
- **clean test** — mock AWS state that produces no findings

## Adding a new check

1. Write the check function in `backend/app/scanner/aws_checks.py`
2. Add it to `run_aws_checks()` in the same file
3. Add a test class in `backend/tests/test_aws_checks.py` following the same pattern:
   - `@mock_aws` decorator on each test method
   - Create boto3 client with the module-level helper (`_s3()`, `_iam()`, etc.)
   - Set up mock AWS resources, call the check function directly, assert findings