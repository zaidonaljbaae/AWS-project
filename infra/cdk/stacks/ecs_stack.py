from __future__ import annotations
from pathlib import Path

import os
from typing import List, Optional

from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
    aws_iam as iam,
)


class TemplateEcsStack(Stack):
    """ECS Fargate service hosting a simple public API."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stage = self.node.try_get_context("stage") or "dev"

        use_existing: bool = bool(self.node.try_get_context("useExistingVpc"))
        vpc: ec2.IVpc

        if use_existing:
            vpc_id: Optional[str] = self.node.try_get_context("vpcId")
            public_subnets: List[str] = self.node.try_get_context("publicSubnetIds") or []
            private_subnets: List[str] = self.node.try_get_context("privateSubnetIds") or []

            if not vpc_id or not public_subnets or not private_subnets:
                raise ValueError(
                    "Missing CDK context for existing VPC. Required: vpcId, publicSubnetIds, privateSubnetIds"
                )

            vpc = ec2.Vpc.from_vpc_attributes(
                self,
                "ImportedVPC",
                vpc_id=vpc_id,
                availability_zones=self.availability_zones,
                public_subnet_ids=public_subnets,
                private_subnet_ids=private_subnets,
            )
            private_selection = ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(self, f"Priv{i}", sid)
                    for i, sid in enumerate(private_subnets)
                ]
            )
        else:
            vpc = ec2.Vpc(
                self,
                "Vpc",
                max_azs=2,
                nat_gateways=1,
                subnet_configuration=[
                    ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC),
                    ec2.SubnetConfiguration(
                        name="private", subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                    ),
                ],
            )
            private_selection = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)

        ecs_sg = ec2.SecurityGroup(
            self,
            "EcsServiceSG",
            vpc=vpc,
            description="ECS service security group",
            allow_all_outbound=True,
        )

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc, cluster_name=f"template-cluster-{stage}")

        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/template/{stage}/ecs-service",
            retention=logs.RetentionDays.ONE_MONTH,
        )

        task_def = ecs.FargateTaskDefinition(self, "TaskDef", cpu=256, memory_limit_mib=512)

        # ✅ Fix Docker build context path using pathlib (absolute path)
        # This file: infra/cdk/stacks/ecs_stack.py
        # Repo root = parents[3]
        repo_root = Path(__file__).resolve().parents[3]
        ecs_service_dir = repo_root / "src" / "app" / "ecs_service"

        if not ecs_service_dir.is_dir():
            raise ValueError(f"Cannot find ecs_service directory: {ecs_service_dir}")

        # IMPORTANT:
        # The Dockerfile copies paths like `src/common` and `src/models`, so the
        # Docker build *context* must be the repository root (not ecs_service_dir).
        docker_context_dir = repo_root
        dockerfile_relpath = "src/app/ecs_service/Dockerfile"

        db_secret_arn = os.getenv("DB_SECRET_ARN") or str(self.node.try_get_context("dbSecretArn") or "")
        if db_secret_arn:
            task_def.task_role.add_to_policy(
                iam.PolicyStatement(
                    actions=["secretsmanager:GetSecretValue"],
                    resources=[db_secret_arn],
                )
            )

        container = task_def.add_container(
            "ApiApp",
            image=ecs.ContainerImage.from_asset(
                directory=str(docker_context_dir),
                file=dockerfile_relpath,
            ),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs", log_group=log_group),
            environment={
                "STAGE": stage,
                # If you store DB credentials in Secrets Manager, pass the ARN here.
                # The app will fall back to DB_* env vars if not set.
                "DB_SECRET_ARN": db_secret_arn,
            },
        )
        container.add_port_mappings(ecs.PortMapping(container_port=8080))

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_def,
            public_load_balancer=True,
            listener_port=80,
            desired_count=1,
            assign_public_ip=False,
            task_subnets=private_selection,
            security_groups=[ecs_sg],
            health_check_grace_period=Duration.seconds(30),
        )

        service.target_group.configure_health_check(path="/health")

        CfnOutput(self, "AlbDnsName", value=service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "EcsLogGroupName", value=log_group.log_group_name)
