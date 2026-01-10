from __future__ import annotations

"""CDK stack: ECS Fargate + public Application Load Balancer.

This repository is a *generic template*.

Defaults (works without extra config):
- Creates a new VPC (2 AZs).
- Deploys a simple Flask container from src/app/ecs_service.
- Creates an Internet-facing ALB (HTTP/80) forwarding to the Fargate service.

Optional: import existing VPC
- If you already have a VPC, you can import it via CDK context:

  cdk deploy \
    -c stage=dev \
    -c useExistingVpc=true \
    -c vpcId=vpc-xxxx \
    -c publicSubnetIds='["subnet-a","subnet-b"]' \
    -c privateSubnetIds='["subnet-c","subnet-d"]'

"""

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
                    ec2.SubnetConfiguration(name="private", subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
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

        container = task_def.add_container(
            "ApiApp",
            image=ecs.ContainerImage.from_asset("../../src/app/ecs_service"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs", log_group=log_group),
            environment={"STAGE": stage},
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
