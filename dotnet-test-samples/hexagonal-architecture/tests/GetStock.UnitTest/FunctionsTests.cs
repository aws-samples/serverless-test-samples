using Amazon.Lambda.TestUtilities;
using GetStock.Domains;
using GetStock.Ports;
using GetStock.UnitTest.Builder;

namespace GetStock.UnitTest;

public class FunctionsTests
{
    [Fact]
    public void GetStockById_With_PathMissingStockId_Should_ReturnFailure()
    {
        using var autoFake = new AutoFake();

        var target = autoFake.Resolve<Functions>();

        var testLambdaContext = new TestLambdaContext();

        var request = new ApiGatewayProxyRequestBuilder().Build();

        var result = target.GetStockById(request, testLambdaContext);

        result.StatusCode.Should().Be(400);
    }

    [Fact]
    public void GetStockById_With_StockIdInPath_Should_CallFunctionHandler()
    {
        using var autoFake = new AutoFake();

        autoFake.Provide<IHttpHandler, HttpHandler>();

        var target = autoFake.Resolve<Functions>();

        var testLambdaContext = new TestLambdaContext();

        var request = new ApiGatewayProxyRequestBuilder()
            .PathParamter("StockId", "stock-1")
            .Build();

        var result = target.GetStockById(request, testLambdaContext);

        var fakeLogic = autoFake.Resolve<IStockLogic>();

        Assert.Multiple(
                () => result.StatusCode.Should().Be(200),
                () => A.CallTo(() => fakeLogic.RetrieveStockValuesAsync("stock-1")).MustHaveHappened()
            );
    }
}