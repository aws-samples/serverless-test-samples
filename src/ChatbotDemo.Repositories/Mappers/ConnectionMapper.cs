using Amazon.DynamoDBv2.Model;
using ChatbotDemo.Repositories.Models;

namespace ChatbotDemo.Repositories.Mappers;

public static class ConnectionMapper
{
    public const string ConnectionId = "connection_id";

    public static ConnectionDto ConnectionFromDynamoDb(Dictionary<string, AttributeValue> items) =>
        new(items[ConnectionId].S);

    public static Dictionary<string, AttributeValue> ConnectionToDynamoDb(ConnectionDto connection) =>
        new(capacity: 1)
        {
            [ConnectionId] = new AttributeValue(connection.ConnectionId)
        };
}