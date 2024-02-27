using Newtonsoft.Json.Schema;

namespace SchemaTesting.UnitTest;

public interface ISchemaReader
{
    Task<JSchema> ReadJsonSchemaAsync(string schemaVersion);
}