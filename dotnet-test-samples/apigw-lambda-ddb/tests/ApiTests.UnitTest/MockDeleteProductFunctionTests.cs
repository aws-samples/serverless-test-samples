using System.ComponentModel;
using Amazon.Lambda.TestUtilities;
using DeleteProduct;
using FakeItEasy;
using FluentAssertions;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockDeleteProductFunctionTests : FunctionTest<Function>
{   
    [Fact]
    public async Task DeleteProduct_With_ProductInDb_Should_ReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Delete)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Returns(Task.FromResult<ProductDTO?>(new ProductDTO("123456", "Test Product", 10)));
        
        var function = new Function(fakeProductDao, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);
        
        A.CallTo(() => fakeProductDao.DeleteProduct("123456", A<CancellationToken>._))
            .MustHaveHappened();
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("GET")]
    public async Task TestLambdaHandler_With_NonDeleteRequests_Should_Return405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(httpMethod)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDAO>();
        var function = new Function(fakeProductDao, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task DeleteProduct_With_ErrorInDeleteDataAccess_Should_Return500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Delete)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDAO>();
        A.CallTo(() => fakeProductDao.DeleteProduct(A<string>._, A<CancellationToken>._))
            .Throws<NullReferenceException>();
        
        var function = new Function(fakeProductDao, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }
    
    [Fact]
    public async Task DeleteProduct_With_TimeOut_Should_Return503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Delete)
            .Build();
        
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.DeleteProduct(A<string>._, A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}