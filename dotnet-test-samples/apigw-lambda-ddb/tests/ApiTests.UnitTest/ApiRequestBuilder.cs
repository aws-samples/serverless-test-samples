using System.Text.Json;
using Amazon.Lambda.APIGatewayEvents;

namespace ApiTests.UnitTest;

public class ApiRequestBuilder
{
    private APIGatewayHttpApiV2ProxyRequest _request;
    private string httpMethod;
    private string body;
    private Dictionary<string, string> headers;
    private Dictionary<string, string> pathParams;

    public ApiRequestBuilder()
    {
        this._request = new APIGatewayHttpApiV2ProxyRequest();
        this.pathParams = new Dictionary<string, string>();
        this.headers = new Dictionary<string, string>();
    }

    public ApiRequestBuilder WithPathParameter(string paramName, string value)
    {
        this.pathParams.Add(paramName, value);
        return this;
    }

    public ApiRequestBuilder WithHttpMethod(string methodName)
    {
        this.httpMethod = methodName;
        return this;
    }

    public ApiRequestBuilder WithBody(string body)
    {
        this.body = body;
        return this;
    }

    public ApiRequestBuilder WithBody(object body)
    {
        this.body = JsonSerializer.Serialize(body);
        return this;
    }

    public ApiRequestBuilder WithHeaders(Dictionary<string, string> headers)
    {
        this.headers = headers;
        return this;
    }

    public APIGatewayHttpApiV2ProxyRequest Build()
    {
        this._request = new APIGatewayHttpApiV2ProxyRequest()
        {
            RequestContext = new APIGatewayHttpApiV2ProxyRequest.ProxyRequestContext()
            {
                Http = new APIGatewayHttpApiV2ProxyRequest.HttpDescription()
                {
                    Method = httpMethod
                }
            },
            PathParameters = pathParams,
            Body = body,
            Headers = headers
        };

        return this._request;
    }
}