namespace ServerlessTestSamples.IntegrationTest.Drivers;

public record ListStorageAreasResult(IEnumerable<string> StorageAreas, bool IsSuccess = true, string Message = "");