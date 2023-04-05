using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.SQS;
using Amazon.SQS.Model;
using Xunit;

namespace SqsEventHandler.IntegrationTests;

public class Setup : IAsyncLifetime
{
    public string? SqsEventQueueUrl;

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "sqs-lambda";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient =
            new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response =
            await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var outputs = response.Stacks[0].Outputs;

        SqsEventQueueUrl = GetOutputVariable(outputs, "SQSEventQueueUrl");
    }

    public Task DisposeAsync()
    {
        return Task.CompletedTask;
    }

    public async Task<SendMessageResponse> SendMessage(IAmazonSQS sqsClient, string? qUrl, string? messageBody)
    {
        return await sqsClient.SendMessageAsync(qUrl, messageBody);
    }

    private static string GetOutputVariable(IEnumerable<Output> outputs, string name) =>
        outputs.FirstOrDefault(o => o.OutputKey == name)?.OutputValue
        ?? throw new Exception($"CloudFormation stack does not have an output variable named '{name}'");
}