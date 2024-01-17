# Using LaunchDarkly for Testing in AWS Lambdas

## Introduction

The goal of this project is to help you get started using LaunchDarkly feature flags to test new code and features within a serverless application using AWS Lambda. The project includes everything you'll need to get started integrating feature flags into your Lambdas using the Node.js runtime.

The project uses the [AWS Cloud Development Kit](https://aws.amazon.com/cdk/) (CDK) for deployment. 

---

## Contents

- [Introduction](#introduction)
- [Contents](#contents)
- [About this Example](#about-this-example)
- [The LaunchDarkly SDKs](#the-launchDarkly-sdks)
- [Deploying via the AWS CDK](#deploying-via-the-aws-cdk)

---

## Contents

We've provided three example Lambdas to demonstrates the basics of deploying LaunchDarkly within AWS serverless.

1. **getFlagsStarter** – This example uses the LaunchDarkly Node.js server SDK to demonstrate how to initialize the SDK client, get a flag value and, as a base use case, establish separate code paths that can be tested within your Lambda. The example uses an anonymous user context which could be used for randomized experimentation or percentage-based progressive rollouts. For more granular control of targeting for testing, you can pass an environment context or send Cognito user data.
2. **getFlagsWithDynamo** – This takes the prior example but adds DynamoDB as a persistent feature store for LaunchDarkly feature flags enabling the SDK client to evaluate flag results based upon the data stored in DynamoDB. It is configured to enable daemon mode, which means that it will not call out to LaunchDarkly for these initial values, which can decrease initialization cost and reduce external requests. To disable daemon mode, remove the `useLdd` flag from the configuration.
3. **syncFlagsToDynamo** – This is a simple Lambda designed to force cache flag values into DynamoDB enabling the use of daemon mode. While this solution works, it requires the function to be called (manually or programmatically) to start the initialization. The ideal solution for this problem is to use LauchDarkly's [Relay Proxy](https://docs.launchdarkly.com/home/relay-proxy/).

For a complete guide to using LaunchDarkly in AWS serverless, including how to set up the Relay Proxy within your AWS environment and how to ensure that all events are captured by the SDKs within an ephemeral Lambda, visit [this guide](https://launchdarkly.com/blog/using-launchdarkly-in-aws-serverless/).

The project also includes the code necessary to build and deploy a Lambda Layer to easily add the necessary LaunchDarkly dependencies to any Lambda that requires them. More on how to create and use the Layer below.

## About This Example

It can be difficult to fully test features in Lambdas outside of a production cloud environment. Feature flags can be a powerful pattern for enabling and disabling features for testing. LaunchDarkly's advanced targeting capabilities allow you to create feature flags that canbe used to safely test features in production without impacting the existing experience. Using feature flags and targeting, you can run code paths that are enabled for one user or one environment (or any combination of criteria) but not for anyone else. For example, utilizing authentication, environment and identity data, you can enable features for:

* Only particular testing or staging environments
* Only particular users or segments of users
* Beta testing with managed beta access customers
* Progressive rollouts to stress testing features
* Experimentation on features or performance

...and much more. 

## The LaunchDarkly SDKs

Adding LaunchDarkly feature flags to any Lambda always begins with installing the appropriate SDK for the Lambda runtime you are using. You can find a [full list of server-side SDKs here](https://docs.launchdarkly.com/sdk). For the Node.js runtime, that would mean using NPM.

```bash
npm install launchdarkly-node-server-sdk
```

If you would like to use [DynamoDB as a persistent feature store](https://docs.launchdarkly.com/sdk/features/storing-data/dynamodb/?q=dynamo), you'll need to also install those dependencies.

```bash
npm install launchdarkly-node-server-sdk-dynamodb
```

This works well for a single Lambda, but if you are using feature flags across a number of Lambdas, the easiest method to maintain the depencies across all of them is using a Lambda Layer. The code provided here will assist you in creating the Layer.

### Creating/Updating the Lambda Layer

The necessary dependencies are already included in this project under `/cdk/resources/layers`. It contains both the Node.js SDK and the DynamoDB extension. In order to ensure that this asset has the latest versions of these SDKs, we've included a script that will download the latest versions and archive them into the proper folder. It is recommended that you run this before deploying any of the assets using the provided CDK scripts. All you need to do is:

```bash
cd  create-layer
npm run build
```

## Deploying via the AWS CDK

You'll need to install the CDK. For more details about the AWS CDK and options for installing it, please visit the [AWS docs](https://aws.amazon.com/cdk/). Once the CDK is installed, follow these commands to bootstrap the deployment and then deploy it to your configured AWS account.

```bash
cd cdk
cdk bootstrap
cdk deploy
```

This will deploy all of the assets discussed above including the Lambda Layer with the LaunchDarkly SDKs and the three example Lambdas, with the Layer as a dependency.

### TypeScript Source Files

Each of the example Lambdas (`index.mjs`) includes the TypeScript source file (`index.ts`) that was used to compile it. These source files include all of the necessary TypeScript types for LaunchDarkly. You can recompile the Lambda source file using the following commands:

```bash
cd launchdarkly-lambda-dynamodb/cdk
npm install
npm run build
```