namespace SchemaTesting.SchemaRegistry;

using Newtonsoft.Json.Schema;

public interface ISchemaReader
{
    Task<JSchema> ReadJsonSchemaAsync(string schemaName, string schemaVersion);
}