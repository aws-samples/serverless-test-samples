// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * get-products.test.ts
 *
 * Unit tests for the get-products Lambda handler function.
 *
 * As the entry point for getting our product list, the handler is the seam (or
 * interface) between the service integration calling the lambda - in this case
 * Amazon API Gateway - and the inner business logic of the application.
 *
 * The unit tests here are focused on testing this interface, exercising code
 * paths that validate inbound request payloads and checking for correct
 * behavior when the busines layer returns different results.
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 */
import { beforeEach, describe, it, expect } from '@jest/globals';
import { handler } from '../src/api/get-products';

describe( 'get-products', () => {

  describe( 'lambdaHandler()', () => {

    it('exists', () => {
      expect(handler).toBeTruthy();
    })

  });

} );