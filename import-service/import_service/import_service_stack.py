from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as iam,
)
from constructs import Construct


class ImportServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self, "ImportBucket",
            bucket_name="rs-aws-import-bucket-i231nlj40ekemalezxp",  
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                )
            ],
        )

        import_products_file = _lambda.Function(
            self, "ImportProductsFileFn",
            function_name="importProductsFile",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="import_products_file.handler",
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "UPLOAD_FOLDER": "uploaded",
            },
        )

        bucket.grant_put(import_products_file)

        import_file_parser = _lambda.Function(
            self, "ImportFileParserFn",
            function_name="importFileParser",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="import_file_parser.handler",
            timeout=Duration.seconds(60),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "UPLOAD_FOLDER": "uploaded",
                "PARSED_FOLDER": "parsed",
            },
        )

        bucket.grant_read_write(import_file_parser)
        bucket.grant_delete(import_file_parser)

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(import_file_parser),
            s3.NotificationKeyFilter(prefix="uploaded/"),
        )

        api = apigw.RestApi(
            self, "ImportApi",
            rest_api_name="Import Service",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        import_resource = api.root.add_resource("import")
        import_resource.add_method(
            "GET",
            apigw.LambdaIntegration(import_products_file),
            request_parameters={
                "method.request.querystring.name": True,
            },
        )

        CfnOutput(self, "ImportApiUrl", value=api.url)
        CfnOutput(self, "BucketName", value=bucket.bucket_name)
