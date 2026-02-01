"""
Read selected stage params from serverless.yml and print them as `export ...` lines.

Security note:
  - Do NOT store plaintext passwords in serverless.yml.
  - Only extract non-sensitive values (e.g., ARNs, VPC/Subnet/SG IDs).

Usage:
  STAGE=dev python scripts/read_params_from_serverless.py
  eval "$(STAGE=dev python scripts/read_params_from_serverless.py)"

Output:
  Prints `export ...` lines suitable for `source`/`eval`.
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
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
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


def _strip_quotes(val: str) -> str:
    val = val.strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val


def _get_scalar(body: str, key: str, required: bool = True) -> Optional[str]:
    mm = re.search(rf"^\s+{re.escape(key)}:\s*(.+)\s*$", body, re.MULTILINE)
    if not mm:
        if required:
            _die(f"Missing {key} in params")
        return None
    return _strip_quotes(mm.group(1).strip())


def _get_list(body: str, key: str, required: bool = True) -> Optional[List[str]]:
    # Match:
    #   KEY:
    #     - item1
    #     - item2
    head = re.search(rf"^\s+{re.escape(key)}:\s*$", body, re.MULTILINE)
    if not head:
        if required:
            _die(f"Missing {key} in params")
        return None

    # Capture list items that follow, indented further and starting with "-"
    start = head.end()
    tail = body[start:]
    items = []
    for line in tail.splitlines():
        # stop when indentation returns to param-level (2 spaces under stage) or empty stage content ends
        if re.match(r"^\s{4}\S", line):  # next key at same level
            break
        m = re.match(r"^\s*-\s*(.+)\s*$", line)
        if m:
            items.append(_strip_quotes(m.group(1)))
        # ignore non "- ..." lines (blank lines, comments)
    if not items and required:
        _die(f"{key} list is empty or malformed in params")
    return items or None


def _esc(v: str) -> str:
    # safe single-quote for bash: ' -> '"'"'
    return v.replace("'", "'\"'\"'")


def _emit(name: str, value: str) -> None:
    print(f"export {name}='{_esc(value)}'")


def main() -> None:
    stage = os.getenv("STAGE", "dev")
    y = _read_file("serverless.yml")
    body = _find_stage_block(y, stage)

    # Scalars (safe to export)
    for k in [
        "DB_SECRET_ARN",
        "ALB_SG_ID",
        "VPC_ID",
    ]:
        v = _get_scalar(body, k, required=False)
        if v:
            _emit(k, v)

    # Lists -> export as CSV (useful for CDK env vars)
    alb_subnets = _get_list(body, "SUBNETIDS", required=False)
    if alb_subnets:
        _emit("ALB_SUBNET_IDS_CSV", ",".join(alb_subnets))


if __name__ == "__main__":
    main()
