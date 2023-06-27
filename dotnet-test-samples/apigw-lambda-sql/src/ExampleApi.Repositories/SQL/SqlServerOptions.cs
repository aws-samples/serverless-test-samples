using Microsoft.Extensions.Configuration;

namespace ExampleApi.Repositories.Sql;

public class SqlServerOptions
{
    [ConfigurationKeyName("SQL_CONNECTION_STRING_SECRET_NAME")]
    public string SqlConnectionStringSecretName { get; set; } = string.Empty;
}