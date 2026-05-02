import aws_cdk as core
import aws_cdk.assertions as assertions

from product_service.product_service_stack import ProductServiceStack

# for future tests

def test_sqs_queue_created():
    app = core.App()
    stack = ProductServiceStack(app, "product-service")
    template = assertions.Template.from_stack(stack)


