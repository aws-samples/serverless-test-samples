## Step Functions Local Testing using Jest
[Step Functions Local testing with mock configuration](https://aws.amazon.com/blogs/compute/mocking-service-integrations-with-aws-step-functions-local/) 
provides the capability to mock AWS service integrations that are present in a state machine. This helps in testing the 
state machine in isolation.

This is sample project which showcases how to run Step Functions local tests with mocks using Jest instead of running ad-hoc CLI commands. [Testcontainers](https://www.testcontainers.org/) is used to run [Step Functions Local Docker image](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local-docker.html).

This is not a replacement of the strategy shown in above blog but another way to test Step Functions state machine with
better assertion capabilities. Teams currently using Javascript / Typescript for Serverless development can leverage this strategy in their
current applications.

### Prerequisites
 - Node.js v14 or newer
 - [Jest](https://jestjs.io/docs/getting-started)
 - [Testcontainers](https://www.testcontainers.org/)
 - [Docker](https://www.docker.com/)

### Running Tests
> Make sure docker engine is running before running the tests.

In order to install the dependencies, just run below command from project "src" subdirectory:
```bash
npm install
```

In order to run the tests, just run below command from project "src" subdirectory:
```bash
npm run test
```

### Explanation
Checkout this file for details:

 - [`step-functions-local.test.ts`](src/tests/sfnLocal/step-functions-local.test.ts)