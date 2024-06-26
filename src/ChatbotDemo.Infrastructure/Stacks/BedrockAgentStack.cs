using System.Collections.Generic;
using System.IO;
using Amazon.CDK;
using Amazon.CDK.AWS.Lambda;
using Amazon.CDK.AWS.Lambda.DotNet;
using Amazon.CDK.AWS.Logs;
using Amazon.CDK.AWS.S3;
using Amazon.CDK.AwsBedrock;
using Cdklabs.GenerativeAiCdkConstructs.Bedrock;
using ChatbotDemo.Infrastructure.Models;
using Constructs;

namespace ChatbotDemo.Infrastructure.Stacks
{
    public class BedrockAgentStack : Stack
    {
        internal BedrockAgentStack(Construct scope, string id, MultiStackProps props = null) : base(scope, id, props)
        {
            var accessLogBucket = new Bucket(this, $"{id}-access-logs", new BucketProps
            {
                EnforceSSL = true,
                Versioned = true,
                PublicReadAccess = false,
                BlockPublicAccess = BlockPublicAccess.BLOCK_ALL,
                Encryption = BucketEncryption.S3_MANAGED,
                RemovalPolicy = RemovalPolicy.DESTROY,
                AutoDeleteObjects = true
            });

            var docBucket = new Bucket(this, $"{id}-doc-bucket", new BucketProps
            {
                EnforceSSL = true,
                Versioned = true,
                PublicReadAccess = false,
                BlockPublicAccess = BlockPublicAccess.BLOCK_ALL,
                Encryption = BucketEncryption.S3_MANAGED,
                RemovalPolicy = RemovalPolicy.DESTROY,
                AutoDeleteObjects = true,
                ServerAccessLogsBucket = accessLogBucket,
                ServerAccessLogsPrefix = "inputsAssetsBucketLogs/"
            });

            var knowledgeBase = new KnowledgeBase(this, $"{id}-kb", new KnowledgeBaseProps
            {
                EmbeddingsModel = BedrockFoundationModel.TITAN_EMBED_TEXT_V1,
                Instruction =
                    @"Use this knowledge base to answer questions about food items. It contains the full detail of food items like product name, size , nutrients contained, description, shelf life and other information."
            });

            var dataSource = new S3DataSource(this, $"{id}-data-source", new S3DataSourceProps
            {
                Bucket = docBucket,
                KnowledgeBase = knowledgeBase,
                DataSourceName = $"{id}-data-source",
                ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                MaxTokens = 500,
                OverlapPercentage = 20
            });

            var agentInstruction = Path.Combine(Directory.GetCurrentDirectory(), "Instruction/agent-instruction.txt");

            var bedrockAgent = new Agent(this, $"{id}-agent", new AgentProps
            {
                FoundationModel = BedrockFoundationModel.ANTHROPIC_CLAUDE_SONNET_V1_0,
                Instruction = agentInstruction,
                KnowledgeBases = [knowledgeBase],
                EnableUserInput = true,
                ShouldPrepareAgent = true,
            });

            var actionGroupFunction = new DotNetFunction(this, $"{id}-action-group-function", new DotNetFunctionProps()
            {
                FunctionName = $"{id}-action-group-function",
                MemorySize = 512,
                Timeout = Duration.Seconds(30),
                Runtime = Runtime.DOTNET_8,
                Handler =
                    "ChatbotDemo.App::ChatbotDemo.App.Functions.ActionGroupFunction::Handler",
                LogRetention = RetentionDays.ONE_WEEK,
                ProjectDir = "./src/ChatbotDemo.App/",
                Architecture = Architecture.X86_64,
                Tracing = Tracing.ACTIVE,
                Environment = new Dictionary<string, string>
                {
                    { "CONNECTION_TABLE_NAME", props?.ConnectionTable.TableName ?? "" },
                }
            });

            var functionProperty = new CfnAgent.FunctionProperty
            {
                Name = $"{id}-action-group-function",
                Description = "Fat food details",
                Parameters = new Dictionary<string, object>
                {
                    {
                        "Limit",
                        new CfnAgent.ParameterDetailProperty
                        {
                            Type = "integer",
                            Description = "20",
                            Required = true
                        }
                    },
                    {
                        "Offset",
                        new CfnAgent.ParameterDetailProperty
                        {
                            Type = "integer",
                            Description = "0",
                            Required = true
                        }
                    },
                    {
                        "NutrientValue",
                        new CfnAgent.ParameterDetailProperty
                        {
                            Type = "integer",
                            Description = "20",
                            Required = true
                        }
                    }
                }
            };

            var actionGroup = new AgentActionGroup(this, $"{id}-action-group", new AgentActionGroupProps
            {
                ActionGroupName = $"{id}-action-group",
                Description = "Use these functions to get information about all food items",
                ActionGroupExecutor = new ActionGroupExecutor
                {
                    Lambda = actionGroupFunction
                },
                ActionGroupState = "ENABLED",
                FunctionSchema = new CfnAgent.FunctionSchemaProperty
                {
                    Functions = new[]
                    {
                        functionProperty
                    }
                }
            });

            bedrockAgent.AddActionGroup(actionGroup);
            bedrockAgent.AddAlias(new AddAgentAliasProps
            {
                AliasName = $"{id}-alias",
                Description = "Alias for my agent"
            });

            _ = new CfnOutput(this, "AgentId", new CfnOutputProps
            {
                Value = bedrockAgent.AgentId,
                Description = "Agent Id"
            });
            _ = new CfnOutput(this, "ActionGroupName", new CfnOutputProps
            {
                Value = actionGroup.ActionGroupName,
                Description = "ActionGroup Name"
            });
            _ = new CfnOutput(this, "KnowledgeBaseId", new CfnOutputProps
            {
                Value = knowledgeBase.KnowledgeBaseId,
                Description = "KnowledgeBase Id"
            });
            _ = new CfnOutput(this, "DataSourceId", new CfnOutputProps
            {
                Value = dataSource.DataSourceId,
                Description = "DataSource Id"
            });
            _ = new CfnOutput(this, "DocumentBucket", new CfnOutputProps
            {
                Value = docBucket.BucketName,
                Description = "Document Bucket"
            });
        }
    }
}