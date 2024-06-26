using System.Text.Json.Serialization;
using ChatbotDemo.Infrastructure.Models.Request;

namespace ChatbotDemo.Infrastructure.Models.Response;

public record FunctionDetailsResponse
{
    [JsonPropertyName("actionGroup")]
    public string ActionGroup { get; set; }

    [JsonPropertyName("function")]
    public string Function { get; set; }

    [JsonPropertyName("functionResponse")]
    public FunctionResponse FunctionResponse { get; init; }
}

public class FunctionDetailsResponseBuilder(BedrockFunctionDetailsRequest request)
{
    private readonly FunctionDetailsResponse _response = new()
    {
        ActionGroup = request.ActionGroup,
        Function = request.Function,
        FunctionResponse = new FunctionResponse
        {
            ResponseBody = new ResponseBody
            {
                ResponseContentType = new ResponseContentType
                {
                    Body = string.Empty
                }
            }
        }
    };

    public FunctionDetailsResponse WithBody(string body)
    {
        _response.FunctionResponse.ResponseBody.ResponseContentType.Body = body;
        return _response;
    }
    
    public FunctionDetailsResponse WithResponseState(string responseState)
    {
        _response.FunctionResponse.ResponseState = responseState;
        return _response;
    }

    public FunctionDetailsResponse Build()
    {
        return _response;
    }
}