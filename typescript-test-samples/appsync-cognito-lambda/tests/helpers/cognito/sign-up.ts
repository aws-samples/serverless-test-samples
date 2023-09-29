import {
    AdminConfirmSignUpCommand,
    CognitoIdentityProviderClient,
    SignUpCommand,
} from '@aws-sdk/client-cognito-identity-provider';
import Chance from 'chance';

const chance = new Chance.Chance();
const cognitoClient = new CognitoIdentityProviderClient({});

export const signUp = async (
    cognitoParams: { clientId: string; userPoolId: string },
    authParams: {
        username: string;
    },
): Promise<{ userId: string; password: string }> => {
    const { clientId, userPoolId } = cognitoParams;
    const { username } = authParams;
    const password = chance.string({ length: 8 });

    try {
        const params = {
            ClientId: clientId,
            Password: password,
            Username: username,
        };
        const signUpResult = await cognitoClient.send(new SignUpCommand(params));

        if (signUpResult.UserSub === undefined) {
            throw new Error('Failed to sign up user');
        }

        await cognitoClient.send(new AdminConfirmSignUpCommand({ UserPoolId: userPoolId, Username: username }));

        return {
            userId: signUpResult.UserSub,
            password,
        };
    } catch (error: unknown) {
        console.error('signUp', error);
        throw error;
    }
};
