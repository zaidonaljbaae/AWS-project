# CI/CD Pipeline Plan (AWS CodePipeline + CodeBuild)

Goal:
- Deploy **Serverless** stack (Lambda + HTTP API) using `sls deploy`
- Deploy **ECS** stack using **CDK** (`cdk deploy`)
- Optionally run **Flyway** migrations in a controlled environment

## Recommended approach
### 1) Source
- GitHub (recommended) or CodeCommit

### 2) CodeBuild projects
Create two CodeBuild projects (or one combined):
1) `dlm-serverless-deploy`
2) `dlm-cdk-deploy`

Enable:
- Privileged mode (Docker) for the CDK build (because it builds Docker image assets)

### 3) IAM roles
- CodeBuild role needs permissions for:
  - CloudFormation, IAM (limited), Lambda, ApiGatewayV2, Logs
  - ECS, EC2, ELBv2, ECR (for CDK assets), S3 (cdk assets bucket), STS
- CDK also needs bootstrap resources (assets bucket, roles).

### 4) Stages
- dev → qa → prod (separate pipelines or manual approval between stages)

## Buildspecs
- `pipeline/buildspec-serverless.yml`
- `pipeline/buildspec-cdk.yml`

You can attach them to two CodeBuild actions in CodePipeline.
