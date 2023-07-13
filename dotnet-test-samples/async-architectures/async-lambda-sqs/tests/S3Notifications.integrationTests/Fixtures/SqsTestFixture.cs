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
        
        public async Task<Message> GetNextMessage()
        {
            var receiveMessageRequest = new ReceiveMessageRequest
            {
                QueueUrl = QueueUrl,
                MaxNumberOfMessages = 1
            };

            int count = 0;
            ReceiveMessageResponse? receiveMessageResponse = null;
            do
            {
                await Task.Delay(1000);
                receiveMessageResponse = await SqsClient.ReceiveMessageAsync(receiveMessageRequest);
                if (receiveMessageResponse.Messages.Count != 0)
                {
                    break;
                }
            } while (count++ < 60);

            Assert.NotNull(receiveMessageResponse);
            Assert.NotEmpty(receiveMessageResponse.Messages);
            
            var message = receiveMessageResponse.Messages[0];
            await SqsClient.DeleteMessageAsync(QueueUrl, message.ReceiptHandle);
            
            return message;
        }

    }
}
