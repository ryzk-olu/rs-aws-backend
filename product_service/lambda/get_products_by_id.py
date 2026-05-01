import json
from products import PRODUCTS

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def handler(event, context):
    product_id = (event.get("pathParameters") or {}).get("productId")
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if product is None:
        return {
            "statusCode": 404,
            "headers": HEADERS,
            "body": json.dumps({"message": "Product not found"}),
        }

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(product),
    }
