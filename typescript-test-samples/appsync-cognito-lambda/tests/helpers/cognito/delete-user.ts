import { AdminDeleteUserCommand, CognitoIdentityProviderClient } from '@aws-sdk/client-cognito-identity-provider';

const cognitoClient = new CognitoIdentityProviderClient({});

export const deleteUser = async (cognitoParams: { userPoolId: string }, username: string): Promise<void> => {
    const { userPoolId } = cognitoParams;

    try {
        const deleteUserResult = await cognitoClient.send(
            new AdminDeleteUserCommand({
                UserPoolId: userPoolId,
                Username: username,
            }),
        );

        if (deleteUserResult.$metadata.httpStatusCode !== 200) {
            throw new Error('Failed to delete user');
        }
    } catch (error: unknown) {
        console.error('deleteUser', error);
        throw error;
    }
};
