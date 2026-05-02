import json
import pytest
from get_products_by_id import handler
from products import PRODUCTS


class TestGetProductByIdSuccess:

    def test_returns_status_code_200(self):
        for product in PRODUCTS:
            event = {"pathParameters": {"productId": product["id"]}}
            response = handler(event, None)
            assert response["statusCode"] == 200

    def test_returns_correct_item(self):
        for product in PRODUCTS:
            event = {"pathParameters": {"productId": product["id"]}}
            response = handler(event, None)
            body = json.loads(response["body"])
            assert body == product

    def test_returns_single_object(self):
        for product in PRODUCTS:
            event = {"pathParameters": {"productId": product["id"]}}
            response = handler(event, None)
            body = json.loads(response["body"])
            assert isinstance(body, dict)

    def test_404_response_has_message(self):
        event = {"pathParameters": {"productId": "nonexistent"}}
        response = handler(event, None)
        body = json.loads(response["body"])
        assert "message" in body


class TestGetProductByIdNotFound:

    def test_returns_404_for_nonexistent_id(self):
        event = {"pathParameters": {"productId": "nonexistent"}}
        response = handler(event, None)
        assert response["statusCode"] == 404


class TestGetProductByIdCors:

    def test_has_cors_origin_header(self):
        event = {"pathParameters": {"productId": PRODUCTS[0]["id"]}}
        response = handler(event, None)
        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_has_cors_methods_header(self):
        event = {"pathParameters": {"productId": PRODUCTS[0]["id"]}}
        response = handler(event, None)
        assert "Access-Control-Allow-Methods" in response["headers"]