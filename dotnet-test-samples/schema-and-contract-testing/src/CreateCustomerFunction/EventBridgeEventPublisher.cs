using System.Text.Json;
using Amazon.EventBridge;
using Amazon.EventBridge.Model;

namespace CreateCustomerFunction;

public class EventBridgeEventPublisher : IEventPublisher
{
    private readonly IAmazonEventBridge _eventBridge;

    public EventBridgeEventPublisher(IAmazonEventBridge eventBridge)
    {
        _eventBridge = eventBridge;
    }
    
    public async Task Publish(Event evt)
    {
        await this._eventBridge.PutEventsAsync(new PutEventsRequest()
        {
            Entries = new List<PutEventsRequestEntry>(1)
            {
                new PutEventsRequestEntry
                {
                    Detail = JsonSerializer.Serialize(evt),
                    DetailType = evt.GetType().Name,
                    EventBusName = Environment.GetEnvironmentVariable("EVENT_BUS_NAME"),
                    Source = $"com.{Environment.GetEnvironmentVariable("ENV")}.customer"
                }
            }
        });
    }
}