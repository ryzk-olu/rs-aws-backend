import os
import base64

def handler(event, context):
    token = event.get('authorizationToken', '')
    method_arn = event.get('methodArn', '')

    if not token:
        raise Exception('Unauthorized')

    try:
        encoded = token.replace('Basic ', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        username, password = decoded.split(':', 1)
    except Exception:
        raise Exception('Unauthorized')

    expected_password = os.environ.get(username, '')

    if not expected_password:
        return generate_policy(username, 'Deny', method_arn)

    if expected_password == password:
        return generate_policy(username, 'Allow', method_arn)
    else:
        return generate_policy(username, 'Deny', method_arn)

def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
