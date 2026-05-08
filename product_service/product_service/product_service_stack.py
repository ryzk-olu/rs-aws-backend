from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        get_products_list = _lambda.Function(
            self, "GetProductsListFn",
            function_name="getProductsList",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="get_products_list.handler",
        )

        get_products_by_id = _lambda.Function(
            self, "GetProductsByIdFn",
            function_name="getProductsById",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="get_products_by_id.handler",
        )

        api = apigw.RestApi(
            self, "ProductsApi",
            rest_api_name="Products Service",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        products = api.root.add_resource("products")
        products.add_method("GET", apigw.LambdaIntegration(get_products_list))

        product_by_id = products.add_resource("{productId}")
        product_by_id.add_method("GET", apigw.LambdaIntegration(get_products_by_id))

        CfnOutput(self, "ApiUrl", value=api.url)
