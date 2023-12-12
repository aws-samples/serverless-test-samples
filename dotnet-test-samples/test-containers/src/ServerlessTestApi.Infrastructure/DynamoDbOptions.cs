using Microsoft.Extensions.Configuration;

namespace ServerlessTestApi.Infrastructure;

public class DynamoDbOptions
{
    [ConfigurationKeyName("PRODUCT_TABLE_NAME")]
    public string ProductTableName { get; set; } = string.Empty;
}
