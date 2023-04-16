namespace SchemaTesting.Validation;

public abstract class Event { }

public interface IEventPublisher
{
    Task Publish(Event evt);
}