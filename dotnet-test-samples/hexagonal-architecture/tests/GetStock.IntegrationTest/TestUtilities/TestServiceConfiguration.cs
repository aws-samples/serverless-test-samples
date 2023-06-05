using GetStock.Adapters;

namespace GetStock.IntegrationTest.TestUtilities;

public class TestServiceConfiguration : IServiceConfiguration
{
    public string CurrencyBaseAddress { get; set; } = "http://dummy.url";

    public string DynamoDbTableName { get; set; } = "test-currencies";

    public string CurrencyApiKey { get; set; } = "api-key";
}