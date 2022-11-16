using System.Net;
using System.Text.Json;
using Amazon;
using Amazon.Lambda;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Amazon.Lambda.Model;
using Amazon.Lambda.TestUtilities;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.XRay.Recorder.Core;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Core.Services;
using ServerlessTestSamples.Integrations;
using ServerlessTestSamples.UnitTest.Models;

namespace ServerlessTestSamples.UnitTest;

public class MockSdkTests
{
    private bool _runningLocally = string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("LOCAL_RUN")) ? true : bool.Parse(System.Environment.GetEnvironmentVariable("LOCAL_RUN"));
    private Mock<ILogger<Function>> _mockLogger = new Mock<ILogger<Function>>();
    private Mock<ILogger<ListStorageAreasQueryHandler>> _mockHandlerLogger = new Mock<ILogger<ListStorageAreasQueryHandler>>();

    public MockSdkTests()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();    
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }
    
    [Fact]
    public async Task TestLambdaHandlerWithValidS3Response_ShouldReturnSuccess()
    {
        var mockedS3Client = new Mock<IAmazonS3>();
        var mockHttpClient = new Mock<HttpClient>();
        
        mockedS3Client.Setup(p => p.ListBucketsAsync(It.IsAny<CancellationToken>())).ReturnsAsync(new ListBucketsResponse()
        {
            Buckets = new List<S3Bucket>()
            {
                new S3Bucket(){BucketName = "bucket1"},
                new S3Bucket(){BucketName = "bucket2"},
                new S3Bucket(){BucketName = "bucket3"},
            },
            HttpStatusCode = HttpStatusCode.OK
        });
        
        var storageService = new S3StorageService(mockedS3Client.Object);
        var handler = new ListStorageAreasQueryHandler(storageService, _mockHandlerLogger.Object);

        var function = new Function(handler, _mockLogger.Object);

        var result = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody?.StorageAreas.Count().Should().Be(3);
        responseBody?.StorageAreas.FirstOrDefault().Should().Be("bucket1");
    }

    [Fact]
    public async Task TestLambdaHandlerWithEmptyS3Response_ShouldReturnEmpty()
    {
        var mockedS3Client = new Mock<IAmazonS3>();
        var mockHttpClient = new Mock<HttpClient>();
        mockedS3Client.Setup(p => p.ListBucketsAsync(It.IsAny<CancellationToken>())).ReturnsAsync(new ListBucketsResponse()
        {
            Buckets = new List<S3Bucket>()
            {
            },
            HttpStatusCode = HttpStatusCode.OK
        });
        
        var storageService = new S3StorageService(mockedS3Client.Object);
        var handler = new ListStorageAreasQueryHandler(storageService, _mockHandlerLogger.Object);

        var function = new Function(handler, _mockLogger.Object);

        var result = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody?.StorageAreas.Count().Should().Be(0);
    }

    [Fact]
    public async Task TestLambdaHandlerWithS3NullResponse_ShouldReturnEmpty()
    {
        var mockedS3Client = new Mock<IAmazonS3>();
        var mockHttpClient = new Mock<HttpClient>();
        
        mockedS3Client.Setup(p => p.ListBucketsAsync(It.IsAny<CancellationToken>())).ReturnsAsync(new ListBucketsResponse()
        {
            Buckets = null,
            HttpStatusCode = HttpStatusCode.BadRequest
        });
        
        var storageService = new S3StorageService(mockedS3Client.Object);
        var handler = new ListStorageAreasQueryHandler(storageService, _mockHandlerLogger.Object);

        var function = new Function(handler, _mockLogger.Object);

        var result = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody?.StorageAreas.Count().Should().Be(0);
    }

    [Fact]
    public async Task TestLambdaHandlerWithS3Exception_ShouldReturnEmpty()
    {
        var mockedS3Client = new Mock<IAmazonS3>();
        var mockHttpClient = new Mock<HttpClient>();
        
        mockedS3Client.Setup(p => p.ListBucketsAsync(It.IsAny<CancellationToken>()))
            .ThrowsAsync(new AmazonS3Exception("Mock S3 failure"));
        
        var storageService = new S3StorageService(mockedS3Client.Object);
        var handler = new ListStorageAreasQueryHandler(storageService, _mockHandlerLogger.Object);

        var function = new Function(handler, _mockLogger.Object);

        var result = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody?.StorageAreas.Count().Should().Be(0);
    }
}