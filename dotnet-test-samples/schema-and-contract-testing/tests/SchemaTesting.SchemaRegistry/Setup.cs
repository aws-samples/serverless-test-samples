namespace SchemaTesting.SchemaRegistry;

using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;

public class Setup : IAsyncLifetime
{
    public ISchemaReader SchemaReader { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "schema-testing";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "eu-west-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response = await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var outputs = response.Stacks[0].Outputs;

        SchemaReader = new EventBridgeSchemaRegistryReader();
    }

    public Task DisposeAsync()
    {
        return Task.CompletedTask;
    }

    private static string GetOutputVariable(List<Output> outputs, string name) =>
        outputs.FirstOrDefault(o => o.OutputKey == name)?.OutputValue
        ?? throw new Exception($"CloudFormation stack does not have an output variable named '{name}'");
}