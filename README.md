# AWS Microservices Template (Serverless + ECS)

A generic, production-minded starter repository that demonstrates:
- **Lambda + API Gateway (HTTP API)** for fast, event-driven APIs
- **ECS Fargate** for containerized services / longer-running workloads
- Optional **DB** integration (via `DB_URL`) and optional **S3** integration

## What is included
- `src/app/example_api` (Lambda + Flask via `serverless-wsgi`)
- `src/app/print_lambda` (simple Lambda that prints to CloudWatch)
- `src/app/ecs_service` (simple Flask container for ECS)
- `serverless.yml` (safe defaults; no credentials in repo)
- `infra/cdk` (CDK stack to deploy ECS + ALB; creates a VPC by default)

## Quick start (local)
```bash
cd src
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Deploy (Serverless)
```bash
npm install
npx serverless deploy --stage dev --region us-east-1
```

## Deploy (CDK / ECS)
```bash
cd infra/cdk
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap
cdk deploy --require-approval never
```

See `docs/README_AR.md` for an Arabic explanation and recommended AWS architecture.
