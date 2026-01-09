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
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
)


class DlmEcsStack(Stack):
    """ECS Fargate service for long-running workloads (no Lambda timeout)."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stage = self.node.try_get_context("stage") or "dev"
        vpc_id = self.node.try_get_context("vpcId")
        public_subnets: List[str] = self.node.try_get_context("publicSubnetIds") or []
        private_subnets: List[str] = self.node.try_get_context("privateSubnetIds") or []
        rds_sg_id = self.node.try_get_context("rdsSecurityGroupId")
        db_secret_arn = self.node.try_get_context("dbSecretArn")
        s3_bucket_name = self.node.try_get_context("s3BucketName")

        if not all([vpc_id, public_subnets, private_subnets, rds_sg_id, db_secret_arn, s3_bucket_name]):
            raise ValueError(
                "Missing CDK context. Required: vpcId, publicSubnetIds, privateSubnetIds, "
                "rdsSecurityGroupId, dbSecretArn, s3BucketName"
            )

        vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "ImportedVPC",
            vpc_id=vpc_id,
            availability_zones=self.availability_zones,
            public_subnet_ids=public_subnets,
            private_subnet_ids=private_subnets,
        )

        # SG for ECS tasks (tight egress)
        ecs_sg = ec2.SecurityGroup(
            self,
            "EcsServiceSG",
            vpc=vpc,
            description="ECS service SG",
            allow_all_outbound=False,
        )
        ecs_sg.add_egress_rule(
            peer=ec2.Peer.security_group_id(rds_sg_id),
            connection=ec2.Port.tcp(5432),
            description="ECS -> RDS",
        )
        ecs_sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS to AWS APIs via NAT",
        )

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc, cluster_name=f"dlm-cluster-{stage}")

        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/dlm/{stage}/ecs",
            retention=logs.RetentionDays.ONE_MONTH,
        )

        db_secret = secretsmanager.Secret.from_secret_complete_arn(self, "DbSecret", db_secret_arn)

        task_def = ecs.FargateTaskDefinition(self, "TaskDef", cpu=512, memory_limit_mib=1024)

        container = task_def.add_container(
            "FlaskApp",
            image=ecs.ContainerImage.from_asset("../../src/app/ecs_service"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs", log_group=log_group),
            environment={
                "STAGE": stage,
                "DB_SECRET_ARN": db_secret_arn,
                "DB_NAME": "postgres",
                "S3_BUCKET_NAME": s3_bucket_name,
            },
        )
        container.add_port_mappings(ecs.PortMapping(container_port=8080))

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_def,
            public_load_balancer=True,
            desired_count=1,
            listener_port=80,
            assign_public_ip=False,
            task_subnets=ec2.SubnetSelection(
                subnets=[ec2.Subnet.from_subnet_id(self, f"Priv{i}", sid) for i, sid in enumerate(private_subnets)]
            ),
            security_groups=[ecs_sg],
            health_check_grace_period=Duration.seconds(30),
        )

        service.target_group.configure_health_check(path="/health")

        # IAM: allow ECS task to read DB secret + access S3
        task_def.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
                resources=[db_secret_arn],
            )
        )
        task_def.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
                resources=[f"arn:aws:s3:::{s3_bucket_name}", f"arn:aws:s3:::{s3_bucket_name}/*"],
            )
        )

        CfnOutput(self, "AlbDnsName", value=service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "EcsLogGroupName", value=log_group.log_group_name)
