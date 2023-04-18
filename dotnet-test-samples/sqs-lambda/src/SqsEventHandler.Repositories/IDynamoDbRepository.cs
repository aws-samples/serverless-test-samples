using SqsEventHandler.Repositories.Mappers;

namespace SqsEventHandler.Repositories;

public interface IDynamoDbRepository<TItem> where TItem : class
{
    Task<TItem?> GetItemAsync(string id, CancellationToken cancellationToken);

    Task<UpsertResult> PutItemAsync(TItem dto, CancellationToken cancellationToken);

    Task<bool> DeleteItemAsync(string id, CancellationToken cancellationToken);
}