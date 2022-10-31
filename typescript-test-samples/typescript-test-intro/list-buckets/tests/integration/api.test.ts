// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * api.test.ts
 *
 * Integration tests for the app's HTTP API.
 *
 * These tests exercise how the system's component work together, verifying
 * that they've been configured to provide the result we're expecting. Besides
 * making sure that they're referencing each other correctly, this also verifies
 * that the security polices between components will allow the actions we expect.
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 */
import axios from 'axios';
import { describe, beforeAll, it, expect } from '@jest/globals';

describe('API Integration tests', () => {
    /**
     * Shared test setup
     *
     * In this case, we're using a beforeAll block to pull configuration from
     * our environment. These tests need a base URL to make HTTP requests against.
     * We don't want to commit this URL into our source code beacuse it may change
     * as we develop code, and between different environments like QA and Production.
     */
    let baseApiUrl: string;
    beforeAll(() => {
        if (process.env.API_URL) {
            baseApiUrl = process.env.API_URL;
        } else {
            throw new Error('API_URL environment variable is not set');
        }
    });

    describe('GET /buckets', () => {
        /**
         * Integration tests.
         *
         * Integration tests still use the "Arrange, Act, Assert" pattern: setting
         * up the request (Arrange), sending the request (Act), then checking that
         * the result matches what we expect (Assert).
         *
         * Notice that we don't have control over the response from S3 in the context
         * of this test - we're exercising the actual API Gateway, Lambda function, and
         * S3 API.
         */
        it('should return success code for http get', async () => {
            const response = await axios.get(`${baseApiUrl}/buckets`);
            expect(response.status).toBe(200);
        });
    });
});
