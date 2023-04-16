using AWS.Lambda.Powertools.Logging;

namespace CreateCustomerFunction;

public enum EventVersion
{
    V1,
    V2,
    V3
}

public record CreateCustomerCommandHandlerOptions
{
    public EventVersion EventVersionToPublish { get; set; }
}

public class CreateCustomerCommandHandler
{
    private readonly IEventPublisher _publisher;
    private readonly CreateCustomerCommandHandlerOptions _options = new();

    public CreateCustomerCommandHandler(Action<CreateCustomerCommandHandlerOptions> options, IEventPublisher publisher)
    {
        _publisher = publisher;
        options.Invoke(_options);
    }
    
    public async Task<bool> Handle(CreateCustomerCommand command)
    {
        Logger.LogInformation("Received new create customer event");
        
        // Perform business logic to create customer.
        var validAddress = command.IsValid();
        
        if (!validAddress)
        {
            Logger.LogInformation("Command is invalid, returning");
            return false;
        }
        
        var customerId = Guid.NewGuid().ToString();
        
        Logger.LogInformation($"Generated customer id {customerId}");
        Logger.AppendKey("customerId", customerId);
        
        // Persist to database
        
        // Publish customer created event
        Logger.LogInformation("Publishing customer created event");
        
        await this._publisher.Publish(this.GenerateEvent(customerId, command));

        return true;
    }

    // This method is for demonstrative purposes only to allow the type of event published
    // to be changed based on options. Typically, the event class would change over time.
    private CustomerCreatedEvent GenerateEvent(string customerId, CreateCustomerCommand command)
    {
        CustomerCreatedEvent result = this._options.EventVersionToPublish switch
        {
            EventVersion.V1 => new CustomerCreatedEventV1()
            {
                Address = command.Address,
                FirstName = command.FirstName,
                LastName = command.LastName,
                CustomerId = customerId
            },
            EventVersion.V2 => new CustomerCreatedEventV2()
            {
                Address = command.Address,
                FirstName = command.FirstName,
                LastName = command.LastName,
                CustomerId = customerId,
                Email = "test@test.com"
            },
            EventVersion.V3 => new CustomerCreatedEventV3()
            {
                Address = command.Address,
                CustomerId = customerId
            },
            _ => new CustomerCreatedEventV1()
            {
                Address = command.Address,
                FirstName = command.FirstName,
                LastName = command.LastName,
                CustomerId = customerId
            }
        };

        return result;
    }
}