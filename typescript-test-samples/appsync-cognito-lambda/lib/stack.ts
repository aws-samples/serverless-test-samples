import { CfnOutput, Stack, StackProps } from 'aws-cdk-lib';
import { AuthorizationType, Definition, GraphqlApi, MappingTemplate } from 'aws-cdk-lib/aws-appsync';
import { UserPool } from 'aws-cdk-lib/aws-cognito';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';
import { join } from 'path';

export class AppSyncCognitoLambdaStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        const randomMessageFunction = new NodejsFunction(this, 'RandomMessageHandler', {
            runtime: Runtime.NODEJS_18_X,
            entry: join(__dirname, '../functions/get-random-message/handler.ts'),
            handler: 'main',
            memorySize: 1024,
        });

        const userPool = new UserPool(this, 'DemoUserPool', {
            userPoolName: 'demo-user-pool',
            selfSignUpEnabled: true,
            autoVerify: { email: true },
            signInAliases: {
                username: true,
                email: true,
            },
            passwordPolicy: {
                minLength: 8,
                requireLowercase: false,
                requireDigits: false,
                requireUppercase: false,
                requireSymbols: false,
            },
        });
        const userPoolClient = userPool.addClient('DemoUserPoolClient', {
            userPoolClientName: 'demo-user-pool-client',
            authFlows: {
                adminUserPassword: true,
                userPassword: true,
            },
        });

        const demoApi = new GraphqlApi(this, 'DemoApi', {
            name: 'demo-api',
            definition: Definition.fromFile(join(__dirname, 'schema.graphql')),
            authorizationConfig: {
                defaultAuthorization: {
                    authorizationType: AuthorizationType.USER_POOL,
                    userPoolConfig: {
                        userPool,
                    },
                },
            },
        });

        const getDemoDataSource = demoApi.addLambdaDataSource('GetRandomMessageDataSource', randomMessageFunction);
        getDemoDataSource.createResolver('QueryGetRandomMessageResolver', {
            typeName: 'Query',
            fieldName: 'getRandomMessage',
            requestMappingTemplate: MappingTemplate.lambdaRequest(),
            responseMappingTemplate: MappingTemplate.lambdaResult(),
        });

        new CfnOutput(this, 'AppsyncUrl', {
            value: demoApi.graphqlUrl,
            description: 'The URL of the GraphQL API',
            exportName: 'APPSYNC-URL',
        });

        new CfnOutput(this, 'CognitoUserPoolId', {
            value: userPool.userPoolId,
            description: 'The User Pool ID of the User Pool',
            exportName: 'COGNITO-USER-POOL-ID',
        });

        new CfnOutput(this, 'CognitoClientId', {
            value: userPoolClient.userPoolClientId,
            description: 'The Client ID of the User Pool',
            exportName: 'COGNITO-CLIENT-ID',
        });
    }
}
