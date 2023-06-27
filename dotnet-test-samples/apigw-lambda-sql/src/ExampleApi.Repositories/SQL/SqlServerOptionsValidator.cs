using Microsoft.Extensions.Options;

namespace ExampleApi.Repositories.Sql;

public class SqlServerOptionsValidator : IValidateOptions<SqlServerOptions>
{
    public ValidateOptionsResult Validate(string? name, SqlServerOptions options)
    {
        if (name != Options.DefaultName) return ValidateOptionsResult.Skip;

        if (string.IsNullOrEmpty(options.SqlConnectionStringSecretName))
        {
            ValidateOptionsResult.Fail("The SQL_CONNECTION_STRING_SECRET_NAME setting has not been configured");
        }

        return ValidateOptionsResult.Success;
    }
}