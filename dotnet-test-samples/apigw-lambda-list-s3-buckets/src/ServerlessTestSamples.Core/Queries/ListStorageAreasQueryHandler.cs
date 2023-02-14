using ServerlessTestSamples.Core.Services;
using Microsoft.Extensions.Logging;

namespace ServerlessTestSamples.Core.Queries;

public class ListStorageAreasQueryHandler
{
    private readonly IStorageService _storageService;
    private readonly ILogger<ListStorageAreasQueryHandler> _logger;

    public ListStorageAreasQueryHandler(
        IStorageService storageService,
        ILogger<ListStorageAreasQueryHandler> logger)
    {
        _storageService = storageService;
        _logger = logger;
    }

    public async Task<ListStorageAreasQueryResult> Handle(ListStorageAreasQuery query, CancellationToken cancellationToken)
    {
        ListStorageAreasResult result;

        try
        {
            result = await _storageService.ListStorageAreas(query.FilterPrefix, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failure querying storage areas");
            return new(new List<string>(capacity: 0));
        }

        if (!result.IsSuccess)
        {
            _logger.LogWarning(result.Message);
        }

        return new(result.StorageAreas);
    }
}