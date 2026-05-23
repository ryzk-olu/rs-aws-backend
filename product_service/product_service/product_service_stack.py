from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
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

        products = api.root.add_resource("products")
        products.add_method("GET", apigw.LambdaIntegration(get_products_list))

        product_by_id = products.add_resource("{productId}")
        product_by_id.add_method("GET", apigw.LambdaIntegration(get_products_by_id))
        products.add_method("POST", apigw.LambdaIntegration(create_product))

        CfnOutput(self, "ApiUrl", value=api.url)
