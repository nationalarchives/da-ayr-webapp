import os

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

DRI_JSON_BUCKET = os.environ["DRI_JSON_BUCKET"]
DRI_DATA_BUCKET = os.environ["DRI_DATA_BUCKET"]


def lambda_handler(event, context):
    results = {
        "json_bucket": test_get_object(
            DRI_JSON_BUCKET,
            event["json_object_key"],
        ),
        "data_bucket": test_get_object(
            DRI_DATA_BUCKET,
            event["data_object_key"],
        ),
    }

    if not all(results.values()):
        raise RuntimeError("GetObject test failed for one or more buckets")

    return results


def test_get_object(bucket, object_key):
    try:
        response = s3.get_object(
            Bucket=bucket,
            Key=object_key,
            Range="bytes=0-0",
        )

        response["Body"].close()
        print(f"SUCCESS: Can get s3://{bucket}/{object_key}")
        return True

    except ClientError as error:
        code = error.response["Error"]["Code"]
        message = error.response["Error"]["Message"]

        print(
            f"FAILED: Cannot get s3://{bucket}/{object_key}: {code} - {message}"
        )
        return False
