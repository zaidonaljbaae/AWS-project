"""Load DB connection info from AWS Secrets Manager.

Expected secret value (JSON, case-insensitive keys):
  - username
  - password
  - host
  - port
  - dbname (or database)

This script prints `export ...` lines suitable for `source`.

Security:
  In CI, redirect output to a file to avoid printing secrets in logs:

    python scripts/load_db_secret.py > /tmp/db_env.sh
    source /tmp/db_env.sh

Inputs:
  - DB_SECRET_ARN: required (ARN or name of the Secrets Manager secret)

Outputs (exported):
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_JDBC_URL
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Mapping

import boto3


def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _lower_keys(d: Mapping[str, Any]) -> dict[str, Any]:
    return {str(k).lower(): v for k, v in d.items()}


def _esc_bash_single_quote(v: str) -> str:
    # safe single-quote for bash: ' -> '"'"'
    return v.replace("'", "'\"'\"'")


def main() -> None:
    secret_id = os.getenv("DB_SECRET_ARN")
    if not secret_id:
        _die("DB_SECRET_ARN is required")

    sm = boto3.client("secretsmanager")
    try:
        resp = sm.get_secret_value(SecretId=secret_id)
    except Exception as exc:
        _die(f"Failed to read secret {secret_id}: {exc}")

    secret_str = resp.get("SecretString")
    if not secret_str:
        _die("SecretString is empty (binary secrets are not supported here)")

    try:
        obj = json.loads(secret_str)
    except json.JSONDecodeError as exc:
        _die(f"SecretString is not valid JSON: {exc}")

    if not isinstance(obj, dict):
        _die("Secret JSON must be an object")

    d = _lower_keys(obj)

    host = str(d.get("host") or "").strip()
    port = str(d.get("port") or "").strip()
    name = str(d.get("dbname") or d.get("database") or d.get("db_name") or "").strip()
    user = str(d.get("username") or d.get("user") or "").strip()
    password = str(d.get("password") or "").strip()

    missing = [k for k, v in [("host", host), ("port", port), ("dbname", name), ("username", user), ("password", password)] if not v]
    if missing:
        _die(f"Secret is missing required keys: {', '.join(missing)}")

    jdbc = f"jdbc:postgresql://{host}:{port}/{name}"

    print(f"export DB_HOST='{_esc_bash_single_quote(host)}'")
    print(f"export DB_PORT='{_esc_bash_single_quote(port)}'")
    print(f"export DB_NAME='{_esc_bash_single_quote(name)}'")
    print(f"export DB_USER='{_esc_bash_single_quote(user)}'")
    print(f"export DB_PASSWORD='{_esc_bash_single_quote(password)}'")
    print(f"export DB_JDBC_URL='{_esc_bash_single_quote(jdbc)}'")


if __name__ == "__main__":
    main()
