using Microsoft.Extensions.Options;

namespace ServerlessTestApi.Infrastructure;

public class DynamoDbOptionsValidator : IValidateOptions<DynamoDbOptions>
{
    public ValidateOptionsResult Validate(string? name, DynamoDbOptions options)
    {
        if (name == Options.DefaultName)
        {
            if (string.IsNullOrEmpty(options.ProductTableName))
            {
                ValidateOptionsResult.Fail("The PRODUCT_TABLE_NAME setting has not been configured");
            }

            return ValidateOptionsResult.Success;
        }

        return ValidateOptionsResult.Skip;
    }
}
