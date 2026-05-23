import json
import os
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]
UPLOAD_FOLDER = os.environ["UPLOAD_FOLDER"]

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    file_name = query_params.get("name")

    if not file_name:
        return {
            "statusCode": 400,
            "headers": HEADERS,
            "body": json.dumps({"message": "Query parameter 'name' is required"}),
        }

    if not file_name.endswith(".csv"):
        return {
            "statusCode": 400,
            "headers": HEADERS,
            "body": json.dumps({"message": "Only .csv files are supported"}),
        }

    key = f"{UPLOAD_FOLDER}/{file_name}"

    try:
        signed_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": key,
                "ContentType": "text/csv",
            },
            ExpiresIn=3600,
        )
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return {
            "statusCode": 500,
            "headers": HEADERS,
            "body": json.dumps({"message": "Failed to generate signed URL"}),
        }

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": signed_url,  
    }
