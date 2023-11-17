import aws_cdk.aws_ec2 as ec2
import aws_cdk as cdk
import aws_cdk.aws_opensearchservice as es
import aws_cdk.aws_cognito as cognito
# basic VPC configs


REGION = 'eu-west-3'
ACCOUNT = '080266302756'



lambdaconf  = {
    'name': "api-lambda-cognito"
}

api = {
    "name": "lambda-cognito-resapi",
    "stage": "test"
}

cognitopool = {
    "userpoolname":"lambda-cognito-api",
    "domain-prefix":"lambda-api-cog",
    "resourceserver": "OAuthClient-Cognito",
    "identifier": "OAuthClient-Cognito",
    "serverscopes": [
        cognito.ResourceServerScope(scope_name="app.v1.get", scope_description="allow get v1"),
        cognito.ResourceServerScope(scope_name="app.v2.get", scope_description="allow get v2")
    ],
    "outhscopes": [
        cognito.ResourceServerScope(scope_name="app.v1.get", scope_description="allow get v1"),
        cognito.ResourceServerScope(scope_name="app.v2.get", scope_description="allow get v2")
    ],
    "appclient": "cognito-app-client"
}