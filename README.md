## Introduction
This repository contains sample code demonstrating a variety of test patterns for serverless applications.

## Testing in the Cloud
Well-designed serverless applications may employ a variety of testing techniques to satisfy a range of requirements and conditions. However, based on current tooling, we recommend customers **focus on testing in the cloud** as much as possible. While testing in the cloud may create additional developer latency, increase costs, and require some customers to invest in additional dev-ops controls, this technique provides the most reliable, accurate, and complete test coverage. Performing tests in the context of the cloud allows you to test IAM policies, service configurations, quotas, and the most up to date API signatures and return values. Tests run in the cloud are most likely to produce consistent results as your code is promoted from environment to environment.

## Accelerate Feedback Loops
When testing in the cloud we encourage developers to explore options for accelerating feedback loops and also to consider cost optimization techniques. The samples in this guide explore some of these techniques including [AWS Serverless Application Model (SAM) Accelerate](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/) and [AWS Cloud Development Kit (CDK) Watch](https://aws.amazon.com/blogs/developer/increasing-development-speed-with-cdk-watch/).

## Mocks and Emulators
Mock frameworks can be useful for writing fast unit tests, especially for testing complex internal business logic or mathematical operations. Emulators may be convenient for some use cases but we encourage developers to use them sparingly, due to lack of feature parity with actual cloud services, configuration costs, and limited emulator service coverage. Mocks and emulators can be valuable testing tools, but they cannot provide the complete test coverage that testing in the cloud provides.  

## Sample Code
The sample code in this project will illustrate techniques for creating automated tests in several languages. The initial samples are written in Python and we will publish samples in other languages over time. The samples demonstrate a variety of approaches including testing in the cloud, mocking and emulation. 

- [Python Samples](./python-test-samples/)
- Java Sample (coming soon)
- .NET Sample (coming soon)
- TypeScript Sample (coming soon)
- Go Sample (coming soon)

