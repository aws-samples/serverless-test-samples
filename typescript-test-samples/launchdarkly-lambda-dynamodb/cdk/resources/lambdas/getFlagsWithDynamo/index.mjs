import LaunchDarkly from "launchdarkly-node-server-sdk";
import { DynamoDBFeatureStore } from "launchdarkly-node-server-sdk-dynamodb";
export const handler = async (event) => {
  const store = DynamoDBFeatureStore(process.env.DYNAMODB_TABLE, {
    cacheTTL: 30
  });
  const options = {
    featureStore: store,
    useLdd: true
  };
  const client = LaunchDarkly.init(
    process.env.LAUNCHDARKLY_SDK_KEY,
    options
  );
  await client.waitForInitialization();
  const context = {
    kind: "user",
    key: "anonymous-1",
    anonymous: true
  };
  const newFeature = await client.variation(
    "new-feature",
    context,
    false
  );
  if (newFeature) {
  } else {
  }
  return newFeature;
};
