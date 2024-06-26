using ChatbotDemo.Repositories.Mappers;

namespace ChatbotDemo.Repositories;

public interface IDynamoDbRepository<TItem> where TItem : class
{
    Task<TItem> GetItemAsync(IDictionary<string, string> input, CancellationToken cancellationToken);
    Task<IEnumerable<TItem>> GetItemsAsync(IDictionary<string, string> input, CancellationToken cancellationToken);
    Task<UpsertResult> PutItemAsync(TItem dto, CancellationToken cancellationToken);
    Task<bool> DeleteItemAsync(IDictionary<string, string> input, CancellationToken cancellationToken);
}