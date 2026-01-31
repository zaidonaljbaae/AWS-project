#!/usr/bin/env python3
import os
import aws_cdk as cdk

from stacks.alb_stack import TemplateAlbStack
from stacks.ecs_stack import TemplateEcsStack

app = cdk.App()

stage = app.node.try_get_context("stage") or os.getenv("STAGE", "dev")

region = (
    app.node.try_get_context("region")
    or os.getenv("CDK_DEFAULT_REGION")
    or os.getenv("AWS_REGION", "us-east-1")
)

account = (
    app.node.try_get_context("account")
    or os.getenv("CDK_DEFAULT_ACCOUNT")
    or os.getenv("AWS_ACCOUNT_ID")
)

if not account:
    raise ValueError("AWS account is not defined. Set AWS_ACCOUNT_ID or CDK_DEFAULT_ACCOUNT")


TemplateAlbStack(
    app,
    f"template-alb-{stage}",
    stage=stage,
    env=cdk.Environment(account=account, region=region),
)

TemplateEcsStack(
    app,
    f"template-ecs-{stage}",
    stage=stage,
    env=cdk.Environment(account=account, region=region),
)

app.synth()
