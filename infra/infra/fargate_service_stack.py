import secrets
from aws_cdk import aws_secretsmanager as ssm
from constructs import Construct
from aws_cdk import Stack, Duration, SecretValue
from aws_cdk.aws_ec2 import Vpc, SecurityGroup, Peer, Port
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationTargetGroup,TargetType,ApplicationProtocol,ApplicationProtocolVersion,HealthCheck,ListenerAction,TargetGroupLoadBalancingAlgorithmType
from aws_cdk.aws_ecs import Secret, FargateTaskDefinition, ContainerImage,LogDrivers, Cluster, PortMapping, Protocol
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedFargateService
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from aws_cdk.aws_logs import LogGroup
from aws_cdk.aws_ecr import Repository

from dataclasses import dataclass
from typing import Optional

@dataclass
class ImageOptions:
    repository: str
    tag: str


@dataclass
class FargateServiceOptions:
    app_name: str
    image: ImageOptions
    cpu: int
    memoryLimitMiB: int

class FargateServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, options: FargateServiceOptions, environment: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import PBR VPC
        vpc = Vpc.from_lookup(self, f"ImportVPC", vpc_name=f'{environment}-pbr-vpc')
        
        security_group = SecurityGroup(self, f'{environment}-{options.app_name}-sg',
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Security group for {environment}-{options.app_name}."

        
        )
        security_group.add_ingress_rule(
            Peer.any_ipv4(), 
            Port.tcp(3838),
            'allow HTTP traffic from anywhere on port 3838',
        )
  
        cluster = Cluster.from_cluster_attributes(self, "PBRCluster", cluster_name=f'{environment}-pbr-cluster', security_groups=[security_group], vpc=vpc)

        # Defined execution Role
        execution_role = Role(self, "ExecutionRole",
            assumed_by=ServicePrincipal("ecs-tasks.amazonaws.com"),
            description=f"{environment}-{options.app_name} service execution role",
            managed_policies=[
                ManagedPolicy.from_managed_policy_arn(self, "AmazonECSTaskExecutionRolePolicy", "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"),
                ManagedPolicy.from_managed_policy_arn(self, "AWSStepFunctionsFullAccessPolicy", "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess")
                                        ]
        )

        # Defined task role  
        task_role = Role(self, "TaskRole",
            assumed_by=ServicePrincipal("ecs-tasks.amazonaws.com"),
            description=f"{environment}-{options.app_name} service task role",
            managed_policies=[
                ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AmazonAthenaFullAccess",
                    "arn:aws:iam::aws:policy/AmazonAthenaFullAccess",
                ),
                ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AmazonS3FullAccess",
                    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                ),
            ],
        )

        # Defined ECS Task definitionn
        task_definition = FargateTaskDefinition(self, f"{environment}-{options.app_name}-task-def",
            family= options.app_name,
            execution_role=execution_role,
            task_role = task_role,
            memory_limit_mib=options.memoryLimitMiB,
            cpu=options.cpu

        )
        port_mapping = PortMapping(container_port=3838,
                                   protocol=Protocol.TCP)
        
        # add container to task definition
        specific_container = task_definition.add_container(options.app_name,
            image=ContainerImage.from_ecr_repository(Repository.from_repository_name(self, 'ECRImage', options.image.repository), tag=options.image.tag),
            logging=LogDrivers.aws_logs(stream_prefix=options.app_name,log_group=LogGroup(self, 'LogGroup')),
            environment= {
                "LOGGING_LEVEL": "INFO",
                "APP_NAME": options.app_name,
                "ENVIRONMENT": environment,
            },
            essential= True,
            port_mappings= [port_mapping]  )

        load_balanced_fargate_service = ApplicationLoadBalancedFargateService(self, f"{environment}-{options.app_name}-lbfgs",
            cluster=cluster, 
            assign_public_ip=True,
            task_definition=task_definition,
            public_load_balancer=True,
            load_balancer_name=f"{environment}-{options.app_name}-lb",
            security_groups=[security_group],
            health_check_grace_period=Duration.seconds(240),
            listener_port=80,
            service_name= F"{environment}-{options.app_name}-Service",
        )