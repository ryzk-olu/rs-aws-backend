from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as event_sources,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)
from constructs import Construct


class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        products_table = dynamodb.Table(self, 'ProductsTable',
            table_name='ryzk_products',
            partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        stocks_table = dynamodb.Table(self, 'StocksTable',
            table_name='ryzk_stocks',
            partition_key=dynamodb.Attribute(name='product_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        catalog_items_queue = sqs.Queue(self, "CatalogItemsQueue",
            queue_name="ryzk_catalogItemsQueue",
            visibility_timeout=Duration.seconds(60),
        )

        create_product_topic = sns.Topic(self, "CreateProductTopic",
            topic_name="ryzk_createProductTopic",
        )

        create_product_topic.add_subscription(
            subscriptions.EmailSubscription("olga.ryzhkova.v@gmail.com")
        )

        create_product_topic.add_subscription(
            subscriptions.EmailSubscription(
                "olga.ryzhkova.v+expensive@gmail.com",
                filter_policy={
                    "price": sns.SubscriptionFilter.numeric_filter(
                        greater_than_or_equal_to=100
                    )
                },
            )
        )

        common_env = {
            'PRODUCTS_TABLE': products_table.table_name,
            'STOCKS_TABLE': stocks_table.table_name,
        }

        get_products_list = _lambda.Function(
            self, "GetProductsListFn",
            function_name="ryzk_getProductsList",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="get_products_list.handler",
            environment=common_env,
        )

        get_products_by_id = _lambda.Function(
            self, "GetProductsByIdFn",
            function_name="ryzk_getProductsById",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="get_products_by_id.handler",
            environment=common_env,
        )

        create_product = _lambda.Function(self, 'CreateProduct',
            function_name='ryzk_createProduct',
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler='create_product.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment=common_env,
        )

        catalog_batch_process = _lambda.Function(self, "CatalogBatchProcessFn",
            function_name="ryzk_catalogBatchProcess",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="catalog_batch_process.handler",
            timeout=Duration.seconds(30),
            environment={
                'PRODUCTS_TABLE': products_table.table_name,
                'STOCKS_TABLE': stocks_table.table_name,
                'SNS_TOPIC_ARN': create_product_topic.topic_arn,
            },
        )

        catalog_batch_process.add_event_source(
            event_sources.SqsEventSource(catalog_items_queue, batch_size=5)
        )

        api = apigw.RestApi(
            self, "ProductsApi",
            rest_api_name="Ryzk Products Service",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        for fn in [get_products_list, get_products_by_id, create_product]:
            products_table.grant_read_write_data(fn)
            stocks_table.grant_read_write_data(fn)

        products_table.grant_read_write_data(catalog_batch_process)
        stocks_table.grant_read_write_data(catalog_batch_process)
        create_product_topic.grant_publish(catalog_batch_process)

        products = api.root.add_resource("products")
        products.add_method("GET", apigw.LambdaIntegration(get_products_list))
        product_by_id = products.add_resource("{productId}")
        product_by_id.add_method("GET", apigw.LambdaIntegration(get_products_by_id))
        products.add_method("POST", apigw.LambdaIntegration(create_product))

        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "CatalogItemsQueueArn",
            value=catalog_items_queue.queue_arn,
            export_name="RyzkCatalogItemsQueueArn",
        )
        CfnOutput(self, "CatalogItemsQueueUrl",
            value=catalog_items_queue.queue_url,
            export_name="RyzkCatalogItemsQueueUrl",
        )
