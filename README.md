# DLM Platform (Serverless + ECS + Flyway)

This repository is a **base project** that deploys:
- **Lambda + API Gateway HTTP API** (Flask via `serverless-wsgi`)
- **ECS Fargate service** for **long-running jobs** (no Lambda timeout)
- **RDS PostgreSQL** connection via **AWS Secrets Manager**
- Optional **S3** access for testing (put/list objects)

> You must provide your own VPC/Subnets/RDS/Secret and pass them as environment variables (Serverless) and CDK context (ECS).

## Required AWS environment variables (Serverless deploy)

Set these in your shell / CodeBuild environment:

- `STAGE` = `dev` or `prod`
- `AWS_REGION` = `us-east-1`
- `AWS_ACCOUNT_ID` = your account id
- `VPC_ID` = your VPC id
- `PRIVATE_SUBNET_IDS` = YAML list for serverless (example: `["subnet-aaa","subnet-bbb"]`)
- `RDS_SG_ID` = Security Group id of the RDS instance
- `DB_SECRET_ARN` = Secrets Manager ARN containing DB credentials
- `S3_BUCKET_NAME` = your bucket name
- (optional auth) `COGNITO_ISSUER_URL`, `COGNITO_AUDIENCE`

## ECS via CDK

Edit `infra/cdk/cdk.json` and replace placeholders:
- `vpcId`
- `publicSubnetIds`
- `privateSubnetIds`
- `rdsSecurityGroupId`
- `dbSecretArn`
- `s3BucketName`

Then:

```bash
cd infra/cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy "dlm-ecs-${STAGE}" --require-approval never
```

## Test endpoints

### Lambda HTTP API
- `/example_api/public/health`
- `/example_api/public/items` (GET/POST)
- `/example_api/public/s3/put` (POST)
- `/example_api/public/s3/list` (GET)
- `/example_api/private/me` (JWT auth via Cognito authorizer)

### Print lambda
- `/print` (GET)

### ECS service (ALB)
- `/health`

## Flyway
See `flyway/` folder in the full runbook. Recommended approach:
- Run Flyway from a **VPC-enabled CodeBuild** (in private subnets with SG that can reach RDS),
  or run Flyway as a **one-off ECS task** in the same cluster.
