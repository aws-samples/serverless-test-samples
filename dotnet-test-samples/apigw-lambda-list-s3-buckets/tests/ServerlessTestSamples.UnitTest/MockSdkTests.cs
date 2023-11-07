using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.TestUtilities;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.XRay.Recorder.Core;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Integrations;
using ServerlessTestSamples.UnitTest.Models;
using System.Net;
using System.Text.Json;
using FakeItEasy;

namespace ServerlessTestSamples.UnitTest;

public class MockSdkTests
{
    public MockSdkTests()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }
    
    private ILogger<Function> Logger { get; } = A.Fake<ILogger<Function>>();

    private ILogger<ListStorageAreasQueryHandler> HandlerLogger { get; } = A.Fake<ILogger<ListStorageAreasQueryHandler>>();

    private IOptions<JsonSerializerOptions> JsonOptions { get; } =
        Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web));

    [Fact]
    public async Task TestLambdaHandler_With_ValidS3Response_Should_ReturnSuccess()
    {
        // arrange
        var fakeS3 = A.Fake<IAmazonS3>();

        A.CallTo(() => fakeS3.ListBucketsAsync(A<CancellationToken>._))
          .Returns(Task.FromResult(new ListBucketsResponse()
          {
              Buckets = new List<S3Bucket>
              {
                  new(){ BucketName = "bucket1" },
                  new(){ BucketName = "bucket2" },
                  new(){ BucketName = "bucket3" },
              },
              HttpStatusCode = HttpStatusCode.OK,
          }));

        var storageService = new S3StorageService(fakeS3);
        var handler = new ListStorageAreasQueryHandler(storageService, HandlerLogger);
        var function = new Function(handler, Logger, JsonOptions);

        // act
        var response = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(
            new ListStorageAreaResponseBody()
            {
                StorageAreas = new[]
                {
                    "bucket1",
                    "bucket2",
                    "bucket3",
                },
            });
    }

    [Fact]
    public async Task TestLambdaHandler_With_EmptyS3Response_Should_ReturnEmpty()
    {
        // arrange
        var fakeS3 = A.Fake<IAmazonS3>();

        A.CallTo(() => fakeS3.ListBucketsAsync(A<CancellationToken>._))
          .Returns(Task.FromResult(new ListBucketsResponse
          {
              Buckets = new List<S3Bucket>(),
              HttpStatusCode = HttpStatusCode.OK,
          }));

        var storageService = new S3StorageService(fakeS3);
        var handler = new ListStorageAreasQueryHandler(storageService, HandlerLogger);
        var function = new Function(handler, Logger, JsonOptions);

        // act
        var response = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(new ListStorageAreaResponseBody());
    }

    [Fact]
    public async Task TestLambdaHandler_With_S3NullResponse_Should_ReturnEmpty()
    {
        // arrange
        var fakeS3 = A.Fake<IAmazonS3>();

        A.CallTo(() => fakeS3.ListBucketsAsync(A<CancellationToken>._))
          .Returns(Task.FromResult(new ListBucketsResponse
          {
              Buckets = null,
              HttpStatusCode = HttpStatusCode.BadRequest,
          }));

        var storageService = new S3StorageService(fakeS3);
        var handler = new ListStorageAreasQueryHandler(storageService, HandlerLogger);
        var function = new Function(handler, Logger, JsonOptions);

        // act
        var response = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(new ListStorageAreaResponseBody());
    }

    [Fact]
    public async Task TestLambdaHandler_With_S3Exception_Should_ReturnEmpty()
    {
        // arrange
        var fakeS3 = A.Fake<IAmazonS3>();

        A.CallTo(() => fakeS3.ListBucketsAsync(A<CancellationToken>._))
          .Throws(new AmazonS3Exception("Mock S3 failure"));

        var storageService = new S3StorageService(fakeS3);
        var handler = new ListStorageAreasQueryHandler(storageService, HandlerLogger);
        var function = new Function(handler, Logger, JsonOptions);

        // act
        var response = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(new ListStorageAreaResponseBody());
    }
}