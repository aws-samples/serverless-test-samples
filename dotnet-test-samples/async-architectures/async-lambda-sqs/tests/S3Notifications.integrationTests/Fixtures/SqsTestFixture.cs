using Amazon;
using Amazon.SQS;
using Amazon.SQS.Model;

namespace S3Notifications.integrationTests.Fixtures
{
    public class SqsTestFixture : IDisposable
    {   
        internal IAmazonSQS SqsClient { get; }
        internal string QueueUrl { get; }

        private static readonly RegionEndpoint Region = RegionEndpoint.USEast1;
        private const string QueueNamePrefix = "test-s3-queue";

        public SqsTestFixture()
        {
            SqsClient = new AmazonSQSClient(Region);

            var queueName = $"{QueueNamePrefix}-{Guid.NewGuid()}";

            var createQueueResponse = SqsClient.CreateQueueAsync(queueName).Result;
            QueueUrl = createQueueResponse.QueueUrl;
        }

        public void Dispose()
        {
            SqsClient.DeleteQueueAsync(QueueUrl).Wait();
            SqsClient.Dispose();
        }
    }
}
