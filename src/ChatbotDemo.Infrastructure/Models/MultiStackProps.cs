using Amazon.CDK;
using Amazon.CDK.AWS.DynamoDB;

namespace ChatbotDemo.Infrastructure.Models;

public class MultiStackProps : StackProps
{
    public Table ConnectionTable { get; set; }
    public string WebSocketCallbackUrl { get; set; }
}