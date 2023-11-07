using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using GetProducts;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using System.Text.Json;
using FakeItEasy;

namespace ApiTests.UnitTest;

using ProductAPI.Tests;

[Collection("APITests")]
public class MockGetProductsFunctionTests : FunctionTest<Function>
{
    private readonly TestStartup _startup;

    public MockGetProductsFunctionTests(TestStartup startup)
    {
        this._startup = startup;
    }

    [Fact]
    public async Task GetProducts_Should_ReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // arrange
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ProductWrapper>(response.Body, JsonOptions.Value);

        body!.Products.Should().HaveCountGreaterThan(0);
    }

    [Fact]
    public async Task GetProducts_With_DataAccessReturnsProducts_Should_ReturnInBody()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var expected = new ProductWrapper(
            new List<ProductDTO>(capacity: 1)
            {
                new(this._startup.TestProduct.Id, this._startup.TestProduct.Name, this._startup.TestProduct.Price),
            });

        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ProductWrapper>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(expected);
    }

    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_With_NonGetRequests_Should_Return405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(httpMethod)
            .Build();

        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var result = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        result.StatusCode.Should().Be(405);
    }

    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProducts_With_ErrorInDataAccess_Should_Return500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetAllProducts(A<CancellationToken>._))
            .Throws<NullReferenceException>();

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProducts_With_TimeOut_Should_Return503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetAllProducts(A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}