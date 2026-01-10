from __future__ import annotations

from typing import List

from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
)


class DlmEcsStack(Stack):
    """ECS Fargate service hosting a simple public API (no DB, no Secrets)."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stage = self.node.try_get_context("stage") or "dev"
        vpc_id = self.node.try_get_context("vpcId")
        public_subnets: List[str] = self.node.try_get_context("publicSubnetIds") or []
        private_subnets: List[str] = self.node.try_get_context("privateSubnetIds") or []

        if not all([vpc_id, public_subnets, private_subnets]):
            raise ValueError(
                "Missing CDK context. Required: vpcId, publicSubnetIds, privateSubnetIds"
            )

        vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "ImportedVPC",
            vpc_id=vpc_id,
            availability_zones=self.availability_zones,
            public_subnet_ids=public_subnets,
            private_subnet_ids=private_subnets,
        )

        # SG for ECS tasks (allow outbound HTTPS by default)
        ecs_sg = ec2.SecurityGroup(
            self,
            "EcsServiceSG",
            vpc=vpc,
            description="ECS service SG",
            allow_all_outbound=True,
        )

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc, cluster_name=f"dlm-api-cluster-{stage}")

        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/dlm/{stage}/ecs-api",
            retention=logs.RetentionDays.ONE_MONTH,
        )

        task_def = ecs.FargateTaskDefinition(self, "TaskDef", cpu=256, memory_limit_mib=512)

        container = task_def.add_container(
            "ApiApp",
            image=ecs.ContainerImage.from_asset("../../src/app/ecs_service"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs", log_group=log_group),
            environment={
                "STAGE": stage,
            },
        )
        container.add_port_mappings(ecs.PortMapping(container_port=8080))

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_def,
            public_load_balancer=True,     # internet-facing ALB
            listener_port=80,
            desired_count=1,
            assign_public_ip=False,
            task_subnets=ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(self, f"Priv{i}", sid)
                    for i, sid in enumerate(private_subnets)
                ]
            ),
            security_groups=[ecs_sg],
            health_check_grace_period=Duration.seconds(30),
        )

        service.target_group.configure_health_check(path="/health")

        CfnOutput(self, "AlbDnsName", value=service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "EcsLogGroupName", value=log_group.log_group_name)
