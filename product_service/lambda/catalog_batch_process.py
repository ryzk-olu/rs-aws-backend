import json
import os
import uuid
import boto3

dynamodb = boto3.resource("dynamodb")
sns_client = boto3.client("sns")

products_table = dynamodb.Table(os.environ["PRODUCTS_TABLE"])
stocks_table = dynamodb.Table(os.environ["STOCKS_TABLE"])
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def handler(event, context):
    print(f"Received event: {event}")
    created_count = 0

    for record in event.get("Records", []):
        body = json.loads(record["body"])
        print(f"Processing product: {body}")

        product_id = str(uuid.uuid4())
        price = int(body.get("price", 0))

        products_table.put_item(Item={
            "id": product_id,
            "title": body.get("title", ""),
            "description": body.get("description", ""),
            "price": price,
        })

        stocks_table.put_item(Item={
            "product_id": product_id,
            "count": int(body.get("count", 0)),
        })
        print(f"Created product: {product_id}")

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Product created",
            Message=json.dumps({
                "message": "Product was created",
                "product": {
                    "id": product_id,
                    "title": body.get("title", ""),
                    "price": price,
                },
            }),
            MessageAttributes={
                "price": {
                    "DataType": "Number",
                    "StringValue": str(price),
                }
            },
        )
        print(f"SNS sent for {product_id}, price={price}")
        created_count += 1

    print(f"Total products created: {created_count}")
    return {"statusCode": 200}
