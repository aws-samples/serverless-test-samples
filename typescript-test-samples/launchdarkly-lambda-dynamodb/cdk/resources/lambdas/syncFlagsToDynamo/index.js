// This function can be used to initially pull all the flag values
// from LaunchDarkly and store them in a DynamoDB table.
// The preferred way of doing this is via the Relay Proxy
// (see https://docs.launchdarkly.com/home/relay-proxy/)

// The LaunchDarkly Node SDKs
// These needs to be npm installed or added via the Lambda Layer
const LaunchDarkly = require("launchdarkly-node-server-sdk");
// The SDK add-on for DynamoDB support
const {
  DynamoDBFeatureStore,
} = require("launchdarkly-node-server-sdk-dynamodb");

exports.handler = (event, context, callback) => {
  setTimeout(() => {
    // initialize the DyanmoDB table where we'll store the flag values
    const store = DynamoDBFeatureStore(process.env.DYNAMODB_TABLE, {
      cacheTTL: 30,
    });

    var ldConfig = {
      featureStore: store,
    };
    var client = LaunchDarkly.init(process.env.LAUNCHDARKLY_SDK_KEY, ldConfig);

    // the connected DynamoDB key store will automatically updated with flag values once initialized
    client.once("ready", () => {
      client.close();
      callback(null, "store updated");
    });
  }, 2000); // initialize after some delay to ensure that LD caches have been purged
};
