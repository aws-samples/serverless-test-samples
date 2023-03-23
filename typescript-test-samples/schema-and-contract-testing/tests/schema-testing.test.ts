// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import jsonSchemaDiff from 'json-schema-diff';

// The schema can be obtained from a repository or from Amazon EventBridge Schema Registry (the latter supports only OpenAPI 3.0 and Json Schema Draft 4 versions).
// Here we're just reading schemas from a local json file for simplicity.
import schema_v1_0_0 from '../schemas/Json/CustomerCreated-v1.0.0.json';
import schema_v1_1_0 from '../schemas/Json/CustomerCreated-v1.1.0.json';
import schema_v1_2_0 from '../schemas/Json/CustomerCreated-v1.2.0.json';

test('adding new optional elements is backward compatible', async () => {    
  const initialSchema = schema_v1_0_0;
  const updatedSchema = schema_v1_1_0;

  const result = await jsonSchemaDiff.diffSchemas({
      sourceSchema: updatedSchema, 
      destinationSchema: initialSchema
  });

  const isBreakingChange = result.removalsFound;

  expect(isBreakingChange).toBeFalsy();
});

test('removing elements is a breaking change', async () => {    
  const initialSchema = schema_v1_1_0;
  const updatedSchema = schema_v1_2_0;

  const result = await jsonSchemaDiff.diffSchemas({
      sourceSchema: updatedSchema, 
      destinationSchema: initialSchema
  });

  const isBreakingChange = result.removalsFound;

  expect(isBreakingChange).toBeTruthy();
});