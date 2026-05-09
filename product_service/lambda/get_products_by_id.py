# lambda/get_products_by_id.py
import json
import os
import boto3
from utils import DecimalEncoder

dynamodb = boto3.resource('dynamodb')

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def handler(event, context):
    print('getProductsById', event)
    product_id = (event.get("pathParameters") or {}).get("productId")

    try:
        product = dynamodb.Table(os.environ['PRODUCTS_TABLE']).get_item(
            Key={'id': product_id}
        ).get('Item')

        if not product:
            return {
                'statusCode': 404,
                'headers': HEADERS,
                'body': json.dumps({'message': 'Product not found'})
            }

        stock = dynamodb.Table(os.environ['STOCKS_TABLE']).get_item(
            Key={'product_id': product_id}
        ).get('Item', {})

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps({**product, 'count': int(stock.get('count', 0))}, cls=DecimalEncoder)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({'message': 'Internal error'})
        }