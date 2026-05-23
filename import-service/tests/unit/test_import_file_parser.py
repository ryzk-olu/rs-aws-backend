import os
from unittest.mock import patch, MagicMock
from io import BytesIO

os.environ["BUCKET_NAME"] = "test-bucket"
os.environ["UPLOAD_FOLDER"] = "uploaded"
os.environ["PARSED_FOLDER"] = "parsed"

from import_file_parser import handler


@patch("import_file_parser.s3_client")
def test_parses_csv_and_moves_file(mock_s3):
    csv_content = b"title,price\nMouse,15\nKeyboard,80\n"
    mock_s3.get_object.return_value = {"Body": BytesIO(csv_content)}

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "uploaded/test.csv"},
                }
            }
        ]
    }

    response = handler(event, None)

    assert response["statusCode"] == 200
    mock_s3.get_object.assert_called_once_with(
        Bucket="test-bucket", Key="uploaded/test.csv"
    )
    mock_s3.copy_object.assert_called_once()
    mock_s3.delete_object.assert_called_once()
