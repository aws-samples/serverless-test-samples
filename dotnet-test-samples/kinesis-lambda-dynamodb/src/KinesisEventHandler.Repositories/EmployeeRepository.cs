using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using KinesisEventHandler.Repositories.Mappers;
using KinesisEventHandler.Repositories.Models;
using Microsoft.Extensions.Options;

namespace KinesisEventHandler.Repositories;

public class EmployeeRepository : IDynamoDbRepository<EmployeeDto>
{
    private readonly IAmazonDynamoDB _dynamoDbClient;
    private readonly IOptions<DynamoDbOptions> _options;

    public EmployeeRepository(IAmazonDynamoDB dynamoDbClient, IOptions<DynamoDbOptions> options)
    {
        _dynamoDbClient = dynamoDbClient;
        _options = options;
    }

    public async Task<EmployeeDto?> GetItemAsync(string id, CancellationToken cancellationToken)
    {
        var response = await _dynamoDbClient.GetItemAsync(
            _options.Value.EmployeeStreamTableName,
            new Dictionary<string, AttributeValue>(capacity: 1) { [EmployeeMapper.EmployeeId] = new(id) },
            cancellationToken);

        return response.IsItemSet
            ? EmployeeMapper.EmployeeFromDynamoDb(response.Item)
            : null;
    }

    public async Task<UpsertResult> PutItemAsync(EmployeeDto dto, CancellationToken cancellationToken)
    {
        var request = new PutItemRequest()
        {
            TableName = _options.Value.EmployeeStreamTableName,
            Item = EmployeeMapper.EmployeeToDynamoDb(dto),
            ReturnValues = ReturnValue.ALL_OLD,
        };
        var response = await _dynamoDbClient.PutItemAsync(request, cancellationToken);
        var hadOldValues = response.Attributes is not null && response.Attributes.Count > 0;

        return hadOldValues ? UpsertResult.Updated : UpsertResult.Inserted;
    }

    public async Task<bool> DeleteItemAsync(string id, CancellationToken cancellationToken)
    {
        var response = await _dynamoDbClient.DeleteItemAsync(
            _options.Value.EmployeeStreamTableName,
            new Dictionary<string, AttributeValue>(capacity: 1) { [EmployeeMapper.EmployeeId] = new(id) },
            cancellationToken);

        return response.HttpStatusCode == System.Net.HttpStatusCode.OK;
    }
}