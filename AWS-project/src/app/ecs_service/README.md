# ECS Service (Flask) — Test App

This is a minimal Flask application intended to run on **ECS Fargate** for:
- long-running HTTP requests (no Lambda 15-minute timeout)
- basic health checks
- CloudWatch logging validation

## Endpoints
- `GET /health`
- `GET /long-task?seconds=120`  (demo: sleeps and logs start/end)

## Local run
```bash
docker build -t dlm-ecs-service:dev .
docker run -p 8000:8000 dlm-ecs-service:dev
```
