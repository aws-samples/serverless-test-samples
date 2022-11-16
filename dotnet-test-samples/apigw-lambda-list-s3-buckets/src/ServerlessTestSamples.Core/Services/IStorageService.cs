namespace ServerlessTestSamples.Core.Services;

public interface IStorageService
{
    Task<ListStorageAreasResult> ListStorageAreas(string? filterPrefix);
}