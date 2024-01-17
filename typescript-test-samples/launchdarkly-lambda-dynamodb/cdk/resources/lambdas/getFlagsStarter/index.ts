import { Handler, APIGatewayEvent } from "aws-lambda";
// The LaunchDarkly Node Server SDK
// This needs to be npm installed or added via the Lambda Layer
import LaunchDarkly from "launchdarkly-node-server-sdk";

export const handler: Handler = async (event: APIGatewayEvent) => {
  // Initialize the client with your LaunchDarkly SDK key
  // This needs to be added to the environment variables of your Lambda function
  const client: LaunchDarkly.LDClient = LaunchDarkly.init(
    process.env.LAUNCHDARKLY_SDK_KEY as string
  );

  // wait for the SDK client to be ready
  // note that you can wait for the ready event instead
  // see the docs at https://docs.launchdarkly.com/sdk/server-side/node-js
  await client.waitForInitialization();

  // we're just using an anonymous user context for this example
  // this could be useful for randomized progressive rollouts or experimentation
  // for targeted rollouts you could use a user context passing Cognito identity information
  // or you could create an environment context with data on the function version, region, etc.
  const context: LaunchDarkly.LDContext = {
    kind: "user",
    key: "anonymous-1",
    anonymous: true,
  };

  // in this example we're just getting a simple boolean flag with the key of "new-feature"
  // we are passing the anonymous user context and setting a default value of false
  const newFeature: boolean = await client.variation(
    "new-feature",
    context,
    false
  );
  // you can implement different code paths based on the flag value
  if (newFeature) {
    // new code
  } else {
    // old code
  }

  return newFeature;
};
