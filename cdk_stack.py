from aws_cdk import (
    # Duration,
    Stack,
    CfnTag,
    Fn,
    RemovalPolicy
    # aws_sqs as sqs,
)

import os
from constructs import Construct
from aws_cdk import aws_kinesis as kinesis
from aws_cdk import aws_lambda as _lambda
import aws_cdk.aws_apigateway as apg
import aws_cdk.aws_cognito as cognito
import aws_cdk as cdk
from config import (
      lambdaconf,
      cognitopool,
      api,
      REGION
    )



class CDKStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.userPool = cognito.UserPool(self,"AWSElasticSearchCognitoUserPool", 
            user_pool_name = cognitopool["userpoolname"],
            removal_policy = RemovalPolicy.DESTROY
        )
        
        self.serverresource = self.userPool.add_resource_server("UserPoolResourceServer",
           identifier = cognitopool["identifier"],
           user_pool_resource_server_name = cognitopool["resourceserver"],
           scopes = cognitopool["serverscopes"]
        )
        
        self.clientscopes = self.client_scope_method()
        
        self.userPool.add_client(
            "UserPoolAppClient",
            user_pool_client_name= cognitopool["appclient"],
            access_token_validity = cdk.Duration.days(1),
            id_token_validity = cdk.Duration.days(1),
            generate_secret = True,
            auth_flows = cognito.AuthFlow(
              admin_user_password = False,
              custom = True,
              user_password = False
            ),
            o_auth = cognito.OAuthSettings(
                flows = cognito.OAuthFlows(
                    authorization_code_grant = False,
                    implicit_code_grant = False,
                    client_credentials = True
                ),
                scopes = self.clientscopes
            ),
        )
        
        cognito.UserPoolDomain(self,"CognitoUserPoolDomain", 
           user_pool = self.userPool,
           cognito_domain = cognito.CognitoDomainOptions(
                domain_prefix=cognitopool["domain-prefix"]
            )
        )
        
        
        authorizer = apg.CognitoUserPoolsAuthorizer(self, "AWSCognitoAuthorizer",
                cognito_user_pools=[self.userPool]
            )
            
        # Lambda
        self.function = _lambda.Function(
            self, "LambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="main.handler",
            code=_lambda.Code.from_asset("src"),
            timeout=cdk.Duration.minutes(2),
            function_name=lambdaconf['name']
        )
        
        # Rest Api
        restapi = apg.RestApi(self, "AWSApiGateway",
               deploy=True,
               rest_api_name = api['name'],
               deploy_options= apg.StageOptions(
                   stage_name = api['stage']
                 ),
               endpoint_types=[apg.EndpointType.REGIONAL]
            )
            
        app = restapi.root.add_resource("app")
        v1  = app.add_resource("v1")
            
        methodreponse200 = apg.MethodResponse(
                status_code="200",
                response_models={
                    "application/json":apg.Model.EMPTY_MODEL
                }
            )
        
        integrationreponse = apg.IntegrationResponse(status_code="200",
                #response_parameters={
                #    "method.response.header.Status":"integration.response.header.Status"
               # },
                response_templates={
                    "application/json": "{ 'statusCode': 200 }"
                }
            )
        
        v1.add_cors_preflight(
                allow_origins=["*"],
                allow_headers=apg.Cors.DEFAULT_HEADERS,
                allow_methods=apg.Cors.ALL_METHODS,
                status_code=204
            )
            
        v1.add_method("GET",
                        integration=apg.LambdaIntegration(
                            self.function
                        ),
                        request_parameters={
                            "method.request.header.Authorization": True,
                        },
                        authorization_type = apg.AuthorizationType.COGNITO,
                        authorization_scopes = [f"{cognitopool['identifier']}/app.v1.get"],
                        authorizer=authorizer,
                        method_responses=[
                             methodreponse200,
                        ]
                )
        
        v2  = app.add_resource("v2")
        
        v2.add_cors_preflight(
                allow_origins=["*"],
                allow_headers=apg.Cors.DEFAULT_HEADERS,
                allow_methods=apg.Cors.ALL_METHODS,
                status_code=204
            )
            
        v2.add_method("GET",
                        integration=apg.LambdaIntegration(
                            self.function
                        ),
                        request_parameters={
                            "method.request.header.Authorization": True,
                        },
                        authorization_type = apg.AuthorizationType.COGNITO,
                        authorization_scopes = [f"{cognitopool['identifier']}/app.v2.get"],
                        authorizer=authorizer,
                        method_responses=[
                             methodreponse200,
                        ]
                )
                
        
                
    def client_scope_method(self):
        outhscopes = []
        for scope in cognitopool["outhscopes"]:
            outhscopes.append(cognito.OAuthScope.resource_server(self.serverresource, scope))
                
        return outhscopes