import aws_cdk as cdk
from authorization_stack import AuthorizationStack

app = cdk.App()
AuthorizationStack(app, "RyzkAuthorizationStack")
app.synth()
