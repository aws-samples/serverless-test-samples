using Amazon.Lambda.TestUtilities;
using GetStock.UnitTest.Builder;
using HexagonalArchitecture.Domains;
using HexagonalArchitecture.Ports;

namespace GetStock.UnitTest;

public class FunctionsTests
{
    [Fact]
    public void GetStockById_stockIdNotInPath_returnFailure()
    {
        using var autoFake = new AutoFake();

        var target = autoFake.Resolve<Functions>();

        var testLambdaContext = new TestLambdaContext();

        var request = new ApiGatewayProxyRequestBuilder().Build();

        var result = target.GetStockById(request, testLambdaContext);

        result.StatusCode.Should().Be(400);
    }

    [Fact]
    public void GetStockById_stockIdInPath_callFunctionHandler()
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
                () => A.CallTo(() => fakeLogic.RetrieveStockValues("stock-1")).MustHaveHappened()
            );
    }
}