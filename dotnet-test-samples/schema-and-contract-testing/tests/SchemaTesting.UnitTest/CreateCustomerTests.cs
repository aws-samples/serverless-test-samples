using CreateCustomerFunction;

namespace SchemaTesting.UnitTest;

public class AddressTests
{
    [Fact]
    public async Task ProcessCommandWithValidAddress_ShouldReturnSuccess()
    {
        var commandHandler = new CreateCustomerCommandHandler(options =>
        {
            options.EventVersionToPublish = EventVersion.V1;
        },new Mock<IEventPublisher>().Object);
        
        var sampleCommand = new CreateCustomerCommand()
        {
            Address = "60 Holbon Viaduct, London, Greater London, EC12 2BN, United Kingdom",
            FirstName = "John",
            LastName = "Doe"
        };

        var result = await commandHandler.Handle(sampleCommand);

        result.Should().BeTrue();
    }
    
    [Fact]
    public async Task ParseEmptyAddressEvent_ShouldReturnNull()
    {
        var commandHandler = new CreateCustomerCommandHandler(options =>
        {
            options.EventVersionToPublish = EventVersion.V1;
        },new Mock<IEventPublisher>().Object);
        
        var sampleCommand = new CreateCustomerCommand()
        {
            Address = "",
            FirstName = "John",
            LastName = "Doe"
        };

        var result = await commandHandler.Handle(sampleCommand);

        result.Should().BeFalse();
    }
}