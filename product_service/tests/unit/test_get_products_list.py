import json
import pytest

from get_products_list import handler

class TestGetProductsListSuccess:

    def test_returns_status_code_200(self):
        response = handler({}, None)
        assert response["statusCode"] == 200

    def test_response_body_is_valid_non_empty_json(self):
        response = handler({}, None)
        body = json.loads(response["body"])
        assert body is not None
        assert len(body) > 0

    def test_each_product_has_id(self):
        response = handler({}, None)
        products = json.loads(response["body"])
        for product in products:
            assert "id" in product, f"Product without id: {product}"

    def test_each_product_has_title(self):
        response = handler({}, None)
        products = json.loads(response["body"])
        for product in products:
            assert "title" in product

    def test_each_product_has_price(self):
        response = handler({}, None)
        products = json.loads(response["body"])
        for product in products:
            assert "price" in product
            assert isinstance(product["price"], (int, float))

class TestGetProductsListCors:

    def test_has_cors_origin_header(self):
        response = handler({}, None)
        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_has_cors_methods_header(self):
        response = handler({}, None)
        assert "Access-Control-Allow-Methods" in response["headers"]