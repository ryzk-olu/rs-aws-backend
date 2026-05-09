#!/usr/bin/env python3
import os

import aws_cdk as cdk

from product_service.product_service_stack import ProductServiceStack


app = cdk.App()
ProductServiceStack(app, "ProductServiceStack")

app.synth()
