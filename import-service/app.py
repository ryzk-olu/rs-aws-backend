#!/usr/bin/env python3
import os

import aws_cdk as cdk

from import_service.import_service_stack import ImportServiceStack


app = cdk.App()
ImportServiceStack(app, "RyzkImportServiceStack",
    )

app.synth()
