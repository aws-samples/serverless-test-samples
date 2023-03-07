using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.TestUtilities;
using GetStock.UnitTest.Builder;

namespace GetStock.UnitTest;

public class FunctionsTests
{
    [Fact]
    public void GetStockById_stockIdNotInPath_returnFailure()
    {
        using var autoFake = new AutoFake();

        var target = autoFake.Resolve<Functions>();

        var testLambdaContext = new TestLambdaContext();

        var request = new APIGatewayProxyRequestBuilder().Build();

        var result = target.GetStockById(request, testLambdaContext);

        result.StatusCode.Should().Be(400);
    }
}