using Microsoft.Extensions.Options;

namespace ChatbotDemo.Repositories;

public class ApplicationConfigurationsValidator : IValidateOptions<ApplicationConfigurationOptions>
{
    public ValidateOptionsResult Validate(string? name, ApplicationConfigurationOptions options)
    {
        if (name != Options.DefaultName) return ValidateOptionsResult.Skip;
        
        if (string.IsNullOrEmpty(options.ConnectionTableName))
        {
            ValidateOptionsResult.Fail("Unable to load setting CONNECTION_TABLE_NAME");
        }
        
        if (string.IsNullOrEmpty(options.WebsocketCallbackUrl))
        {
            ValidateOptionsResult.Fail("Unable to load setting WEBSOCKET_CALLBACK_URL");
        }

        return ValidateOptionsResult.Success;
    }
}