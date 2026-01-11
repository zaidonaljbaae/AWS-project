#!/usr/bin/env bash
set -euo pipefail

# Build per-Lambda vendored dependencies under src/app/<lambda>/vendor.
# This mirrors the CI step in pipeline/buildspec-serverless.yml.

PYTHON_BIN=${PYTHON_BIN:-python3}

for svc in src/app/*; do
  if [[ -f "$svc/requirements.txt" ]]; then
    echo "[build_vendors] Installing requirements for $svc"
    rm -rf "$svc/vendor"
    mkdir -p "$svc/vendor"
    "$PYTHON_BIN" -m pip install -r "$svc/requirements.txt" -t "$svc/vendor"
  fi
done

echo "[build_vendors] Done. You can now run: sls deploy --stage <stage> --region <region>"
