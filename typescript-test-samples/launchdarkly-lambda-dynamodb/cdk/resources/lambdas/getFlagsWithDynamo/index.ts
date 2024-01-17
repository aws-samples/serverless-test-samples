import { Handler, APIGatewayEvent } from "aws-lambda";
// The LaunchDarkly Node SDKs
// These needs to be npm installed or added via the Lambda Layer
import LaunchDarkly from "launchdarkly-node-server-sdk";
// The SDK add-on for DynamoDB support
import { DynamoDBFeatureStore } from "launchdarkly-node-server-sdk-dynamodb";

export const handler: Handler = async (event: APIGatewayEvent) => {
  // this establishes the settings for caching in Dynamo
  // for details, check the documentation at https://docs.launchdarkly.com/sdk/features/storing-data/dynamodb
  const store = DynamoDBFeatureStore(process.env.DYNAMODB_TABLE as string, {
    cacheTTL: 30,
  });
  // pass in the flag store as an option to the SDK client
  // useLdd puts the client in daemon mode, relying on DynamoDB as the source of truth for flags
  // leave useLdd off if you are not syncing all flags to a DynamoDB table
  // this will use the DyanmoDB table as a cache, but will still rely on the LaunchDarkly API for flag evaluations
  const options: LaunchDarkly.LDOptions = {
    featureStore: store,
    useLdd: true,
  };
  const client: LaunchDarkly.LDClient = LaunchDarkly.init(
    process.env.LAUNCHDARKLY_SDK_KEY as string,
    options
  );
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
