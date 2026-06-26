from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_lambda as _lambda,
)
from constructs import Construct
import os
from dotenv import load_dotenv

load_dotenv()

class AuthorizationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.basic_authorizer = _lambda.Function(
            self, "BasicAuthorizerFn",
            function_name="ryzk_basicAuthorizer",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="basicAuthorizer.handler",
            timeout=Duration.seconds(30),
            environment={
                "oluashua": os.getenv("oluashua", ""),
            },
        )

        CfnOutput(self, "BasicAuthorizerArn",
            value=self.basic_authorizer.function_arn,
            export_name="RyzkBasicAuthorizerArn"
        )
