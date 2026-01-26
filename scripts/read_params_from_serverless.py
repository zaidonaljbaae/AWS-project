"""Read selected stage params from serverless.yml.

Security note:
  - Do NOT store plaintext passwords in serverless.yml.
  - This script only extracts non-sensitive values (e.g., DB_SECRET_ARN).

Usage:
  STAGE=dev python scripts/read_params_from_serverless.py

Output:
  Prints `export ...` lines suitable for `source`/`eval`.
"""

from __future__ import annotations

import os
import re
import sys


def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _read_file(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8").read()
    except FileNotFoundError:
        _die(f"{path} not found")


def _find_stage_block(yaml_text: str, stage: str) -> str:
    if not re.search(r"^params:\s*$", yaml_text, re.MULTILINE):
        _die("params: section not found in serverless.yml")

    # Match:
    # params:
    #   dev:
    #     KEY: value
    pattern = rf"^\s{{2}}{re.escape(stage)}:\s*\n(?P<body>(?:^\s{{4,}}.*\n)+)"
    m = re.search(pattern, yaml_text, re.MULTILINE)
    if not m:
        _die(f"params.{stage} not found")
    return m.group("body")


def _get(body: str, key: str, required: bool = True) -> str | None:
    mm = re.search(rf"^\s+{re.escape(key)}:\s*(.+)\s*$", body, re.MULTILINE)
    if not mm:
        if required:
            _die(f"Missing {key} in params")
        return None
    val = mm.group(1).strip()
    # Strip quotes
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return val


def _esc(v: str) -> str:
    # safe single-quote for bash: ' -> '"'"'
    return v.replace("'", "'\"'\"'")


def main() -> None:
    stage = os.getenv("STAGE", "dev")
    y = _read_file("serverless.yml")
    body = _find_stage_block(y, stage)

    db_secret_arn = _get(body, "DB_SECRET_ARN", required=False)
    if db_secret_arn:
        print(f"export DB_SECRET_ARN='{_esc(db_secret_arn)}'")


if __name__ == "__main__":
    main()
