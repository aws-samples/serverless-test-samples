namespace ApiTests.IntegrationTestWithEmulation;

using System.Text.Json;

using Amazon.Lambda.APIGatewayEvents;

public class ApiRequestBuilder
{
    private readonly List<string> _path = new() { "dev" };
    private string? _body;
    private HttpMethod? _httpMethod;
    private Dictionary<string, string>? _pathParams;
    private Dictionary<string, string>? _headers;

    public ApiRequestBuilder WithPathParameter(string name, string value)
    {
        this._pathParams ??= new(StringComparer.OrdinalIgnoreCase);
        this._pathParams.Add(name, value);
        this._path.Add(value);
        return this;
    }

    public ApiRequestBuilder WithHttpMethod(string httpMethod) =>
        this.WithHttpMethod(new HttpMethod(httpMethod));

    public ApiRequestBuilder WithHttpMethod(HttpMethod httpMethod)
    {
        this._httpMethod = httpMethod;
        return this;
    }

    public ApiRequestBuilder WithBody(string body)
    {
        this._body = body;
        return this;
    }

    public ApiRequestBuilder WithBody<T>(T body, JsonSerializerOptions? jsonOptions = default)
    {
        this._body = JsonSerializer.Serialize(body, jsonOptions);
        return this;
    }

    public ApiRequestBuilder WithHeader(string name, string value)
    {
        this._headers ??= new(StringComparer.OrdinalIgnoreCase);
        this._headers[name] = value;
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
                    Method = (this._httpMethod ?? HttpMethod.Get).Method,
                    Path = string.Join('/', this._path),
                }
            },
            PathParameters = this._pathParams,
            Body = this._body,
            Headers = this._headers,
        };
}