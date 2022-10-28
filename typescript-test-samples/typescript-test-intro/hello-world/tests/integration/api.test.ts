// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from 'axios';
import { beforeAll, it, expect } from '@jest/globals';

let baseApiUrl: string;

beforeAll(() => {
    if (process.env.API_URL) {
        baseApiUrl = process.env.API_URL;
    } else {
        throw new Error('API_URL environment variable is not set');
    }
});

it('should return sucess code for http get', async () => {
    console.log(`${baseApiUrl}/hello`);
    const response = await axios.get(`${baseApiUrl}/hello`);
    expect(response.status).toBe(200);
});
