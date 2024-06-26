using Amazon.Lambda.Core;

// Assembly attribute to enable the Lambda function's JSON request to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.CamelCaseLambdaJsonSerializer))]
