using Amazon.Lambda.APIGatewayEvents;

namespace GetStock.UnitTest.Builder;

internal class APIGatewayProxyRequestBuilder
{
    private readonly IDictionary<string, string> _pathParamters = new Dictionary<string, string>();

    public APIGatewayProxyRequest Build()
    {
        return new APIGatewayProxyRequest
        {
            PathParameters = _pathParamters
        };
    }

    public APIGatewayProxyRequestBuilder WithPathParamter(string key, string value)
    {
        _pathParamters[key] = value;

        return this;
    }
}