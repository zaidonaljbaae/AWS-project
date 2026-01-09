# Example API

## Public (no auth)
- GET  /example_api/public/health
- GET  /example_api/public/items?limit=20
- POST /example_api/public/items  {"name":"test"}

## Private (Cognito)
- GET /example_api/private/me

## Database migrations (Flyway)
This project uses **Flyway** (not Alembic).

Run:
```bash
export FLYWAY_URL="jdbc:postgresql://<HOST>:5432/<DB>"
export FLYWAY_USER="<USER>"
export FLYWAY_PASSWORD="<PASS>"
./flyway/run_flyway.sh migrate
```

Migrations:
- `flyway/sql/V1__create_example_items.sql`
