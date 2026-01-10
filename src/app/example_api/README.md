# Example API (Lambda + HTTP API)

Routes:
- `GET  /api/health`
- `GET  /api/echo` (returns request context)
- `POST /api/echo` (returns request context + JSON body)
- `GET  /api/private/me` (placeholder "auth" example)

## Notes
- This is a template service intentionally kept minimal.
- To add real authentication, configure a JWT authorizer in API Gateway (HTTP API) and/or validate tokens in code.
- To add DB access, set `DB_URL` in Serverless params or via SSM/Secrets.
