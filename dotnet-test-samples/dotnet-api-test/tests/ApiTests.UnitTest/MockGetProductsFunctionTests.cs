using System.Text.Json;
using Amazon.Lambda.TestUtilities;
using Amazon.XRay.Recorder.Core;
using FluentAssertions;
using GetProducts;
using Microsoft.Extensions.Logging;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockGetProductsFunctionTests
{
    private bool _runningLocally = string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("LOCAL_RUN")) ? true : bool.Parse(System.Environment.GetEnvironmentVariable("LOCAL_RUN"));
    private Mock<ILogger<Function>> _mockLogger = new Mock<ILogger<Function>>();

    public MockGetProductsFunctionTests()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();    
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }
    
    [Fact]
    public async Task GetProducts_ShouldReturnSuccess()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("GET")
            .Build();
        
        var mockDataAccessLayer = new Mock<ProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetAllProducts()).ReturnsAsync(new ProductWrapper());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ProductWrapper>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody.Products.Count.Should().Be(0);
    }
    
    [Fact]
    public async Task GetProducts__WhenDataAccessReturnsProducts_ShouldReturnInBody()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("GET")
            .Build();
        
        var mockDataAccessLayer = new Mock<ProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetAllProducts()).ReturnsAsync(new ProductWrapper(new List<ProductDTO>(1)
        {
            new ProductDTO("testid", "test product", 10)
        }));
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(200);

        var responseBody = JsonSerializer.Deserialize<ProductWrapper>(result.Body);

        responseBody.Should().NotBeNull();
        responseBody.Products.Count.Should().Be(1);
        responseBody.Products[0].Name.Should().Be("test product");
        responseBody.Products[0].Id.Should().Be("testid");
        responseBody.Products[0].Price.Should().Be(10);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_ForNonGetRequests_ShouldReturn405(string httpMethod)
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod(httpMethod)
            .Build();
        
        var mockDataAccessLayer = new Mock<ProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetAllProducts()).ReturnsAsync(new ProductWrapper());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task GetProducts_ErrorInDataAccess_ShouldReturn500()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("GET")
            .Build();
        
        var mockDataAccessLayer = new Mock<ProductsDAO>();
        mockDataAccessLayer.Setup(p => p.GetAllProducts())
            .ThrowsAsync(new NullReferenceException());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(500);
    }
}