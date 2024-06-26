using System.Collections.Generic;
using Amazon.CDK;
using Amazon.CDK.AWS.Apigatewayv2;
using Amazon.CDK.AWS.DynamoDB;
using Amazon.CDK.AWS.IAM;
using Amazon.CDK.AWS.Lambda;
using Amazon.CDK.AWS.Lambda.DotNet;
using Amazon.CDK.AWS.Lambda.EventSources;
using Amazon.CDK.AWS.Logs;
using Amazon.CDK.AWS.SQS;
using Amazon.CDK.AwsApigatewayv2Integrations;
using ChatbotDemo.Infrastructure.Models;
using Constructs;

namespace ChatbotDemo.Infrastructure.Stacks;

public sealed class WebSocketStack : Stack
{
    //For Cross-Reference
    public Table ConnectionTable { get; set; }
    public string WebSocketCallbackUrl { get; set; }

    internal WebSocketStack(Construct scope, string id, MultiStackProps props = null) : base(scope, id, props)
    {
        // DynamoDB Connection Table
        var ddbConnectionTable = new Table(this, $"{id}-connection-table", new TableProps
        {
            PartitionKey = new Attribute
            {
                Name = "connection_id",
                Type = AttributeType.STRING
            },
            BillingMode = BillingMode.PAY_PER_REQUEST,
            TableName = $"{id}-connection-table"
        });

        var onConnectFunctionName = $"{id}-on-connect-function";
        var onConnectFunction = new DotNetFunction(this, onConnectFunctionName, new DotNetFunctionProps()
        {
            FunctionName = onConnectFunctionName,
            MemorySize = 1024,
            Timeout = Duration.Seconds(30),
            Runtime = Runtime.DOTNET_8,
            Handler = "ChatbotDemo.App::ChatbotDemo.App.Functions.WsOnConnectFunction::Handler",
            LogRetention = RetentionDays.ONE_WEEK,
            ProjectDir = "./src/ChatbotDemo.App/",
            Architecture = Architecture.X86_64,
            Tracing = Tracing.ACTIVE,
            Environment = new Dictionary<string, string>
            {
                { "CONNECTION_TABLE_NAME", ddbConnectionTable.TableName },
            }
        });

        var onDisconnectFunctionName = $"{id}-on-disconnect-function";
        var onDisconnectFunction = new DotNetFunction(this, onDisconnectFunctionName, new DotNetFunctionProps()
        {
            FunctionName = onDisconnectFunctionName,
            MemorySize = 1024,
            Timeout = Duration.Seconds(30),
            Runtime = Runtime.DOTNET_8,
            Handler = "ChatbotDemo.App::ChatbotDemo.App.Functions.WsOnDisconnectFunction::Handler",
            LogRetention = RetentionDays.ONE_WEEK,
            ProjectDir = "./src/ChatbotDemo.App/",
            Architecture = Architecture.X86_64,
            Tracing = Tracing.ACTIVE,
            Environment = new Dictionary<string, string>
            {
                { "CONNECTION_TABLE_NAME", ddbConnectionTable.TableName },
            }
        });

        //SQS
        var sendMessaheDlq = new Queue(this, $"{id}-send-message-dlq", new QueueProps
        {
            Fifo = true,
            RetentionPeriod = Duration.Days(14)
        });
        var sendMessageQueue = new Queue(this, $"{id}-send-message-queue", new QueueProps
        {
            Fifo = true,
            DeadLetterQueue = new DeadLetterQueue
            {
                Queue = sendMessaheDlq,
                MaxReceiveCount = 5
            },
            RetentionPeriod = Duration.Days(14)
        });

        // Create the service proxy execution role
        var serviceProxyExecutionRole = new Role(this, $"{id}-service-proxy-execution-role", new RoleProps
        {
            RoleName = $"{id}-service-proxy-execution-role",
            AssumedBy = new ServicePrincipal("apigateway.amazonaws.com"),
            // ManagedPolicies =
            // [
            //     ManagedPolicy.FromAwsManagedPolicyName("service-role/AWSLambdaBasicExecutionRole"),
            //     ManagedPolicy.FromAwsManagedPolicyName("service-role/AmazonAPIGatewayPushToCloudWatchLogs"),
            //     ManagedPolicy.FromAwsManagedPolicyName("service-role/AWSAppSyncPushToCloudWatchLogs")
            // ]
        });

        // Add SQS permissions to the service proxy execution role
        serviceProxyExecutionRole.AddToPolicy(new PolicyStatement(new PolicyStatementProps
        {
            Actions = ["sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
            Resources = [sendMessageQueue.QueueArn, sendMessaheDlq.QueueArn]
        }));


        //Websocket API
        var webSocketApi = new WebSocketApi(this, $"{id}-web-socket-api", new WebSocketApiProps
        {
            ApiName = $"{id}-web-socket-api",
            Description = "Chatbot Demo Websocket API",
            ConnectRouteOptions = new WebSocketRouteOptions
            {
                Integration = new WebSocketLambdaIntegration($"{id}-connect-integration", onConnectFunction)
            },
            DisconnectRouteOptions = new WebSocketRouteOptions
            {
                Integration = new WebSocketLambdaIntegration($"{id}-disconnect-integration", onDisconnectFunction)
            },
            DefaultRouteOptions = new WebSocketRouteOptions
            {
                Integration = new WebSocketAwsIntegration($"{id}-send-message-integration",
                    new WebSocketAwsIntegrationProps
                    {
                        IntegrationUri = $"arn:aws:apigateway:{Region}:sqs:path/{Account}/{sendMessageQueue.QueueName}",
                        IntegrationMethod = "POST",
                        CredentialsRole = serviceProxyExecutionRole,
                        RequestParameters = new Dictionary<string, string>
                        {
                            { "integration.request.header.Content-Type", "'application/x-www-form-urlencoded'" }
                        },
                        RequestTemplates = new Dictionary<string, string>
                        {
                            {
                                "$default",
                                "Action=SendMessage&MessageGroupId=$input.path('$.MessageGroupId')&MessageDeduplicationId=$context.requestId&MessageAttribute.1.Name=connectionId&MessageAttribute.1.Value.StringValue=$context.connectionId&MessageAttribute.1.Value.DataType=String&MessageAttribute.2.Name=requestId&MessageAttribute.2.Value.StringValue=$context.requestId&MessageAttribute.2.Value.DataType=String&MessageBody=$util.urlEncode($input.json('$'))"
                            }
                        },
                        TemplateSelectionExpression = "\\$default",
                    }),
            },
        });

        var webSocketStage = new WebSocketStage(this, $"{id}-api-stage", new WebSocketStageProps
        {
            WebSocketApi = webSocketApi,
            StageName = "dev",
            AutoDeploy = true,
        });

        WebSocketCallbackUrl = webSocketStage.CallbackUrl;
        ConnectionTable = ddbConnectionTable;

        var messageFunctionName = $"{id}-message-function";
        var messageFunction = new DotNetFunction(this, messageFunctionName, new DotNetFunctionProps()
        {
            FunctionName = messageFunctionName,
            MemorySize = 1024,
            Timeout = Duration.Seconds(30),
            Runtime = Runtime.DOTNET_8,
            Handler = "ChatbotDemo.App::ChatbotDemo.App.Functions.WsMessageFunction::Handler",
            LogRetention = RetentionDays.ONE_WEEK,
            ProjectDir = "./src/ChatbotDemo.App/",
            Architecture = Architecture.X86_64,
            Tracing = Tracing.ACTIVE,
            Environment = new Dictionary<string, string>
            {
                { "WEBSOCKET_CALLBACK_URL", webSocketStage.CallbackUrl },
            },
            Events =
            [
                new SqsEventSource(sendMessageQueue, new SqsEventSourceProps
                {
                    BatchSize = 1,
                    ReportBatchItemFailures = true,
                    Enabled = true,
                })
            ]
        });

        ddbConnectionTable.GrantReadWriteData(onConnectFunction);
        ddbConnectionTable.GrantReadWriteData(onDisconnectFunction);
        webSocketApi.GrantManageConnections(messageFunction);

        _ = new CfnOutput(this, "ConnectionTableName", new CfnOutputProps
        {
            Value = ddbConnectionTable.TableName,
            Description = "Connection Table Name"
        });

        _ = new CfnOutput(this, "OnConnectFunction", new CfnOutputProps
        {
            Value = onConnectFunction.FunctionArn,
            Description = "On Connect Function ARN"
        });

        _ = new CfnOutput(this, "OnDisconnectFunction", new CfnOutputProps
        {
            Value = onDisconnectFunction.FunctionArn,
            Description = "On Disconnect Function ARN"
        });

        _ = new CfnOutput(this, "MessageFunction", new CfnOutputProps
        {
            Value = messageFunction.FunctionArn,
            Description = "Message Function ARN"
        });

        _ = new CfnOutput(this, "WebSocketApi", new CfnOutputProps
        {
            Value = webSocketApi.ApiEndpoint,
            Description = "WebSocket API Endpoint"
        });

        _ = new CfnOutput(this, "WebSocketUrl", new CfnOutputProps
        {
            Value = webSocketStage.Url,
            Description = "WebSocket Url"
        });

        _ = new CfnOutput(this, "WebSocketCallbackUrl", new CfnOutputProps
        {
            Value = webSocketStage.CallbackUrl,
            Description = "WebSocket Url"
        });
    }
}