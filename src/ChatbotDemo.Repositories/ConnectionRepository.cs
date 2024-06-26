using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using ChatbotDemo.Repositories.Mappers;
using ChatbotDemo.Repositories.Models;
using Microsoft.Extensions.Options;

namespace ChatbotDemo.Repositories;

public class ConnectionRepository(IAmazonDynamoDB dynamoDbClient, IOptions<ApplicationConfigurationOptions> options)
    : IDynamoDbRepository<ConnectionDto>
{
    public async Task<ConnectionDto> GetItemAsync(IDictionary<string, string> input,
        CancellationToken cancellationToken)
    {
        var response = await dynamoDbClient.GetItemAsync(
            options.Value.ConnectionTableName,
            new Dictionary<string, AttributeValue>(capacity: 1)
            {
                [ConnectionMapper.ConnectionId] = new
                    (input["connection_id"])
            },
            cancellationToken);

        return response.IsItemSet
            ? ConnectionMapper.ConnectionFromDynamoDb(response.Item)
            : throw new KeyNotFoundException($"Connection with id: {input["connection_id"]} not found.");
    }

    public Task<IEnumerable<ConnectionDto>> GetItemsAsync(IDictionary<string, string> input,
        CancellationToken cancellationToken)
    {
        throw new NotImplementedException();
    }

    public async Task<UpsertResult> PutItemAsync(ConnectionDto dto, CancellationToken cancellationToken)
    {
        var request = new PutItemRequest()
        {
            TableName = options.Value.ConnectionTableName,
            Item = ConnectionMapper.ConnectionToDynamoDb(dto),
            ReturnValues = ReturnValue.ALL_OLD,
        };
        var response = await dynamoDbClient.PutItemAsync(request, cancellationToken);
        var hadOldValues = response.Attributes is not null && response.Attributes.Count > 0;

        return hadOldValues ? UpsertResult.Updated : UpsertResult.Inserted;
    }

    public async Task<bool> DeleteItemAsync(IDictionary<string, string> input, CancellationToken cancellationToken)
    {
        var response = await dynamoDbClient.DeleteItemAsync(
            options.Value.ConnectionTableName,
            new Dictionary<string, AttributeValue>(capacity: 1)
                { [ConnectionMapper.ConnectionId] = new(input["connection_id"]) },
            cancellationToken);

        return response.HttpStatusCode == System.Net.HttpStatusCode.OK;
    }
}