using Amazon.CDK;
using ChatbotDemo.Infrastructure.Models;
using ChatbotDemo.Infrastructure.Stacks;

namespace ChatbotDemo.Infrastructure
{
    public sealed class Program
    {
        public static void Main(string[] args)
        {
            var app = new App();

            var websocketStack = new WebSocketStack(app, "WebSocketStack");
            _ = new BedrockAgentStack(app, "BedrockAgentStack", new MultiStackProps
            {
                ConnectionTable = websocketStack.ConnectionTable,
                WebSocketCallbackUrl = websocketStack.WebSocketCallbackUrl
            });
            _ = new BedrockGuardrailStack(app, "BedrockGuardrailStack");

            app.Synth();
        }
    }
}