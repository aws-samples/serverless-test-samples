using Microsoft.Extensions.Configuration;

namespace KinesisEventHandler.Repositories;

public class DynamoDbOptions
{
    [ConfigurationKeyName("EMPLOYEE_TABLE_NAME")]
    public string EmployeeStreamTableName { get; set; } = string.Empty;
}