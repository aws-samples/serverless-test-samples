using System.Diagnostics;
using Amazon.DynamoDBv2;

namespace GetStock.IntegrationTest.Fixtures
{
    public class LocalDynamoDbFixture : IDisposable
    {
        private const string DockerExec = "docker";
        private const string ImageName = "dynamoDbLocal_test";

        private const int ExtenralPort = 8000;
        private Process? _process;
        public AmazonDynamoDBClient Client { get; }

        public LocalDynamoDbFixture()
        {
            _process = Process.Start($"{DockerExec}", $"run --name {ImageName} -p {ExtenralPort}:8000 amazon/dynamodb-local");

            var clientConfig = new AmazonDynamoDBConfig
            {
                ServiceURL = $"http://localhost:{ExtenralPort}"
            };

            Client = new AmazonDynamoDBClient(clientConfig);
        }

        public void Dispose()
        {
            _process?.Dispose();
            _process = null;

            var processStop = Process.Start($"{DockerExec}", $"stop {ImageName}");
            processStop?.WaitForExit();
            var processRm = Process.Start($"{DockerExec}", $"rm {ImageName}");
            processRm?.WaitForExit();
        }
    }
}

