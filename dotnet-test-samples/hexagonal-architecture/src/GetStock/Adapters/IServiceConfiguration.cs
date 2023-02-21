namespace GetStock.Adapters
{
    public interface IServiceConfiguration
    {
        string CurrencyBaseAddress { get; }
        string DynamoDbTableName { get; }
        string CurrencyApiKey { get; }
    }
}