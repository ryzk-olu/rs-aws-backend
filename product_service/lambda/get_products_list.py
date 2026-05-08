import json
from products import PRODUCTS

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def handler(event, context):
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(PRODUCTS),
    }
