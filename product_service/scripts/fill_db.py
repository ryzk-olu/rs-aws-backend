# scripts/populate_db.py
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table('products')
stocks_table = dynamodb.Table('stocks')

products = [
    {'id': str(uuid.uuid4()), 'title': 'Pack of 10 stickers', 'description': 'Unique stickers with merch from RS School', 'price': 5},
    {'id': str(uuid.uuid4()), 'title': 'Yellow mug', 'description': 'A great mug with a sloth on it as a gift', 'price': 10},
    {'id': str(uuid.uuid4()), 'title': 'T-shirt with symbols', 'description': 'A recognizable T-shirt exclusively from RS School', 'price': 20},
]

for product in products:
    products_table.put_item(Item=product)
    stocks_table.put_item(Item={
        'product_id': product['id'],
        'count': 5
    })
    print(f"Added: {product['title']}")

print('Done')