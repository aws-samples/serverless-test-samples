import {
    AdminInitiateAuthCommand,
    AdminInitiateAuthRequest,
    AuthenticationResultType,
    CognitoIdentityProviderClient,
} from '@aws-sdk/client-cognito-identity-provider';

const cognitoClient = new CognitoIdentityProviderClient({});

export const getCognitoToken = async (
    cognitoParams: { clientId: string; userPoolId: string },
    authParams: { username: string; password: string },
): Promise<AuthenticationResultType> => {
    const { clientId, userPoolId } = cognitoParams;
    const { username, password } = authParams;

    try {
        const params = <AdminInitiateAuthRequest>{
            AuthFlow: 'ADMIN_USER_PASSWORD_AUTH',
            ClientId: clientId,
            UserPoolId: userPoolId,
            AuthParameters: {
                USERNAME: username,
                PASSWORD: password,
            },
        };

        const authResult = await cognitoClient.send(new AdminInitiateAuthCommand(params));

        if (authResult.AuthenticationResult === undefined) {
            throw new Error('Failed to retrieve Cognito token');
        }

        return authResult.AuthenticationResult;
    } catch (error: unknown) {
        console.error('getCognitoToken', error);
        throw error;
    }
};
