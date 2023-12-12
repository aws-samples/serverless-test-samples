using Newtonsoft.Json.Schema;

namespace SchemaTesting.UnitTest;

public class LocalDiskSchemaReader : ISchemaReader 
{
    public async Task<JSchema> ReadJsonSchemaAsync(string schemaVersion)
    {
        var schemaData = await File.ReadAllTextAsync($"./schemas/json/customerCreated-v{schemaVersion}.json");
        
        var schema = JSchema.Parse(schemaData);

        return schema;
    }
}