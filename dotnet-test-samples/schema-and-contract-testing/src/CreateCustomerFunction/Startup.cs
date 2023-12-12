namespace CreateCustomerFunction;

using Amazon.EventBridge;
using Amazon.Lambda.Annotations;
using Amazon.XRay.Recorder.Handlers.AwsSdk;

using Microsoft.Extensions.DependencyInjection;

using SchemaTesting.Shared;

[LambdaStartup]
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        AWSSDKHandler.RegisterXRayForAllServices();

        services.AddSingleton<IEventPublisher>(new EventBridgeEventPublisher(new AmazonEventBridgeClient()));
        services.AddSingleton(
            new CreateCustomerCommandHandlerOptions()
            {
                EventVersionToPublish = EventVersion.V1
            });

        services.AddSingleton<CreateCustomerCommandHandler>();
    }
}