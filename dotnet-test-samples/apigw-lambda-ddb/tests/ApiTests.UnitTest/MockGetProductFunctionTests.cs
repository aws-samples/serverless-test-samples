using System.Text.Json;
using Amazon.Lambda.TestUtilities;
using Amazon.XRay.Recorder.Core;
using FluentAssertions;
using GetProduct;
using Microsoft.Extensions.Logging;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockGetProductFunctionTests
{
    private bool _runningLocally = string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("LOCAL_RUN")) ? true : bool.Parse(System.Environment.GetEnvironmentVariable("LOCAL_RUN"));
    private Mock<ILogger<Function>> _mockLogger = new Mock<ILogger<Function>>();

    public MockGetProductFunctionTests()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();    
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }
    
    [Fact]
    public async Task GetProduct_ShouldReturnSuccess()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod("GET")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>())).ReturnsAsync(new ProductDTO("testid", "test product", 10));
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ProductDTO>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody.Id.Should().Be("testid");
        responseBody.Name.Should().Be("test product");
        responseBody.Price.Should().Be(10);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_ForNonGetRequests_ShouldReturn405(string httpMethod)
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(httpMethod)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetAllProducts()).ReturnsAsync(new ProductWrapper());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task GetProduct_ErrorInDataAccess_ShouldReturn500()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod("GET")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>()))
            .ThrowsAsync(new NullReferenceException());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(500);
    }
    
    [Fact]
    public async Task GetProduct_ProductNotFound_ShouldReturn400()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("GET")
            .WithPathParameter("id", "123456")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>()))
            .ReturnsAsync(() => null);
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(400);
    }
}