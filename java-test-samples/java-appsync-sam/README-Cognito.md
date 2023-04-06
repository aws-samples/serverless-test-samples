# Shared Resources
These resources are available to integrate and use as a boilerplate infrastructure-as-a-code (IaaC) templates.

## Amazon Cognito
[This template](cognito.yaml) creates Amazon Cognito user and identity pools. Both authorized and unauthorized roles are created for identity pool and empty administrative user group is created in the User Pool. You will need to create appropriate policies and associate them with the roles created. Please note that this stack does not create UI that could be used for interactive login and User Pool callback URL points to the localhost.

To deploy this stack use the following command:

```bash
aws cloudformation create-stack --stack-name serverless-api-cognito --template-body file://cognito.yaml --capabilities CAPABILITY_IAM
```

After stack is created you may need to create user account for authentication/authorization. 

Use AWS CLI to create and confirm a user:

```bash
aws cognito-idp sign-up --client-id <cognito user pool application client id> --username <username> --password <password> --user-attributes Name="name",Value="<username>"
aws cognito-idp admin-confirm-sign-up --user-pool-id <cognito user pool id> --username <username> 
```

After this first step step your new user account will be able to access public data and create new bookings. To add locations and resources you will need to navigate to AWS Console, pick Amazon Cognito service, select User Pool instance that was created during this deployment, navigate to "Users and Groups", and add your user to administrative users group. 

While using command line or third party tools such as Postman to test APIs, you will need to provide Identity Token in the request "Authorization" header. You can authenticate with Amazon Cognito User Pool using AWS CLI (this command is also available in SAM template outputs) and use IdToken value present in the output of the command (it is available in the stack outputs as well):

```bash
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id <cognito user pool application client id> --auth-parameters USERNAME=<username>,PASSWORD=<password>
```
To delete this stack use the following command ():

```bash
aws cloudformation delete-stack --stack-name serverless-api-cognito
```

__Customizations necessary before using__
Edit policy to tighten permissions as needed.

__Inputs__
  - UserPoolAdminGroupName - (optional) Name of User Pool group for administrative users

__Outputs__
 - UserPool - Cognito User Pool ID
 - UserPoolClient - Cognito User Pool Application Client ID
 - IdentityPool - Cognito Identity Pool ID
 - UserPoolAdminGroupName - User Pool group name for API administrators
 - CognitoIdentityPoolAuthorizedUserRole - IAM role for Cognito Identity Pool authorized users
 - CognitoLoginURL - Cognito User Pool Application Client Hosted Login UI URL
 - CognitoAuthCommand - AWS CLI command for Amazon Cognito User Pool authentication
 
