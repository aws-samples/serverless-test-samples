namespace SchemaTesting.Shared;

using Amazon.EventBridge;
using Amazon.EventBridge.Model;

using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;

using Newtonsoft.Json;

public class EventBridgeEventPublisher : IEventPublisher
{
    private readonly IAmazonEventBridge _eventBridge;
    private readonly JsonSerializerSettings _settings;

    public EventBridgeEventPublisher(IAmazonEventBridge eventBridge)
    {
        this._eventBridge = eventBridge;
        this._settings = new JsonSerializerSettings { };
    }

    [Tracing]
    public async Task Publish(EventWrapper evt)
    {
        var evtData = JsonConvert.SerializeObject(
            evt,
            this._settings);

        Logger.LogInformation(evtData);

        await this._eventBridge.PutEventsAsync(
            new PutEventsRequest()
            {
                Entries = new List<PutEventsRequestEntry>(1)
                {
                    new PutEventsRequestEntry
                    {
                        Detail = evtData,
                        DetailType = evt.GetType().Name,
                        EventBusName = Environment.GetEnvironmentVariable("EVENT_BUS_NAME"),
                        Source = $"com.{Environment.GetEnvironmentVariable("ENV")}.customer"
                    }
                }
            });
    }
}