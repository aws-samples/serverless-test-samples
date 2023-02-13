using Amazon.Lambda.APIGatewayEvents;
using System.Text.Json;

namespace ApiTests.UnitTest;

public class ApiRequestBuilder
{
    private readonly List<string> _path = new() { "dev" };
    private string? _body;
    private HttpMethod? _httpMethod;
    private Dictionary<string, string>? _pathParams;
    private Dictionary<string, string>? _headers;

    public ApiRequestBuilder WithPathParameter(string name, string value)
    {
        _pathParams ??= new(StringComparer.OrdinalIgnoreCase);
        _pathParams.Add(name, value);
        _path.Add(value);
        return this;
    }

    public ApiRequestBuilder WithHttpMethod(string httpMethod) =>
        WithHttpMethod(new HttpMethod(httpMethod));

    public ApiRequestBuilder WithHttpMethod(HttpMethod httpMethod)
    {
        _httpMethod = httpMethod;
        return this;
    }

    public ApiRequestBuilder WithBody(string body)
    {
        _body = body;
        return this;
    }

    public ApiRequestBuilder WithBody<T>(T body, JsonSerializerOptions? jsonOptions = default)
    {
        _body = JsonSerializer.Serialize(body, jsonOptions);
        return this;
    }

    public ApiRequestBuilder WithHeader(string name, string value)
    {
        _headers ??= new(StringComparer.OrdinalIgnoreCase);
        _headers[name] = value;
        return this;
    }

    public APIGatewayHttpApiV2ProxyRequest Build() =>
        new()
        {
            RequestContext = new APIGatewayHttpApiV2ProxyRequest.ProxyRequestContext()
            {
                DomainName = "localhost",
                Http = new APIGatewayHttpApiV2ProxyRequest.HttpDescription()
                {
                    Method = (_httpMethod ?? HttpMethod.Get).Method,
                    Path = string.Join('/', _path),
                }
            },
            PathParameters = _pathParams,
            Body = _body,
            Headers = _headers,
        };
}