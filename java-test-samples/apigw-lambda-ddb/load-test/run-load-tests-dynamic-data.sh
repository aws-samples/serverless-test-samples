STACK_NAME=testing-java-apigw-lambda-ddb

API_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

echo $API_URL

artillery run load-test-dynamic-data.yml --target $API_URL