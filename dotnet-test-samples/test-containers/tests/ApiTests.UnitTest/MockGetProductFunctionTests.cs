using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using GetProduct;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using System.Text.Json;
using FakeItEasy;

namespace ApiTests.UnitTest;

using ProductAPI.Tests;

[Collection("APITests")]
public class MockGetProductFunctionTests : FunctionTest<Function>
{
    private readonly TestStartup _startup;

    public MockGetProductFunctionTests(TestStartup startup)
    {
        this._startup = startup;
    }

    [Fact]
    public async Task GetProduct_Should_ReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", this._startup.TestProduct.Id)
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var expected = new ProductDTO(this._startup.TestProduct.Id, this._startup.TestProduct.Name, this._startup.TestProduct.Price);

        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ProductDTO>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(expected);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_WithNonGetRequests_Should_Return405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", this._startup.TestProduct.Id)
            .WithHttpMethod(httpMethod)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDAO>();
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task GetProduct_With_ProductNotFound_Should_Return404()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .WithPathParameter("id", "not a real id")
            .Build();
        
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(404);
    }
    
    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProduct_With_ErrorInDataAccess_Should_Return500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Throws<NullReferenceException>();
        
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProduct_With_TimeOut_Should_Return503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}