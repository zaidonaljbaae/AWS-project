# scripts/read_db_from_serverless.py
import os, re, sys

stage = os.getenv("STAGE", "dev")
path = "serverless.yml"

try:
    y = open(path, "r", encoding="utf-8").read()
except FileNotFoundError:
    print("ERROR: serverless.yml not found", file=sys.stderr)
    sys.exit(1)

if not re.search(r"^params:\s*$", y, re.MULTILINE):
    print("ERROR: params: section not found in serverless.yml", file=sys.stderr)
    sys.exit(1)

pattern = rf"^\s{{2}}{re.escape(stage)}:\s*\n(?P<body>(?:^\s{{4,}}.*\n)+)"
m = re.search(pattern, y, re.MULTILINE)
if not m:
    print(f"ERROR: params.{stage} not found in serverless.yml", file=sys.stderr)
    sys.exit(1)

body = m.group("body")

def get(key: str) -> str:
    mm = re.search(rf"^\s+{re.escape(key)}:\s*(.+)\s*$", body, re.MULTILINE)
    if not mm:
        print(f"ERROR: Missing {key} in params.{stage}", file=sys.stderr)
        sys.exit(1)
    val = mm.group(1).strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return val

host = get("DB_HOST")
port = get("DB_PORT")
name = get("DB_NAME")
user = get("DB_USER")
pwd  = get("DB_PASSWORD")

def esc(v: str) -> str:
    return v.replace("'", "'\"'\"'")

print(f"export DB_HOST='{esc(host)}'")
print(f"export DB_PORT='{esc(port)}'")
print(f"export DB_NAME='{esc(name)}'")
print(f"export DB_USER='{esc(user)}'")
print(f"export DB_PASSWORD='{esc(pwd)}'")
print(f"export DB_JDBC_URL='jdbc:postgresql://{esc(host)}:{esc(port)}/{esc(name)}'")
