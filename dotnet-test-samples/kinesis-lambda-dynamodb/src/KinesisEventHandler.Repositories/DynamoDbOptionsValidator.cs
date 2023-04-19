using Microsoft.Extensions.Options;

namespace KinesisEventHandler.Repositories;

public class DynamoDbOptionsValidator : IValidateOptions<DynamoDbOptions>
{
    public ValidateOptionsResult Validate(string? name, DynamoDbOptions options)
    {
        if (name != Options.DefaultName) return ValidateOptionsResult.Skip;
        
        if (string.IsNullOrEmpty(options.EmployeeStreamTableName))
        {
            ValidateOptionsResult.Fail("The EMPLOYEE_TABLE_NAME setting has not been configured");
        }

        return ValidateOptionsResult.Success;
    }
}