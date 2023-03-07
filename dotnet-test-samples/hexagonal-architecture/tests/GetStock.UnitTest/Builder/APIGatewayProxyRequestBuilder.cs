using Amazon.Lambda.APIGatewayEvents;

namespace GetStock.UnitTest.Builder;

internal class ApiGatewayProxyRequestBuilder
{
    private string _resource = "";
    private string _path = "/";
    private string _httpMethod = "GET";
    private readonly IDictionary<string, string> _headers = new Dictionary<string, string>();
    private readonly IDictionary<string, IList<string>> _multiValueHeaders = new Dictionary<string, IList<string>>();
    private readonly IDictionary<string, IList<string>> _multiValueQueryStringParameters = new Dictionary<string, IList<string>>();
    private readonly IDictionary<string, string> _queryStringParameters = new Dictionary<string, string>();
    private readonly IDictionary<string, string> _pathParamters = new Dictionary<string, string>();
    private readonly IDictionary<string, string> _stageVariables = new Dictionary<string, string>();
    private APIGatewayProxyRequest.ProxyRequestContext _requestContext = new();
    private string _body = "";
    private bool _isBase64Encoded;

    public APIGatewayProxyRequest Build()
    {
        return new APIGatewayProxyRequest
        {
            Resource = _resource,
            Path = _path,
            HttpMethod = _httpMethod,
            Headers = _headers,
            MultiValueHeaders = _multiValueHeaders,
            MultiValueQueryStringParameters = _multiValueQueryStringParameters,
            QueryStringParameters = _queryStringParameters,
            PathParameters = _pathParamters,
            StageVariables = _stageVariables,
            RequestContext = _requestContext,
            Body = _body,
            IsBase64Encoded = _isBase64Encoded
        };
    }

    public ApiGatewayProxyRequestBuilder Resource(string value)
    {
        _resource = value;

        return this;
    }
    
    public ApiGatewayProxyRequestBuilder Path(string value)
    {
        _path = value;

        return this;
    }

    public ApiGatewayProxyRequestBuilder HttpMethod(string value)
    {
        _httpMethod = value;

        return this;
    }

    public ApiGatewayProxyRequestBuilder MultiValueHeader(string key, IList<string> value)
    {
        _multiValueHeaders[key] = value;

        return this;
    }  
    
    public ApiGatewayProxyRequestBuilder MultiValueQueryStringParameters(string key, IList<string> value)
    {
        _multiValueQueryStringParameters[key] = value;

        return this;
    } 
    
    public ApiGatewayProxyRequestBuilder QueryStringParameters(string key, string value)
    {
        _queryStringParameters[key] = value;

        return this;
    }  
    
    public ApiGatewayProxyRequestBuilder PathParamter(string key, string value)
    {
        _pathParamters[key] = value;

        return this;
    }  
    
    public ApiGatewayProxyRequestBuilder StageVariables(string key, string value)
    {
        _stageVariables[key] = value;

        return this;
    }

    public ApiGatewayProxyRequestBuilder RequestContext(APIGatewayProxyRequest.ProxyRequestContext value)
    {
        _requestContext = value;

        return this;
    }

    public ApiGatewayProxyRequestBuilder Body(string value)
    {
        _body = value;

        return this;
    }
    
    public ApiGatewayProxyRequestBuilder IsBase64Encoded(bool value)
    {
        _isBase64Encoded = value;

        return this;
    }
}