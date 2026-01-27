from __future__ import annotations

from pathlib import Path

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
)
from constructs import Construct


class TemplateEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ====== Networking (use default VPC, or replace with your VPC lookup) ======
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

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
        repo_root = Path(__file__).resolve().parents[3]  # .../infra/cdk/stacks -> repo root
        service_dir = repo_root / "src" / "app" / "ecs_service"

        if not service_dir.exists():
            raise RuntimeError(
                f"ECS service directory not found: {service_dir}\n"
                "Create it or update SERVICE_DIR path in infra/cdk/stacks/ecs_stack.py"
            )

        container = task_def.add_container(
            "AppContainer",
            image=ecs.ContainerImage.from_asset(
                directory=str(service_dir),
                # Extra safety even with .dockerignore:
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
            environment={
            },
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # ====== Fargate Service + ALB (simple pattern) ======
        ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_def,
            desired_count=1,
            public_load_balancer=True,
            health_check_grace_period=Duration.seconds(60),
        )
