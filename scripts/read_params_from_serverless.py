"""
Read selected stage params from serverless.yml.

Security note:
  - Do NOT store plaintext passwords in serverless.yml.
  - This script only extracts non-sensitive values (e.g., DB_SECRET_ARN).

Usage:
  STAGE=dev python scripts/read_params_from_serverless.py

Output:
  Prints `export ...` lines suitable for `source`/`eval`.

What it supports:
  - Scalar values under params.<stage> (e.g., DB_SECRET_ARN)
  - List values under params.<stage> (e.g., SUBNETIDS: - subnet-... - subnet-...)
    -> exported as CSV for CDK usage (ALB_SUBNET_IDS) and/or generic usage (SUBNETIDS_CSV)
"""

from __future__ import annotations

import os
import re
import sys
from typing import List, Optional


def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _read_file(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8").read()
    except FileNotFoundError:
        _die(f"{path} not found")


def _find_stage_block(yaml_text: str, stage: str) -> str:
    """
    Extract the indented block under:
      params:
        <stage>:
          ...
    Returns only the body under params.<stage> (still indented).
    """
    if not re.search(r"^params:\s*$", yaml_text, re.MULTILINE):
        _die("params: section not found in serverless.yml")

    # This pattern looks for:
    #   <stage>:
    #     ...
    # It assumes typical indentation:
    # params:
    #   dev:
    #     KEY: value
    pattern = rf"^\s{{2}}{re.escape(stage)}:\s*\n(?P<body>(?:^\s{{4,}}.*\n)+)"
    m = re.search(pattern, yaml_text, re.MULTILINE)
    if not m:
        _die(f"params.{stage} not found")
    return m.group("body")


def _strip_quotes(val: str) -> str:
    v = val.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def _get_scalar(body: str, key: str, required: bool = True) -> Optional[str]:
    """
    Match scalar:
      KEY: value
    """
    mm = re.search(rf"^\s+{re.escape(key)}:\s*(.+)\s*$", body, re.MULTILINE)
    if not mm:
        if required:
            _die(f"Missing {key} in params")
        return None
    return _strip_quotes(mm.group(1))


def _get_list(body: str, key: str, required: bool = False) -> List[str]:
    """
    Match list:
      KEY:
        - item1
        - item2
    Returns [] if not found and required=False.
    """
    # Find the "KEY:" line
    key_line = re.search(rf"^\s+{re.escape(key)}:\s*$", body, re.MULTILINE)
    if not key_line:
        if required:
            _die(f"Missing {key} list in params")
        return []

    # Starting from the end of the key line, capture subsequent "- ..." lines with deeper indentation
    start = key_line.end()
    tail = body[start:]

    items: List[str] = []
    for line in tail.splitlines():
        # stop when indentation goes back to the same level as keys (4 spaces) and it's not a list item
        # Typical:
        # "    OTHERKEY: ..."
        if re.match(r"^\s{4}\S", line) and not re.match(r"^\s{6,}-\s+", line):
            break

        m = re.match(r"^\s*-\s*(.+)\s*$", line)
        if m:
            items.append(_strip_quotes(m.group(1)))

    return [x.strip() for x in items if x.strip()]


def _esc(v: str) -> str:
    # safe single-quote for bash: ' -> '"'"'
    return v.replace("'", "'\"'\"'")


def main() -> None:
    stage = os.getenv("STAGE", "dev")
    y = _read_file("serverless.yml")
    body = _find_stage_block(y, stage)

    # 1) Optional scalar: DB_SECRET_ARN
    db_secret_arn = _get_scalar(body, "DB_SECRET_ARN", required=False)
    if db_secret_arn:
        print(f"export DB_SECRET_ARN='{_esc(db_secret_arn)}'")

    # 2) Optional list: SUBNETIDS (YAML list)
    subnet_ids = _get_list(body, "SUBNETIDS", required=False)
    if subnet_ids:
        csv = ",".join(subnet_ids)
        # Recommended name for CDK to consume ALB subnets:
        print(f"export ALB_SUBNET_IDS='{_esc(csv)}'")
        # Generic name if you still want it elsewhere:
        print(f"export SUBNETIDS_CSV='{_esc(csv)}'")
    else:
        # Set empty vars to avoid unbound errors in bash if you use -u
        print("export ALB_SUBNET_IDS=''")
        print("export SUBNETIDS_CSV=''")


if __name__ == "__main__":
    main()
