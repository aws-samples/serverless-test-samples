namespace SchemaTesting.SchemaRegistry;

using Amazon.Schemas;
using Amazon.Schemas.Model;

using Newtonsoft.Json.Schema;

public class EventBridgeSchemaRegistryReader : ISchemaReader
{
    private readonly AmazonSchemasClient _schemasClient;
    
    public EventBridgeSchemaRegistryReader()
    {
        this._schemasClient = new AmazonSchemasClient();
    }
    
    public async Task<JSchema> ReadJsonSchemaAsync(string schemaName, string schemaVersion)
    {
        var schemaData = await this._schemasClient.ExportSchemaAsync(new ExportSchemaRequest()
        {
            RegistryName = "discovered-schemas",
            SchemaName = $"com.dev.customer@{schemaName}",
            SchemaVersion = schemaVersion,
            Type = "JSONSchemaDraft4"
        });

        var schema = JSchema.Parse(schemaData.Content);

        return schema;
    }
}