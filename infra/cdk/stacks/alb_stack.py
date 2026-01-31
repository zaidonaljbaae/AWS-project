from __future__ import annotations

import os

from aws_cdk import (
    Stack,
    CfnOutput,
    Fn,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct


class TemplateAlbStack(Stack):
    """
    Stack مسؤول فقط عن ALB + Listener بحيث يبقى ثابت عبر أي Deploys.
    - يمكن تثبيت SG للـ ALB عبر متغير البيئة ALB_SG_ID
    - يمكن تحديد Subnets للـ ALB عبر ALB_SUBNET_IDS (اختياري)
    """

    def __init__(self, scope: Construct, construct_id: str, *, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = os.getenv("VPC_ID")
        if not vpc_id:
            raise ValueError("VPC_ID is required. Set VPC_ID to your existing VPC.")

        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

        alb_sg_id = os.getenv("ALB_SG_ID")
        if not alb_sg_id:
            raise ValueError("ALB_SG_ID environment variable is required (existing SG for ALB).")

        alb_sg = ec2.SecurityGroup.from_security_group_id(
            self, "ImportedAlbSg", alb_sg_id, mutable=False
        )

        # اختيار subnets للـ ALB
        alb_subnet_ids_env = os.getenv("ALB_SUBNET_IDS", "")
        alb_subnet_ids = [s.strip() for s in alb_subnet_ids_env.split(",") if s.strip()]

        if alb_subnet_ids:
            alb_subnets = ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(self, f"AlbSubnet{i}", sid)
                    for i, sid in enumerate(alb_subnet_ids)
                ]
            )
        else:
            # استخدم public subnets المعرفة في الـ VPC
            alb_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)

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
            open=True,  # يسمح 80 من الإنترنت (معتمد على SG)
            default_action=elbv2.ListenerAction.fixed_response(
                status_code=404,
                message_body="No default target configured.",
                content_type="text/plain",
            ),
        )

        # Exports (CloudFormation cross-stack)
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
