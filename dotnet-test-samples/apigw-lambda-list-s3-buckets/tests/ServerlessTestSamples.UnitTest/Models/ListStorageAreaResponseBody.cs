namespace ServerlessTestSamples.UnitTest.Models;

public record ListStorageAreaResponseBody
{
    public ListStorageAreaResponseBody()
    {
        StorageAreas = Enumerable.Empty<string>();
    }
    
    public IEnumerable<string> StorageAreas { get; set; }
}