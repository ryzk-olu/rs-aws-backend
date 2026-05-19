# lambda/create_product.py
import json
import os
import uuid
import boto3

dynamodb = boto3.client('dynamodb')

def handler(event, context):
    print('createProduct', event)
    try:
        body = json.loads(event['body'])
        title = body.get('title')
        description = body.get('description', '')
        price = body.get('price')
        count = body.get('count')

        if not title or price is None or count is None:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid product data'})}

        product_id = str(uuid.uuid4())

        dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': os.environ['PRODUCTS_TABLE'],
                        'Item': {
                            'id':          {'S': product_id},
                            'title':       {'S': title},
                            'description': {'S': description},
                            'price':       {'N': str(price)},
                        }
                    }
                },
                {
                    'Put': {
                        'TableName': os.environ['STOCKS_TABLE'],
                        'Item': {
                            'product_id': {'S': product_id},
                            'count':      {'N': str(count)},
                        }
                    }
                },
            ]
        )

        return {'statusCode': 201, 'body': json.dumps({'id': product_id})}
    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': json.dumps({'message': 'Internal error'})}