namespace ApiTests.IntegrationTestWithEmulation;

using System.Net;

using Amazon.Lambda.TestUtilities;

using FakeItEasy;

using FluentAssertions;

using ServerlessTestApi;
using ServerlessTestApi.Core.DataAccess;

[Collection("APITests")]
public class MockDeleteProductFunctionTests : FunctionTest<Function>
{
    private readonly TestStartup _startup;

    public MockDeleteProductFunctionTests(TestStartup startup)
    {
        this._startup = startup;
    }
    
    [Fact]
    public async Task DeleteProduct_With_ProductInDb_Should_ReturnSuccess()
    {
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.DeleteProduct("123456", new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
    
    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task DeleteProduct_With_ErrorInDeleteDataAccess_Should_Return500()
    {
        var fakeProductDao = A.Fake<IProductsDAO>();
        A.CallTo(() => fakeProductDao.DeleteProduct(A<string>._, A<CancellationToken>._))
            .Throws<NullReferenceException>();
        
        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.DeleteProduct("123456", new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.InternalServerError);
    }
    
    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task DeleteProduct_With_TimeOut_Should_Return503()
    {
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.DeleteProduct(A<string>._, A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.DeleteProduct("123456", new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.ServiceUnavailable);
    }
}