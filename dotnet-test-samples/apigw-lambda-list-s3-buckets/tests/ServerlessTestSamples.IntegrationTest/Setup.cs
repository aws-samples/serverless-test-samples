using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;

namespace ServerlessTestSamples.IntegrationTest;

public class Setup : IDisposable
{
    public static string ApiUrl { get; set; }

    public Setup()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "dotnet-intro-test-samples";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";

        if (string.IsNullOrEmpty(stackName))
        {
            throw new Exception("Cannot find env var AWS_SAM_STACK_NAME. Please setup this environment variable with the stack name where we are running integration tests.");
        }

        var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig()
        {
            RegionEndpoint = RegionEndpoint.GetBySystemName(region)
        });

        var response = cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest()
        {
            StackName = stackName
        }).Result;

        var output = response.Stacks[0].Outputs.FirstOrDefault(p => p.OutputKey == "ApiEndpoint");

        ApiUrl = output.OutputValue;
    }

    public void Dispose()
    {
        // Do "global" teardown here; Only called once.
    }
}