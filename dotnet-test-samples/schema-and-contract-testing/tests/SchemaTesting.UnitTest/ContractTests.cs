using CreateCustomerFunction;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema;

namespace SchemaTesting.UnitTest;

using CreateCustomerFunction.CustomerCreatedEvent;

using Newtonsoft.Json;

using SchemaTesting.Shared;

public class ContractTests
{
    private readonly List<BaseCustomerCreatedEvent?> _publishedEvents;
    private readonly IEventPublisher _mockEventPublisher;
    private readonly ISchemaReader _schemaReader;

    public ContractTests()
    {
        this._publishedEvents = new List<BaseCustomerCreatedEvent?>();
        this._mockEventPublisher = A.Fake<IEventPublisher>();
        A.CallTo(() => _mockEventPublisher.Publish(A<EventWrapper>._))
            .Invokes(
                fakedCall =>
                {
                    var evt = fakedCall.Arguments.Get<EventWrapper>("evt");
                    _publishedEvents.Add(evt!.Payload as BaseCustomerCreatedEvent);
                });
        
        _schemaReader = new LocalDiskSchemaReader();
    }
    
    [Fact]
    public async Task EventPayloadMatchesSchema_ShouldPass()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V1
        },_mockEventPublisher);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        _publishedEvents.Count.Should().Be(1);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(JsonConvert.SerializeObject(_publishedEvents[0] as CustomerCreatedEventV1));

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.0.0");

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema).Should().BeTrue();
    }
    
    [Fact]
    public async Task OptionalElementsAddedToExpectedSchema_ShouldPass()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V1
        },_mockEventPublisher);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        _publishedEvents.Count.Should().Be(1);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(JsonConvert.SerializeObject(_publishedEvents[0] as CustomerCreatedEventV1));

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.3.0");

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema).Should().BeTrue();
    }
    
    [Fact]
    public async Task AdditionalElementsAddedToEventPayload_ShouldPass()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V2
        }, _mockEventPublisher);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        _publishedEvents.Count.Should().Be(1);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(JsonConvert.SerializeObject(_publishedEvents[0] as CustomerCreatedEventV2));

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.0.0");

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema).Should().BeTrue();
    }
    
    [Fact]
    public async Task ElementsRemovedFromEventPayload_ShouldFail()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V3
        }, _mockEventPublisher);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        _publishedEvents.Count.Should().Be(1);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(JsonConvert.SerializeObject(_publishedEvents[0] as CustomerCreatedEventV3));

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.0.0");

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema).Should().BeFalse();
    }
    
    [Fact]
    public async Task EventPayloadDoesNotMatchSchema_ShouldFail()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V1
        },_mockEventPublisher);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        _publishedEvents.Count.Should().Be(1);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(JsonConvert.SerializeObject(_publishedEvents[0] as CustomerCreatedEventV1));

        var schema = await this._schemaReader.ReadJsonSchemaAsync("1.2.0");

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema).Should().BeFalse();
    }
}