using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;

namespace ServerlessTestSamples.IntegrationTest;

public class Setup : IAsyncLifetime
{
    public string ApiUrl { get; private set; } = default!;

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "dotnet-intro-test-samples";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response = await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var output = response.Stacks[0].Outputs.FirstOrDefault(p => p.OutputKey == "ApiEndpoint");

        ApiUrl = output?.OutputValue ?? string.Empty;
    }

    public Task DisposeAsync() => Task.CompletedTask;
}