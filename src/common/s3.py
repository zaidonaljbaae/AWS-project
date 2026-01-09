#Libs
import boto3
import botocore
import os
import io

s3 = boto3.client('s3')
MAKE_THE_PRICE_BUCKET_NAME = os.getenv('MAKE_THE_PRICE_BUCKET_NAME')

def get_file_body_by_event(s3event):
    bucket = s3event['Records'][0]['s3']['bucket']['name']
    key = s3event['Records'][0]['s3']['object']['key']
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body']
    return body


def get_file_body_by_sped(s3event):
    bucket = s3event['Records'][0]['s3']['bucket']['name']
    key = s3event['Records'][0]['s3']['object']['key']
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body']
    size_in_bytes = obj['ContentLength']
    return body, size_in_bytes, key
    

def get_file_body_by_key(key, bucket_name):
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    body = obj['Body']
    size_in_bytes = obj['ContentLength']
    return body, size_in_bytes


def upload_file(key, bucket_name, body):
    s3.put_object(Bucket=bucket_name, Body=body, Key=key)


def delete_file(key, bucket_name):
    s3.delete_object(Bucket=bucket_name, Key=key)


def check_obj_exists(key, bucket_name):
    try:
        s3.get_object(Bucket=bucket_name, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
    return True

def move_obj(bucket, origin_key, destination_key):
    return s3.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': origin_key},
        Key=destination_key
        )