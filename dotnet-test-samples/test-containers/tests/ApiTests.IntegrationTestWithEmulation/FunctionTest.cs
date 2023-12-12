namespace ApiTests.IntegrationTestWithEmulation;

using System.Text.Json;

using Amazon.XRay.Recorder.Core;

using FakeItEasy;

using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

public abstract class FunctionTest<TFunc>
{
    protected FunctionTest()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }

    protected IOptions<JsonSerializerOptions> JsonOptions { get; } =
        Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web));

    protected ILogger<TFunc> Logger { get; } = A.Fake<ILogger<TFunc>>();
}