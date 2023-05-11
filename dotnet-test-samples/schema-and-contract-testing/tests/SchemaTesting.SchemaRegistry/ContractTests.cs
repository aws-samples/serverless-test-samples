namespace SchemaTesting.SchemaRegistry;

using CreateCustomerFunction;

using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema;

using SchemaTesting.Shared;

public class ContractTests : IClassFixture<Setup>
{
    private readonly Setup _setup;
    private readonly List<EventBusEventOverride<CustomerCreatedEvent>> _publishedEvents;
    private readonly Mock<IEventPublisher> _mockEventPublisher;
    private readonly JsonSerializerSettings settings = new() { NullValueHandling = NullValueHandling.Ignore };

    public ContractTests(Setup setup)
    {
        this._setup = setup;
        this._publishedEvents = new List<EventBusEventOverride<CustomerCreatedEvent>>();
        this._mockEventPublisher = new Mock<IEventPublisher>();
        this._mockEventPublisher.Setup(p => p.Publish(It.IsAny<EventWrapper>()))
            .Callback((EventWrapper e) =>
            {
                this._publishedEvents.Add(new EventBusEventOverride<CustomerCreatedEvent>(e.Payload));
            });
    }
    
    [Fact]
    public async Task EventPayload_With_MatchingSchema_Should_PassSchemaValidation()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(options =>
        {
            options.EventVersionToPublish = EventVersion.V1;
        },this._mockEventPublisher.Object);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        this._publishedEvents.Count.Should().Be(1);

        var publishedEventJsonString = JsonConvert.SerializeObject(
            this._publishedEvents[0],
            settings).Replace("\"Type\"", "\"-type\"");
        
        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(publishedEventJsonString);
        
        var schema = await this._setup.SchemaReader.ReadJsonSchemaAsync(nameof(CustomerCreatedEventV1), "1");

        IList<string> errorMessages;

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema, out errorMessages);

        errorMessages.Count.Should().Be(0);
    }
    
    [Fact]
    public async Task EventPayload_With_NonBreakingChange_Should_PassSchemaValidation()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(options =>
        {
            // The V2 event type introduces a non-breaking change by adding an email address field.
            options.EventVersionToPublish = EventVersion.V2;
        },this._mockEventPublisher.Object);

        // Act
        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Assert
        // Check that an event is published
        this._publishedEvents.Count.Should().Be(1);

        var publishedEventJsonString = JsonConvert.SerializeObject(this._publishedEvents[0], settings);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(publishedEventJsonString);

        var schema = await this._setup.SchemaReader.ReadJsonSchemaAsync(nameof(CustomerCreatedEventV1), "1");

        IList<string> errorMessages;

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema, out errorMessages);

        errorMessages.Count.Should().Be(0);
    }
    
    [Fact]
    public async Task EventPayload_With_DifferentSchema_Should_FailSchemaValidation()
    {
        // Create a new command handler using the mock event publisher.
        var commandHandler = new CreateCustomerCommandHandler(options =>
        {
            options.EventVersionToPublish = EventVersion.V3;
        },this._mockEventPublisher.Object);

        await commandHandler.Handle(new CreateCustomerCommand()
        {
            FirstName = "John", LastName = "Doe",
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom"
        });

        // Check that an event is published
        this._publishedEvents.Count.Should().Be(1);

        var publishedEventJsonString = JsonConvert.SerializeObject(this._publishedEvents[0], settings);

        // Parse the published event as a JObject.
        var publishedEventJson = JObject.Parse(publishedEventJsonString);

        var schema = await this._setup.SchemaReader.ReadJsonSchemaAsync(nameof(CustomerCreatedEventV1), "1");

        // Compare the published event JSON to the expected schema.
        IList<string> errorMessages;

        // Compare the published event JSON to the expected schema.
        publishedEventJson.IsValid(schema, out errorMessages);

        errorMessages.Count.Should().BeGreaterThan(0);
    }
}