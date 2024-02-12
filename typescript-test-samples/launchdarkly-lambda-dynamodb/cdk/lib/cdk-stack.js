const { Stack, RemovalPolicy } = require("aws-cdk-lib");
const lambda = require("aws-cdk-lib/aws-lambda");
const dynamodb = require("aws-cdk-lib/aws-dynamodb");
const { execSync } = require("node:child_process");
const fs = require("fs");
const archiver = require("archiver");
const { constants } = require("node:fs/promises");

class CdkStack extends Stack {
  /**
   *
   * @param {Construct} scope
   * @param {string} id
   * @param {StackProps=} props
   */
  constructor(scope, id, props) {
    super(scope, id, props);

    // create a Lambda Layer using the new zip file
    const layer = new lambda.LayerVersion(this, "LaunchDarklyLayer", {
      code: lambda.Code.fromAsset("resources/layers/layer.zip"),
      description: "Common helper utility",
      compatibleRuntimes: [
        lambda.Runtime.NODEJS_16_X,
        lambda.Runtime.NODEJS_18_X,
      ],
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const flagsStarter = new lambda.Function(this, "getFlagsStarter", {
      runtime: lambda.Runtime.NODEJS_16_X,
      code: lambda.Code.fromAsset("resources/lambdas/getFlagsStarter"),
      handler: "index.js",
      layers: [layer],
      environment: {
        LAUNCHDARKLY_SDK_KEY: "YOUR_SDK_KEY_HERE",
      },
    });

    const featureStore = new dynamodb.Table(this, "FeatureStore", {
      partitionKey: {
        name: "namespace",
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: "key",
        type: dynamodb.AttributeType.STRING,
      },
    });

    const flagsDynamo = new lambda.Function(this, "getFlagsWithDynamo", {
      runtime: lambda.Runtime.NODEJS_16_X,
      code: lambda.Code.fromAsset("resources/lambdas/getFlagsWithDynamo"),
      handler: "index.js",
      layers: [layer],
      environment: {
        LAUNCHDARKLY_SDK_KEY: "YOUR_SDK_KEY_HERE",
        DYNAMODB_TABLE: featureStore.tableName,
      },
    });

    const flagsToDynamo = new lambda.Function(this, "syncFlagsToDynamo", {
      runtime: lambda.Runtime.NODEJS_16_X,
      code: lambda.Code.fromAsset("resources/lambdas/syncFlagsToDynamo"),
      handler: "index.handler",
      layers: [layer],
      environment: {
        LAUNCHDARKLY_SDK_KEY: "YOUR_SDK_KEY_HERE",
        DYNAMODB_TABLE: featureStore.tableName,
      },
    });
  }
}

module.exports = { CdkStack };
