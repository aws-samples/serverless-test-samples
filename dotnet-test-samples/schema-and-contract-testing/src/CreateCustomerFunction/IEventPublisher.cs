namespace CreateCustomerFunction;

public abstract class Event { }

public interface IEventPublisher
{
    Task Publish(Event evt);
}