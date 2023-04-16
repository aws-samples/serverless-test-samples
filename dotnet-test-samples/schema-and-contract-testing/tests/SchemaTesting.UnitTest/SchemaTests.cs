using Newtonsoft.Json.Schema;

namespace SchemaTesting.UnitTest;

public class SchemaTests
{
    private readonly ISchemaReader _schemaReader;

    public SchemaTests()
    {
        this._schemaReader = new LocalDiskSchemaReader();
    }
    
    [Fact]
    public async Task EventPayloadMatchesSchema_ShouldPass()
    {
        // Initial test to check success
        var sampleEventJson = await SampleEventReader.ParseRawJsonFromEventVersion("1.0.0");

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.0.0");

        var isValid = sampleEventJson.IsValid(schema);

        isValid.Should().BeTrue();
    }
    
    [Fact]
    public async Task AdditionalOptionalPropertiesAdded_ShouldPass()
    {
        // Schema version 1.1.0 adds an additional email property
        var sampleEventJson = await SampleEventReader.ParseRawJsonFromEventVersion("1.1.0");

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.0.0");

        var isValid = sampleEventJson.IsValid(schema);

        isValid.Should().BeTrue();
    }
    
    [Fact]
    public async Task RemoveElementsFromPayload_ShouldFail()
    {
        // Schema version 1.2.0 removes the address property
        var sampleEventJson = await SampleEventReader.ParseRawJsonFromEventVersion("1.2.0");

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.0.0");

        var isValid = sampleEventJson.IsValid(schema);

        isValid.Should().BeFalse();
    }
}