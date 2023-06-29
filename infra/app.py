#!/usr/bin/env python3
import os
from aws_cdk import App 
from infra.fargate_service_stack import FargateServiceStack, FargateServiceOptions, ImageOptions
import re


app = App()

# Get context variables
environment = app.node.try_get_context("environment")
app_name =  app.node.try_get_context("app_name")
image = app.node.try_get_context("image")

#Check that image conforms to expected format
image_format = re.compile(r'(.*):(.*)')
if image_format.match(image):
#Derive repository and tag from image
  groups = image_format.match(image).groups()
  repository = groups[0].split('/')[-1]
  tag = groups[1] 
else:
  raise Exception(f"{image} does not conform to required format repository:tag")

# Defined App configs
app_options = FargateServiceOptions(
  app_name=app_name, 
  image=ImageOptions(repository=repository, tag=tag), 
  cpu=1024,
  memoryLimitMiB=4096,
)

# Application Stack
FargateServiceStack(app, f"{environment}-{app_name}-FargateTaskStack",
  options=app_options, 
  environment=environment, 
  env={
    'account': os.environ['CDK_DEFAULT_ACCOUNT'], 
    'region': os.environ['CDK_DEFAULT_REGION']
  }
)

app.synth()

