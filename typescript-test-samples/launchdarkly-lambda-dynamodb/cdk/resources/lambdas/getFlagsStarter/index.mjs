import LaunchDarkly from "launchdarkly-node-server-sdk";
export const handler = async (event) => {
  const client = LaunchDarkly.init(
    process.env.LAUNCHDARKLY_SDK_KEY
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
