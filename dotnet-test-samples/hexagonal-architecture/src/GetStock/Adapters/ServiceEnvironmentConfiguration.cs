namespace GetStock.Adapters;

internal class ServiceEnvironmentConfiguration : IServiceConfiguration
{
    public string DynamoDbTableName => Environment.GetEnvironmentVariable("DB_TABLE") ?? string.Empty;
    public string CurrencyBaseAddress => Environment.GetEnvironmentVariable("BASE_API") ?? string.Empty;
    public string CurrencyApiKey => Environment.GetEnvironmentVariable("API_KEY") ?? string.Empty;
}