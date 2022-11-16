STACK_NAME=dotnet-test-samples
REGION=us-east-1

API_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`HelloWorldApi`].OutputValue' \
  --output text)

artillery run load-test.yml --target "$API_URL"