# Get Access Token
```
export CLIENT_ID=....... 
export CLIENT_SECRETE=......
export DOMAIN_NAME=....... 
curl -X POST --user $CLIENT_ID:$CLIENT_SECRETE $DOMAIN_NAME/oauth2/token?grant_type=client_credentials -H "Content-Type: application/x-www-form-urlencoded" 

{"access_token":".......","expires_in":86400,"token_type":"Bearer"}
```

# Call Rest Api 

```
export API_ENDPOINT=....... # check cdk deploy output: RestApigatewayStack.RESTAPIsEndpoint
export ACCESS_TOKEN=.......  # check client_credential's output: "access_token":"......."

curl -X GET "${API_ENDPOINT}/app/v1" -H "Authorization:${ACCESS_TOKEN}"
{"path":"/app/v1"}


```
# References
* https://docs.aws.amazon.com/apigateway/latest/developerguide/integrating-api-with-aws-services-lambda.html
* https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
* https://www.w3schools.com/tags/ref_urlencode.ASP