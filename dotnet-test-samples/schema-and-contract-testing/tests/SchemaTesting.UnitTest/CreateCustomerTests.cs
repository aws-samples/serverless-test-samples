using CreateCustomerFunction;

namespace SchemaTesting.UnitTest;

using Autofac.Extras.FakeItEasy;

using CreateCustomerFunction.CustomerCreatedEvent;

using SchemaTesting.Shared;

public class AddressTests
{
    private IEventPublisher _eventPublisher;

    public AddressTests()
    {
        this._eventPublisher = A.Fake<IEventPublisher>();
        A.CallTo(() => this._eventPublisher.Publish(A<EventWrapper>._));
    }
    [Fact]
    public async Task ProcessCommandWithValidAddress_ShouldReturnSuccess()
    {
        using var autoFake = new AutoFake();

        var commandHandler = autoFake.Resolve<CreateCustomerCommandHandler>();
        
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
    public async Task ParseEmptyAddressEvent_ShouldReturnNull()
    {
        using var autoFake = new AutoFake();

        var commandHandler = autoFake.Resolve<CreateCustomerCommandHandler>();
        
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