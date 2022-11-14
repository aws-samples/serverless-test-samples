using ServerlessTestSamples.Core.Services;
using Microsoft.Extensions.Logging;

namespace ServerlessTestSamples.Core.Queries;

public class ListStorageAreasQuery
{
    public string? FilterPrefix { get; set; }
}

public class ListStorageAreasQueryResult
{
    public ListStorageAreasQueryResult(IEnumerable<string> storageAreas)
    {
        this.StorageAreas = storageAreas;
    }
    
    public IEnumerable<string> StorageAreas { get; set; }
}

public class ListStorageAreasQueryHandler
{
    private readonly IStorageService _storageService;
    private readonly ILogger<ListStorageAreasQueryHandler> _logger;
    
    public ListStorageAreasQueryHandler(IStorageService storageService, ILogger<ListStorageAreasQueryHandler> logger)
    {
        _storageService = storageService;
        _logger = logger;
    }

    public async Task<ListStorageAreasQueryResult> Handle(ListStorageAreasQuery query)
    {
        try
        {
            var storageAreas = await _storageService.ListStorageAreas(query.FilterPrefix);

            if (!storageAreas.IsSuccess)
            {
                this._logger.LogWarning(storageAreas.Message);
            }

            return new ListStorageAreasQueryResult(storageAreas.StorageAreas);
        }
        catch (Exception ex)
        {
            this._logger.LogError(ex, "Failure querying storage areas");
            
            return new ListStorageAreasQueryResult(new List<string>(0));
        }
    }
}