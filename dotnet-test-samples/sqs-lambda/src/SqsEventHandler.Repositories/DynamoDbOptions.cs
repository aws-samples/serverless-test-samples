using Microsoft.Extensions.Configuration;

namespace SqsEventHandler.Repositories;

public class DynamoDbOptions
{
    [ConfigurationKeyName("EMPLOYEE_TABLE_NAME")]
    public string EmployeeTableName { get; set; } = string.Empty;
}