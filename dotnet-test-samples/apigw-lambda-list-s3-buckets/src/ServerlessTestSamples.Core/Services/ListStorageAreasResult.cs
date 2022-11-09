namespace ServerlessTestSamples.Core.Services;

public record ListStorageAreasResult(IEnumerable<string> StorageAreas, bool IsSuccess = true, string Message = "");