import LaunchDarkly from "launchdarkly-node-server-sdk";
import { DynamoDBFeatureStore } from "launchdarkly-node-server-sdk-dynamodb";
export const handler = async (event, context, callback) => {
  setTimeout(() => {
    const store = DynamoDBFeatureStore(process.env.DYNAMODB_TABLE, {
      cacheTTL: 30
    });
    const options = {
      featureStore: store
    };
    const client = LaunchDarkly.init(
      process.env.LAUNCHDARKLY_SDK_KEY,
      options
    );
    client.once("ready", () => {
      client.close();
      const response = {
        statusCode: 200,
        body: JSON.stringify({
          message: "Store updated",
          input: event
        })
      };
      callback(null, response);
    });
  }, 2e3);
};
