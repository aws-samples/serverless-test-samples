namespace GetStock.Adapters
{
    internal class ServiceEnvironmentConfiguration : IServiceConfiguration
    {
        public string DynamoDbTableName => Environment.GetEnvironmentVariable("DB_TABLE");
        public string CurrencyBaseAddress => Environment.GetEnvironmentVariable("BASE_API");
        public string CurrencyApiKey => Environment.GetEnvironmentVariable("API_KEY");
    }
}
