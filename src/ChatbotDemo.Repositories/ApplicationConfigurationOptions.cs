using Microsoft.Extensions.Configuration;

namespace ChatbotDemo.Repositories;

public class ApplicationConfigurationOptions
{
    [ConfigurationKeyName("CONNECTION_TABLE_NAME")]
    public string ConnectionTableName { get; init; } = string.Empty;

    [ConfigurationKeyName("WEBSOCKET_CALLBACK_URL")]
    public string WebsocketCallbackUrl { get; init; } = string.Empty;
}