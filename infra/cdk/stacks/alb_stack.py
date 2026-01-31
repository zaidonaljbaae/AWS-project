from __future__ import annotations

import json
import os

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct


def _parse_subnet_ids_env(var_name: str) -> list[str]:
    """
    Parse subnet IDs from an environment variable.

    Supported formats:
      1) JSON list (recommended): '["subnet-aaa","subnet-bbb"]'
      2) Comma-separated: 'subnet-aaa,subnet-bbb'

    Returns:
      List of subnet IDs (strings). Empty list if env var is missing/blank.
    """
    raw = os.getenv(var_name, "").strip()
    if not raw:
        return []

    # Try JSON list first (recommended)
    if raw.startswith("["):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"{var_name} looks like JSON but is invalid. "
                f'Use format: ["subnet-aaa","subnet-bbb"]. Got: {raw}'
            ) from e

        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError(
                f"{var_name} must be a JSON list of strings. "
                f'Example: ["subnet-aaa","subnet-bbb"]. Got: {value}'
            )

        return [s.strip() for s in value if s.strip()]

    # Fallback: comma-separated
    return [s.strip() for s in raw.split(",") if s.strip()]


class TemplateAlbStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---- VPC ----
        vpc_id = os.getenv("VPC_ID")
        if not vpc_id:
            raise ValueError("VPC_ID is required. Set VPC_ID to your existing VPC.")
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

        # ---- ALB Security Group (existing, fixed) ----
        alb_sg_id = os.getenv("ALB_SG_ID")
        if not alb_sg_id:
            raise ValueError("ALB_SG_ID environment variable is required (existing SG for ALB).")
        alb_sg = ec2.SecurityGroup.from_security_group_id(
            self, "ImportedAlbSg", alb_sg_id, mutable=False
        )

        # ---- Subnets selection (from env) ----
        # Recommended: ALB_SUBNET_IDS='["subnet-...","subnet-..."]'
        # Also supports: ALB_SUBNET_IDS='subnet-...,subnet-...'
        alb_subnet_ids = _parse_subnet_ids_env("ALB_SUBNET_IDS")

        if alb_subnet_ids:
            alb_subnets = ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(self, f"AlbSubnet{i}", sid)
                    for i, sid in enumerate(alb_subnet_ids)
                ]
            )
        else:
            # Default behavior: pick PUBLIC subnets from the VPC
            alb_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)

        # ---- ALB ----
        alb = elbv2.ApplicationLoadBalancer(
            self,
            "Alb",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
            vpc_subnets=alb_subnets,
        )

        listener = alb.add_listener(
            "HttpListener",
            port=80,
            open=True,
            default_action=elbv2.ListenerAction.fixed_response(
                status_code=404,
                message_body="No default target configured.",
                content_type="text/plain",
            ),
        )

        # ---- Exports (CloudFormation cross-stack) ----
        export_prefix = f"template-{stage}"
        CfnOutput(
            self,
            "AlbArn",
            value=alb.load_balancer_arn,
            export_name=f"{export_prefix}-alb-arn",
        )
        CfnOutput(
            self,
            "AlbDnsName",
            value=alb.load_balancer_dns_name,
            export_name=f"{export_prefix}-alb-dns",
        )
        CfnOutput(
            self,
            "ListenerArn",
            value=listener.listener_arn,
            export_name=f"{export_prefix}-alb-listener-arn",
        )
