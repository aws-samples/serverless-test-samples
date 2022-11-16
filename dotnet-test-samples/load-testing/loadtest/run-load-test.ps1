$STACK_NAME = "dotnet-test-samples"
$REGION= "us-east-1"
Write-Output "Retrieving API Url from CloudFormation stack"
$API_URL = (aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`HelloWorldApi`].OutputValue' --output text)
Write-Output "API Url found"
Write-Output $API_URL
Write-Output "Running load test"
artillery run loadtest.yml --target "$API_URL"