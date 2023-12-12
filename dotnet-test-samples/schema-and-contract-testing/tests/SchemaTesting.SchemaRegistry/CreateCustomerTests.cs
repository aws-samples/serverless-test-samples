namespace SchemaTesting.SchemaRegistry;

using CreateCustomerFunction;

using SchemaTesting.Shared;

public class AddressTests
{
    [Fact]
    public async Task HandleCreateCustomerCommand_With_ValidRequest_Should_CompleteSuccessfully()
    {
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V1
        },new Mock<IEventPublisher>().Object);
        
        var sampleCommand = new CreateCustomerCommand()
        {
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom",
            FirstName = "John",
            LastName = "Doe"
        };

        var result = await commandHandler.Handle(sampleCommand);

        result.Success.Should().BeTrue();
    }
    
    [Fact]
    public async Task HandleCreateCustomerCommand_With_EmptyAddressProperty_Should_ReturnNull()
    {
        var commandHandler = new CreateCustomerCommandHandler(new CreateCustomerCommandHandlerOptions()
        {
            EventVersionToPublish = EventVersion.V1
        },new Mock<IEventPublisher>().Object);
        
        var sampleCommand = new CreateCustomerCommand()
        {
            Address = "",
            FirstName = "John",
            LastName = "Doe"
        };

        var result = await commandHandler.Handle(sampleCommand);

        result.Success.Should().BeFalse();
    }
}