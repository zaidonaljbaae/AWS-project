#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.ecs_stack import DlmEcsStack

app = cdk.App()

stage = app.node.try_get_context("stage") or os.getenv("STAGE", "dev")
region = app.node.try_get_context("region") or os.getenv("AWS_REGION", "us-east-1")

DlmEcsStack(
    app,
    f"dlm-ecs-{stage}",
    env=cdk.Environment(region=region),
)

app.synth()
