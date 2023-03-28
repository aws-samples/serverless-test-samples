namespace ServerlessTestSamples.Core.Queries;

public class ListStorageAreasQueryResult
{
    public ListStorageAreasQueryResult(IEnumerable<string> storageAreas) => StorageAreas = storageAreas;

    public IEnumerable<string> StorageAreas { get; }
}
