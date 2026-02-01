from __future__ import annotations

import os
import boto3


def get_bucket_name() -> str:
    name = os.getenv("S3_BUCKET_NAME")
    if not name:
        raise RuntimeError("S3_BUCKET_NAME is not set")
    return name


def s3_client():
    return boto3.client("s3")


def put_text_object(key: str, body: str) -> None:
    bucket = get_bucket_name()
    s3_client().put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))


def list_objects(prefix: str = "", limit: int = 20):
    bucket = get_bucket_name()
    resp = s3_client().list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=limit)
    return [o["Key"] for o in resp.get("Contents", [])]
