# Asynchronous System Test with Lambda Event and DynamoDB
In this pattern, a Lambda function is configured to be an event listener to receive the SUT’s output data. DynamoDB is configured to be the event listener storage option. In Step 1 in the diagram below, the test establishes a long polling pattern with DynamoDB. In Step 2, the test sends input data to the asynchronous system under test. The async system processes the data and in Step 3 the the Lambda function receives the data and puts it into DynamoDB. The long poll queries DynamoDB and examines the result. We recommend writing tests for failure conditions including timeouts and malformed requests.

![AWS Lambda and AmazonDynamoDB](./img/lambda-dynamo.png)
