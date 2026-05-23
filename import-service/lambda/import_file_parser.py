import os
import csv
import io
import json
import boto3
from urllib.parse import unquote_plus

s3_client = boto3.client("s3")
sqs_client = boto3.client("sqs")

UPLOAD_FOLDER = os.environ["UPLOAD_FOLDER"]
PARSED_FOLDER = os.environ["PARSED_FOLDER"]
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]


def handler(event, context):
    print(f"Received event: {event}")

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        print(f"Processing file: s3://{bucket}/{key}")

        response = s3_client.get_object(Bucket=bucket, Key=key)
        body = response["Body"]

        text_stream = io.TextIOWrapper(body, encoding="utf-8")
        reader = csv.DictReader(text_stream)

        record_count = 0
        for row in reader:
            sqs_client.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(row),
            )
            record_count += 1

        print(f"Sent {record_count} records to SQS")

        new_key = key.replace(f"{UPLOAD_FOLDER}/", f"{PARSED_FOLDER}/", 1)
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={"Bucket": bucket, "Key": key},
            Key=new_key,
        )
        print(f"Copied to: s3://{bucket}/{new_key}")

        s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"Deleted: s3://{bucket}/{key}")

    return {"statusCode": 200}
