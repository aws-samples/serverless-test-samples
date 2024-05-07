namespace AsyncTesting.IntegrationTest;

using System.Text;

using Amazon.DynamoDBv2.Model;
using Amazon.S3.Model;

using FluentAssertions;

using Xunit.Abstractions;

public class TextTransformerE2ETest : IClassFixture<Setup>
{
    private const int MAX_POLL_ATTEMPTS = 10;
    private const int POLL_INTERVAL = 2;
    
    private readonly Setup setup;
    private readonly ITestOutputHelper outputHelper;

    public TextTransformerE2ETest(Setup setup, ITestOutputHelper outputHelper)
    {
        this.setup = setup;
        this.outputHelper = outputHelper;
    }

    [Fact]
    public async Task PutObjectToS3_With_ValidData_Should_TriggerAsyncProcess()
    {
        // Arrange
        var testFileName = $"{Guid.NewGuid()}.txt";
        
        // Act
        var testString = "hello world";

        await this.PutObjectIntoSourceBucket(
            testString,
            this.setup.SourceBucketName,
            testFileName);

        // Assert
        var result = await this.PollForProcessedMessage(testFileName);

        if (string.IsNullOrEmpty(result))
        {
            throw new Exception("Message not found");
        }

        result.Should().Be(testString.ToUpper());
    }

    [Fact]
    public async Task PutObjectToS3_With_InvalidFileFormat_Should_NotTriggerAsyncProcess()
    {
        // Arrange
        var testFileName = $"{Guid.NewGuid()}.csv";
        
        // Act
        var testString = "hello world";
        
        await this.PutObjectIntoSourceBucket(
            testString,
            this.setup.SourceBucketName,
            testFileName);

        // Assert
        var result = await this.PollForProcessedMessage(testFileName);

        result.Should().BeNull();
    }

    private async Task PutObjectIntoSourceBucket(
        string message,
        string sourceBucketName,
        string testFilename)
    {
        var inputBytes = Encoding.ASCII.GetBytes(message);

        await this.setup.S3Client.PutObjectAsync(
            new PutObjectRequest()
            {
                BucketName = sourceBucketName,
                InputStream = new MemoryStream(inputBytes),
                Key = testFilename
            });
        
        this.setup.CreatedFiles.Add(testFilename);
    }

    private async Task<string> PollForProcessedMessage(string testFilename)
    {
        var pollAttempts = 0;

        while (pollAttempts < MAX_POLL_ATTEMPTS)
        {
            this.outputHelper.WriteLine($"Poll attempt {pollAttempts}");
            
            var result = await this.setup.DynamoDbClient.GetItemAsync(
                this.setup.DestinationTableName,
                new Dictionary<string, AttributeValue>(1)
                {
                    { "id", new AttributeValue(testFilename) }
                });

            if (result.IsItemSet)
            {
                this.outputHelper.WriteLine($"Message found after {pollAttempts} attempt(s), returning");
                
                return result.Item["message"].S;
            }

            pollAttempts++;
            
            this.outputHelper.WriteLine($"Wait for {POLL_INTERVAL}");

            await Task.Delay(TimeSpan.FromSeconds(POLL_INTERVAL));
        }

        return null;
    }
}