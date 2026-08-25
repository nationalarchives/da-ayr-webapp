import os

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

DRI_JSON_BUCKET = os.environ["DRI_JSON_BUCKET"]


def lambda_handler(event, context):
    object_key = event["object_key"]

    try:
        response = s3.get_object(
            Bucket=DRI_JSON_BUCKET,
            Key=object_key,
            Range="bytes=0-0",
        )

        response["Body"].close()

        print(f"SUCCESS: Role can get s3://{DRI_JSON_BUCKET}/{object_key}")

        return {"success": True, "object_key": object_key}

    except ClientError as error:
        code = error.response["Error"]["Code"]
        message = error.response["Error"]["Message"]

        print(f"FAILED: {code} - {message}")
        raise
