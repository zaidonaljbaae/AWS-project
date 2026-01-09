#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run_flyway.sh migrate
# Env vars required:
#   FLYWAY_URL=jdbc:postgresql://host:5432/db
#   FLYWAY_USER=user
#   FLYWAY_PASSWORD=pass
# Optional:
#   FLYWAY_CMD=migrate|info|validate|repair|clean (avoid clean in prod)

CMD="${1:-migrate}"

docker run --rm \
  -e FLYWAY_URL="${FLYWAY_URL}" \
  -e FLYWAY_USER="${FLYWAY_USER}" \
  -e FLYWAY_PASSWORD="${FLYWAY_PASSWORD}" \
  -v "$(pwd)/flyway/sql:/flyway/sql" \
  -v "$(pwd)/flyway/flyway.conf:/flyway/conf/flyway.conf" \
  flyway/flyway:10 \
  ${CMD}
