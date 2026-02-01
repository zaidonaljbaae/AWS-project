#Libs
import boto3
import json

client = boto3.client('lambda', region_name='us-east-1')

def invoke_lambda_async(function_name, input_lambda):
    return client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(input_lambda)
    )