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
    created_products = []

    for record in event.get("Records", []):
        body = json.loads(record["body"])
        print(f"Processing product: {body}")

        product_id = str(uuid.uuid4())

        products_table.put_item(Item={
            "id": product_id,
            "title": body.get("title", ""),
            "description": body.get("description", ""),
            "price": int(body.get("price", 0)),
        })

        stocks_table.put_item(Item={
            "product_id": product_id,
            "count": int(body.get("count", 0)),
        })

        created_products.append({
            "id": product_id,
            "title": body.get("title", ""),
        })
        print(f"Created product: {product_id}")

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="Products created",
        Message=json.dumps({
            "message": f"{len(created_products)} products were created",
            "products": created_products,
        }),
    )
    print(f"SNS notification sent for {len(created_products)} products")

    return {"statusCode": 200}
