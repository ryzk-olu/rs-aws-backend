# lambda/get_products_list.py
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
    print('getProductsList', event)
    try:
        products = dynamodb.Table(os.environ['PRODUCTS_TABLE']).scan()['Items']
        stocks = dynamodb.Table(os.environ['STOCKS_TABLE']).scan()['Items']

        stocks_map = {s['product_id']: s['count'] for s in stocks}

        result = [
            {**p, 'count': int(stocks_map.get(p['id'], 0))}
            for p in products
        ]

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(result, cls=DecimalEncoder)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({'message': 'Internal error'})
        }