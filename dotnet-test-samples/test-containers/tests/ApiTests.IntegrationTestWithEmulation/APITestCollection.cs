namespace ApiTests.IntegrationTestWithEmulation;

[CollectionDefinition("APITests")]
public class APITestCollection : ICollectionFixture<TestStartup>
{
    // This class has no code, and is never created. Its purpose is simply
    // to be the place to apply [CollectionDefinition] and all the
    // ICollectionFixture<> interfaces.
}