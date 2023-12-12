
namespace SchemaTesting.Shared;

public abstract class Event
{
    public abstract string Type { get; }
}

public interface IEventPublisher
{
    Task Publish(EventWrapper evt);
}