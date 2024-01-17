// This function can be used to initially pull all the flag values
// from LaunchDarkly and store them in a DynamoDB table.
// The preferred way of doing this is via the Relay Proxy
// (see https://docs.launchdarkly.com/home/relay-proxy/)
import {
  Handler,
  Context,
  APIGatewayProxyCallback,
  APIGatewayEvent,
  APIGatewayProxyResult,
} from "aws-lambda";
// The LaunchDarkly Node SDKs
// These needs to be npm installed or added via the Lambda Layer
import LaunchDarkly from "launchdarkly-node-server-sdk";
// The SDK add-on for DynamoDB support
import { DynamoDBFeatureStore } from "launchdarkly-node-server-sdk-dynamodb";

export const handler: Handler = async (
  event: APIGatewayEvent,
  context: Context,
  callback: APIGatewayProxyCallback
) => {
  setTimeout(() => {
    // initialize the DyanmoDB table where we'll store the flag values
    const store = DynamoDBFeatureStore(process.env.DYNAMODB_TABLE as string, {
      cacheTTL: 30,
    });

    const options: LaunchDarkly.LDOptions = {
      featureStore: store,
    };
    const client: LaunchDarkly.LDClient = LaunchDarkly.init(
      process.env.LAUNCHDARKLY_SDK_KEY as string,
      options
    );

    // the connected DynamoDB key store will automatically updated with flag values once initialized
    client.once("ready", () => {
      client.close();
      const response: APIGatewayProxyResult = {
        statusCode: 200,
        body: JSON.stringify({
          message: "Store updated",
          input: event,
        }),
      };
      callback(null, response);
    });
  }, 2000); // initialize after some delay to ensure that LD caches have been purged
};
