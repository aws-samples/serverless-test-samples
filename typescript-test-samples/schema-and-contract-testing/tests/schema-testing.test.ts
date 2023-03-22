// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import openapiDiff from 'openapi-diff';
import fs from 'fs';

// The schema can be obtained from a repository or Amazon EventBridge Schema Registry;
// here we're just reading it from a local json file for simplicity
import schema_v1_0_0 from '../schemas/CustomerCreated-v1.0.0.json';
import schema_v1_1_0 from '../schemas/CustomerCreated-v1.1.0.json';
import schema_v1_2_0 from '../schemas/CustomerCreated-v1.2.0.json';

test('adding new elements is backward compatible', async () => {    

  const initialSchema = schema_v1_0_0;
  const updatedSchema = schema_v1_1_0;

  const result = await openapiDiff.diffSpecs({
    sourceSpec: {
      content: JSON.stringify(initialSchema),
      location: 'initialSchema.json',
      format: 'openapi3'
    },
    destinationSpec: {
      content: JSON.stringify(updatedSchema),
      location: 'updatedSchema.json',
      format: 'openapi3'
    }
  });

  console.log("result: ", result);

  expect(result.breakingDifferencesFound).toBeFalsy();
});

test('removing elements is a breaking change', async () => {    

  const initialSchema = schema_v1_1_0;
  const updatedSchema = schema_v1_2_0;

  const result = await openapiDiff.diffSpecs({
    sourceSpec: {
      content: JSON.stringify(initialSchema),
      location: 'initialSchema.json',
      format: 'openapi3'
    },
    destinationSpec: {
      content: JSON.stringify(updatedSchema),
      location: 'updatedSchema.json',
      format: 'openapi3'
    }
  });

  console.log("result: ", result);

  expect(result.breakingDifferencesFound).toBeTruthy();
});