namespace ServerlessTestSamples.UnitTest.Models;

public record ListStorageAreaResponseBody
{
    public IEnumerable<string> StorageAreas { get; set; } = Enumerable.Empty<string>();
}