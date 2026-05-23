import json
import os
from unittest.mock import patch, MagicMock

os.environ["PRODUCTS_TABLE"] = "test-products"
os.environ["STOCKS_TABLE"] = "test-stocks"
os.environ["SNS_TOPIC_ARN"] = "arn:aws:sns:us-east-1:123456789012:test-topic"


def make_sqs_event(products):
    return {
        "Records": [
            {"body": json.dumps(product)} for product in products
        ]
    }


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_returns_200(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = make_sqs_event([
        {"title": "Mouse", "description": "Wireless", "price": "15", "count": "10"},
    ])
    response = handler(event, None)

    assert response["statusCode"] == 200


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_creates_product_in_products_table(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = make_sqs_event([
        {"title": "Mouse", "description": "Wireless", "price": "15", "count": "10"},
    ])
    handler(event, None)

    mock_products.put_item.assert_called_once()

    item = mock_products.put_item.call_args.kwargs["Item"]
    assert item["title"] == "Mouse"
    assert item["description"] == "Wireless"
    assert item["price"] == 15
    assert "id" in item


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_creates_stock_in_stocks_table(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = make_sqs_event([
        {"title": "Mouse", "description": "Wireless", "price": "15", "count": "10"},
    ])
    handler(event, None)

    mock_stocks.put_item.assert_called_once()

    item = mock_stocks.put_item.call_args.kwargs["Item"]
    assert item["count"] == 10
    assert "product_id" in item


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_processes_all_records_in_batch(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = make_sqs_event([
        {"title": "Mouse", "description": "Wireless", "price": "15", "count": "10"},
        {"title": "Keyboard", "description": "Mechanical", "price": "80", "count": "5"},
        {"title": "Monitor", "description": "4K", "price": "300", "count": "2"},
    ])
    handler(event, None)

    assert mock_products.put_item.call_count == 3
    assert mock_stocks.put_item.call_count == 3


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_publishes_to_sns(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = make_sqs_event([
        {"title": "Mouse", "description": "Wireless", "price": "15", "count": "10"},
    ])
    handler(event, None)

    assert mock_sns.publish.called


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_sns_publish_uses_correct_topic(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = make_sqs_event([
        {"title": "Mouse", "description": "Wireless", "price": "15", "count": "10"},
    ])
    handler(event, None)

    call_kwargs = mock_sns.publish.call_args.kwargs
    assert call_kwargs["TopicArn"] == "arn:aws:sns:us-east-1:123456789012:test-topic"


@patch("catalog_batch_process.sns_client")
@patch("catalog_batch_process.stocks_table")
@patch("catalog_batch_process.products_table")
def test_handles_empty_records(mock_products, mock_stocks, mock_sns):
    from catalog_batch_process import handler

    event = {"Records": []}
    response = handler(event, None)

    assert response["statusCode"] == 200
    mock_products.put_item.assert_not_called()
    mock_stocks.put_item.assert_not_called()
