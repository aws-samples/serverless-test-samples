using System.Runtime.CompilerServices;
using Amazon.EventBridge;
using Amazon.Schemas;
using Amazon.Schemas.Model;
using Newtonsoft.Json.Schema;

namespace SchemaTesting.UnitTest;

public class EventBridgeSchemaRegistryReader : ISchemaReader
{
    private readonly AmazonSchemasClient _schemasClient;
    
    public EventBridgeSchemaRegistryReader()
    {
        this._schemasClient = new AmazonSchemasClient();
    }
    
    public async Task<JSchema> ReadJsonSchemaAsync(string schemaVersion)
    {
        var schemaData = await this._schemasClient.DescribeSchemaAsync(new DescribeSchemaRequest
        {
            RegistryName = "my-event-registry",
            SchemaName = "create-customer",
            SchemaVersion = schemaVersion
        });
        
        var schema = JSchema.Parse(schemaData.Content);

        return schema;
    }
}