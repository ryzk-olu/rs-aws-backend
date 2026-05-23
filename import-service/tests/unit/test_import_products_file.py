import json
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

os.environ["BUCKET_NAME"] = "test-bucket"
os.environ["UPLOAD_FOLDER"] = "uploaded"

from import_products_file import handler


def test_returns_400_without_name():
    event = {"queryStringParameters": None}
    response = handler(event, None)
    assert response["statusCode"] == 400


def test_returns_400_for_non_csv():
    event = {"queryStringParameters": {"name": "file.txt"}}
    response = handler(event, None)
    assert response["statusCode"] == 400


@patch("import_products_file.s3_client")
def test_returns_signed_url_for_csv(mock_s3):
    mock_s3.generate_presigned_url.return_value = "https://example.com/signed-url"
    event = {"queryStringParameters": {"name": "products.csv"}}
    response = handler(event, None)
    assert response["statusCode"] == 200
    assert response["body"] == "https://example.com/signed-url"
    mock_s3.generate_presigned_url.assert_called_once()
    call_args = mock_s3.generate_presigned_url.call_args
    assert call_args.kwargs["Params"]["Key"] == "uploaded/products.csv"
    assert call_args.kwargs["Params"]["Bucket"] == "test-bucket"


@patch("import_products_file.s3_client")
def test_returns_500_when_s3_fails(mock_s3):
    mock_s3.generate_presigned_url.side_effect = ClientError(
        error_response={
            "Error": {"Code": "InternalError", "Message": "S3 unavailable"}
        },
        operation_name="GeneratePresignedUrl",
    )

    event = {"queryStringParameters": {"name": "products.csv"}}
    response = handler(event, None)

    assert response["statusCode"] == 500
