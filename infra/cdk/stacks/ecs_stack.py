from __future__ import annotations

import os
from pathlib import Path

from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
    Fn,
    aws_logs as logs,
)
from constructs import Construct


class TemplateEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ====== Networking ======
        # IMPORTANT: An ALB can only attach Security Groups from the SAME VPC.
        # If you previously deployed this stack using a different VPC and later changed the lookup,
        # CloudFormation can fail with:
        #   "One or more security groups are invalid"
        #
        # Pro rule: make the VPC choice explicit and stable across deployments.
        #
        # Options:
        # 1) Provide an existing VPC id via env var VPC_ID (recommended in shared AWS accounts)
        # 2) If VPC_ID is not set, CDK will CREATE a dedicated VPC (recommended for demos/sandboxes)
        vpc_id = os.getenv("VPC_ID")
        if not vpc_id:
            raise ValueError("VPC_ID is required. Set VPC_ID to your existing VPC.")

        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

        # ====== Security Groups (fixed, provided via env vars) ======
        ecs_task_sg_id = os.getenv("ECS_TASK_SG_ID")
        if not ecs_task_sg_id:
            raise ValueError("ECS_TASK_SG_ID environment variable is required (existing SG for ECS tasks).")

        ecs_task_sg = ec2.SecurityGroup.from_security_group_id(
            self, "ImportedEcsTaskSg", ecs_task_sg_id, mutable=True
        )

        alb_sg_id = os.getenv("ALB_SG_ID")
        if not alb_sg_id:
            raise ValueError("ALB_SG_ID environment variable is required (existing SG for ALB).")

        alb_sg = ec2.SecurityGroup.from_security_group_id(
            self, "ImportedAlbSgForIngress", alb_sg_id, mutable=False
        )

        # Allow ALB to reach ECS tasks on app port
        ecs_task_sg.add_ingress_rule(
            peer=alb_sg,
            connection=ec2.Port.tcp(8080),
            description="Allow ALB to reach ECS tasks on 8080",
        )

        subnet_ids_env = os.getenv("SUBNET_IDS", "")
        subnet_ids = [s.strip() for s in subnet_ids_env.split(",") if s.strip()]

        subnet_selection = None
        if subnet_ids:
            subnet_selection = ec2.SubnetSelection(
                subnets=[ec2.Subnet.from_subnet_id(self, f"Subnet{i}", sid) for i, sid in enumerate(subnet_ids)]
            )

        # ====== ECS Cluster ======
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        # ====== Task Definition ======
        task_def = ecs.FargateTaskDefinition(
            self,
            "TaskDef",
            cpu=512,
            memory_limit_mib=1024,
        )

        # ====== Docker context directory (IMPORTANT!) ======
        # Put ONLY the ECS service folder here, NOT the project root.
        # Expected: src/app/ecs_service/Dockerfile
        repo_root = Path(__file__).resolve().parents[3]
        dockerfile_path = repo_root / "src" / "app" / "ecs_service" / "Dockerfile"

        container = task_def.add_container(
            "AppContainer",
            image=ecs.ContainerImage.from_asset(
                directory=str(repo_root),  # ✅ build context = root
                file=str(dockerfile_path.relative_to(repo_root)),  # ✅ Dockerfile path relative
                exclude=[
                    "**/cdk.out/**",
                    "**/.git/**",
                    "**/node_modules/**",
                    "**/__pycache__/**",
                    "**/vendor/**",
                    "**/.venv/**",
                    "**/venv/**",
                    "**/dist/**",
                    "**/build/**",
                ],
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="ecs",
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
            environment={},
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=8080, protocol=ecs.Protocol.TCP)
        )

        
        # ====== ECS Service (no ALB creation here) ======
        service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_def,
            desired_count=1,
            assign_public_ip=False,
            vpc_subnets=subnet_selection,
            security_groups=[ecs_task_sg],
            health_check_grace_period=Duration.seconds(60),
        )

        # ====== Attach Service to EXISTING ALB Listener (from TemplateAlbStack exports) ======
        listener_arn = Fn.import_value(f"template-{stage}-alb-listener-arn")
        alb_dns = Fn.import_value(f"template-{stage}-alb-dns")

        listener = elbv2.ApplicationListener.from_application_listener_attributes(
            self,
            "ImportedAlbListener",
            listener_arn=listener_arn,
            security_group=alb_sg,
        )

        # Create a Target Group behind the existing listener and register ECS tasks (IP targets)
        listener.add_targets(
            "EcsTargets",
            port=8080,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            health_check=elbv2.HealthCheck(
                path="/",
                healthy_http_codes="200-399",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=2,
            ),
        )

        # Useful output: public URL
        CfnOutput(self, "ServiceUrl", value=f"http://{alb_dns}")
