using System.Text.Json;
using Amazon.Lambda.TestUtilities;
using Amazon.XRay.Recorder.Core;
using FluentAssertions;
using PutProduct;
using Microsoft.Extensions.Logging;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockPutProductFunctionTests
{
    private bool _runningLocally = string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("LOCAL_RUN")) ? true : bool.Parse(System.Environment.GetEnvironmentVariable("LOCAL_RUN"));
    private Mock<ILogger<Function>> _mockLogger = new Mock<ILogger<Function>>();

    public MockPutProductFunctionTests()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();    
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }
    
    [Fact]
    public async Task PutProduct_WithValidBody_ShouldReturnSuccess()
    {
        var testProduct = new ProductDTO("testid", "test product", 10);
        
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("PUT")
            .WithBody(testProduct)
            .WithPathParameter("id", testProduct.Id)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.PutProduct(It.IsAny<Product>())).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(201);
        mockDataAccessLayer.Verify(p => p.PutProduct(It.IsAny<Product>()), Times.Once);
    }
    
    [Fact]
    public async Task PutProduct_WithEmptyBody_ShouldReturnBadRequest()
    {
        var testProduct = new ProductDTO("testid", "test product", 10);
        
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("PUT")
            .WithPathParameter("id", testProduct.Id)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.PutProduct(It.IsAny<Product>())).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(400);
        mockDataAccessLayer.Verify(p => p.PutProduct(It.IsAny<Product>()), Times.Never);
    }
        
    [Fact]
    public async Task PutProduct_WithMismatchingIds_ShouldReturnBadRequest()
    {
        var testProduct = new ProductDTO("testid", "test product", 10);
        
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("PUT")
            .WithPathParameter("id", "adifferentid")
            .WithBody(testProduct)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.PutProduct(It.IsAny<Product>())).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(400);
        result.Body.Should().Be("Product ID in the body does not match path parameter");
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("GET")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_ForNonPutRequests_ShouldReturn405(string httpMethod)
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod(httpMethod)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.PutProduct(It.IsAny<Product>())).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task PutProduct_ErrorInDataAccess_ShouldReturn500()
    {
        var testProduct = new ProductDTO("testid", "test product", 10);
        
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("PUT")
            .WithPathParameter("id", testProduct.Id)
            .WithBody(testProduct)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.PutProduct(It.IsAny<Product>()))
            .ThrowsAsync(new NullReferenceException());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(500);
    }
}