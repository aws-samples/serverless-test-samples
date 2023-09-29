/**
 * Integration Tests
 * Before running this test suite the stack must be deployed.
 */

import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { deleteUser, getCognitoToken, signUp } from '../helpers/cognito';

let validUserId = `VALID_USER_${uuidv4()}`;

let cognitoUserPoolId: string;
let cognitoClientId: string;

describe('AppSync Integration tests', () => {
    /**
     * Test setup
     *
     * We're using a beforeAll block to pull configuration from
     * our environment.
     * This test suite needs an AppSync URL to make HTTP requests against and
     * Cognito User Pool ID and Client ID to create and authenticate users.
     */
    let appsyncUrl: string;

    beforeAll(async () => {
        if (process.env.APPSYNC_URL === undefined) {
            throw new Error('APPSYNC_URL environment variable is not set');
        }
        if (process.env.COGNITO_USER_POOL_ID === undefined) {
            throw new Error('COGNITO_USER_POOL_ID environment variable is not set');
        }
        if (process.env.COGNITO_CLIENT_ID === undefined) {
            throw new Error('COGNITO_CLIENT_ID environment variable is not set');
        }

        appsyncUrl = process.env.APPSYNC_URL;
        cognitoClientId = process.env.COGNITO_CLIENT_ID;
        cognitoUserPoolId = process.env.COGNITO_USER_POOL_ID;
    });

    /**
     * Calling AppSync with a valid user. This test will create a user, sign them up, and then call AppSync with their credentials.
     */
    describe('given an authenticated user', () => {
        it('when they call getDemo, then a success response is returned', async () => {
            const { password } = await signUp(
                { clientId: cognitoClientId, userPoolId: cognitoUserPoolId },
                { username: validUserId },
            );

            const accessToken = await getCognitoToken(
                { clientId: cognitoClientId, userPoolId: cognitoUserPoolId },
                { username: validUserId, password },
            );

            const response = await axios({
                url: appsyncUrl,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${accessToken.AccessToken}`,
                },
                data: {
                    query: `
                        query getRandomMessage {
                            getRandomMessage {
                                message
                          }
                        }
                      `,
                },
            });

            const data = response.data.data.getRandomMessage;

            expect(response.status).toBe(200);
            expect(data.message).toBeTruthy();
        });

        afterAll(async () => {
            await deleteUser({ userPoolId: cognitoUserPoolId }, validUserId);
        });
    });
});
