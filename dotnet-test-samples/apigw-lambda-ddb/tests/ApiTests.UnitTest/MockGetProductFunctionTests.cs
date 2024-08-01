using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using GetProduct;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using System.Text.Json;
using FakeItEasy;

namespace ApiTests.UnitTest;

public class MockGetProductFunctionTests : FunctionTest<Function>
{   
    [Fact]
    public async Task GetProduct_Should_ReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var expected = new ProductDTO("testid", "test product", 10);
        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Returns(Task.FromResult<ProductDTO?>(expected));
        
        var function = new Function(fakeProductDao, Logger, JsonOptions);

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
            .WithPathParameter("id", "123456")
            .WithHttpMethod(httpMethod)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDao>();
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task GetProduct_With_ErrorInDataAccess_Should_Return500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Throws<NullReferenceException>();
        
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    [Fact]
    public async Task GetProduct_With_TimeOut_Should_Return503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }

    [Fact]
    public async Task GetProduct_With_ProductNotFound_Should_Return404()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .WithPathParameter("id", "123456")
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Returns(Task.FromResult<ProductDTO?>(null));
        
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(404);
    }
}