# Changes made (sanitization + template)

- Renamed service from **dlm-platform** to **aws-microservices-template**.
- Removed all hardcoded AWS resource IDs and credentials from configuration.
- Simplified `example_api` to a safe "print/echo" API that never requires DB or S3.
- Made DB helper (`src/common/conexao_banco.py`) non-failing: falls back to SQLite if `DB_URL` is not set.
- Updated CDK stack to `TemplateEcsStack`:
  - Creates a new VPC by default.
  - Can import an existing VPC via context.
- Removed generated artifacts (`cdk.out`) and Python bytecode.
- Reduced dependencies to keep deployments fast and reliable.
