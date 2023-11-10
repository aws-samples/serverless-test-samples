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
     * Calling AppSync with a valid user. This test will create a user, sign them in, and then call AppSync with their credentials.
     * After the test is complete, the user will be deleted.
     */
    describe('given an authenticated user', () => {
        let userPassword: string;

        beforeAll(async () => {
            const { password } = await signUp(
                { clientId: cognitoClientId, userPoolId: cognitoUserPoolId },
                { username: validUserId },
            );

            userPassword = password;
        });

        it('when they call getDemo, then a success response is returned', async () => {
            const accessToken = await getCognitoToken(
                { clientId: cognitoClientId, userPoolId: cognitoUserPoolId },
                { username: validUserId, password: userPassword },
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

    /**
     * Calling AppSync with an anonymous user. This test will attempt to call AppSync without any credentials.
     * We expect to receive an unauthorized response, indicating that our auth is configured correctly.
     */
    describe('given an anonymous user', () => {
        it('when they call getDemo, then an unauthorized response is returned', async () => {
            try {
                const response = await axios({
                    url: appsyncUrl,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
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

                // We expect this not to be called because the request should fail
                expect(response.status).not.toBe(200);
            } catch (error) {
                // Here we check if the error is an unauthorized error
                if (axios.isAxiosError(error)) {
                    expect(error.response?.status).toBe(401); // 401 Unauthorized
                } else {
                    // Rethrow if we got an unexpected error
                    throw error;
                }
            }
        });
    });
});
