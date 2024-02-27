[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS:Step Functions](https://img.shields.io/badge/AWS-Step%20Functions-blueviolet)](https://img.shields.io/badge/Step%20Functions-blueviolet)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)

# Python: AWS Step Functions Local Testing

## Introduction

[Step Functions Local testing with mocks](https://aws.amazon.com/blogs/compute/mocking-service-integrations-with-aws-step-functions-local/) 
provides the capability to mock AWS service integrations that are present in a state machine. This helps in testing the 
state machine in isolation.

This is a sample project which showcases how to run Step Functions local tests with mocks using pytest instead of running ad-hoc CLI commands. 
[Testcontainers](https://www.testcontainers.org/) is used to run the [Step Functions Local Docker image](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local-docker.html).

This is an implementation of the test strategy shown in the blog post above using pytest within Python to provide
automated testing with strong assertion capabilities.

---

## Contents

- [Introduction](#introduction)
- [Contents](#contents)
- [About this Pattern](#about-this-pattern)
- [About this Example](#about-this-example)
  - [Key Files in the Project](#key-files-in-the-project)
- [Sample project description](#sample-project-description)
- [Unit Test](#unit-test)

---

## About this Pattern

### System Under Test (SUT)

The SUT is a sales lead generation sample workflow implemented with AWS Step Functions. In this example, new sales leads are created in a customer relationship management system.  This triggers the sample workflow execution using [input data](statemachine/test/valid_input.json), which provides information about the contact.

Using the sales lead data, the workflow first validates the contact’s identity and address. If valid, it uses Step Functions’ AWS SDK integration for [Amazon Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/how-sentiment.html) to call the [DetectSentiment](https://docs.aws.amazon.com/comprehend/latest/dg/API_DetectSentiment.html) API. It uses the sales lead’s comments as input for sentiment analysis.

If the comments have a positive sentiment, it adds the sales leads information to a DynamoDB table for follow-up. The event is published to [Amazon EventBridge](https://aws.amazon.com/eventbridge/) to notify subscribers.

If the sales lead data is invalid or a negative sentiment is detected, it publishes events to EventBridge for notification. No record is added to the [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table. The following Step Functions Workflow Studio diagram shows the control logic:

![System Under Test (SUT)](img/stepfunctions_local_test.png)

### Goal

The goal of this example is to test AWS Step Functions state machines in isolation using mocked responses for the external services which need to conform to actual responses before testing. With mocking, developers get more control over the type of scenarios that a state machine can handle, leading to assertion of multiple behaviors. Testing a state machine with mocks can also be part of the software release. Asserting on behaviors like error handling, branching, parallel, dynamic parallel (map state) helps test the entire state machine’s behavior. For any new behavior in the state machine, such as a new type of exception from a state, you can mock and add as a test.

### Description

In this example, you test a scenario in which:

1. The identity and address are successfully validated using a Lambda function.
2. A positive sentiment is detected using the Comprehend.DetectSentiment API after three retries.
3. A contact item is written to a DynamoDB table successfully
4. An event is published to an EventBridge event bus successfully

The execution path for this test scenario is shown in the following diagram (the red and green numbers have been added). 0 represents the first execution; 1, 2, and 3 represent the max retry attempts (MaxAttempts), in case of an InternalServerException.

![System Under Test Description (SUT)](img/system-under-test-description.png)

[Top](#contents)

---

## About this Example

To use service integration mocking, [create a mock configuration file](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local-test-sm-exec.html) with sections specifying mock AWS service responses. These are grouped into test cases that can be activated when executing state machines locally. The following example provides code snippets and the full mock configuration is available in the [code repository](statemachine/test/MockConfigFile.json).

To mock a successful Lambda function invocation, define a mock response that conforms to the [Lambda.Invoke](https://docs.aws.amazon.com/lambda/latest/dg/API_Invoke.html#API_Invoke_ResponseElements) API response elements. Associate it to the first request attempt:

```json
"CheckIdentityLambdaMockedSuccess": {
  "0": {
    "Return": {
      "StatusCode": 200,
      "Payload": {
        "statusCode": 200,
        "body": "{\"approved\": true}"
      }
    }
  }
}
```

To mock the DetectSentiment retry behavior, define failure and successful mock responses that conform to the [Comprehend.DetectSentiment](https://docs.aws.amazon.com/comprehend/latest/dg/API_DetectSentiment.html#API_DetectSentiment_ResponseElements) API call. Associate the failure mocks to three request attempts, and associate the successful mock to the fourth attempt:

```json
"DetectSentimentRetryOnErrorWithSuccess": {
  "0-2": {
    "Throw": {
      "Error": "InternalServerException",
      "Cause": "Server Exception while calling DetectSentiment API in Comprehend Service"
    }
  },
  "3": {
    "Return": {
      "Sentiment": "POSITIVE",
      "SentimentScore": {
        "Mixed": 0.00012647535,
        "Negative": 0.00008031699,
        "Neutral": 0.0051454515,
        "Positive": 0.9946478
      }
    }
  }
}

```

Note that Step Functions Local does not validate the structure of the mocked responses. Ensure that your mocked responses conform to actual responses before testing. To review the structure of service responses, either perform the actual service calls using Step Functions or view the documentation for those services.

Next, associate the mocked responses to a test case identifier:

```json
"RetryOnServiceExceptionTest": {
  "Check Identity": "CheckIdentityLambdaMockedSuccess",
  "Check Address": "CheckAddressLambdaMockedSuccess",
  "DetectSentiment": "DetectSentimentRetryOnErrorWithSuccess",
  "Add to FollowUp": "AddToFollowUpSuccess",
  "CustomerAddedToFollowup": "CustomerAddedToFollowupSuccess"
}
```

With the test case and mock responses configured, you can use them for testing with Step Functions Local.

### Key Files in the Project

  - [local_testing.asl.json](statemachine/local_testing.asl.json) - State machine definition in ASL
  - [valid_input.json](statemachine/test/valid_input.json) - State machine unit test input event
  - [MockConfigFile.json](statemachine/test/MockConfigFile.json) - Unit test mocked responses
  - [test_step_functions_local.py](tests/unit/src/test_step_functions_local.py) - Unit tests definition

[Top](#contents)

---

## Unit Test

### Prerequisites
 - Python 3.9 or newer
 - [Docker](https://www.docker.com/)
 
### Test flow

The unit test flow in [test_step_funtions_local.py](tests/unit/src/test_step_functions_local.py) is:

- ```fixture_container``` downloads and starts the  ```amazon/aws-stepfunctions-local``` 
  container locally
- ```fixture_sfn_client``` then creates the state machine using the definition from [local_testing.
  asl.json](statemachine/local_testing.asl.json)
- When a test runs it calls ```execute_stepfunction```.  This executes the state machine passing 
  the input in [valid_input.json](statemachine/test/valid_input.json) and appending ```test_name``` to 
  the state machine ARN. ```test_name``` is used to look up the TestCase entry in [MockConfigFile.json](statemachine/test/MockConfigFile.json) which defines which 
  mocked responses to use.  ```execute_stepfunction``` returns the list of events from the state 
  machine execution.
- After all the tests have run, the container is shut down by the ```stop_step_function``` 
  finalizer added in ```fixture_container```

### Unit Test description

This example contains a [sample event](statemachine/test/valid_input.json) with new user registration data to be processed by the state machine. The unit tests will check how the state machine behaves for each of the following scenarios defined in the [MockConfigFile.json](statemachine/test/MockConfigFile.json) file:

- `HappyPathTest`: every external service runs succesfully and the state machine exits with "CustomerAddedToFollowup". 
- `NegativeSentimentTest`: the contact details are properly formatted, a negative sentiment is detected within the user comments and the state machine exits with "NegativeSentimentDetected".
- `RetryOnServiceExceptionTest`: the sentiment detection service fails three times and the state machine retries until successfully retrieving the sentiment in the fourth attempt.

### Run the Unit Test
> Make sure docker engine is running before running the tests.

``` shell
step-functions-local$ docker version
Client: Docker Engine - Community
 Version:           24.0.6
 API version:       1.43
...
```

To set it up:

``` shell
step-functions-local$ cd tests
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```


To run the unit tests:

``` shell
step-functions-local$ cd tests
python3 -m pytest -s unit/src/test_step_functions_local.py -v
```

[Top](#contents)

---
