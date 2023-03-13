#define RUN_LOCAL_DB

#if RUN_LOCAL_DB
global using DynamoDbFixture = GetStock.IntegrationTest.Fixtures.LocalDynamoDbFixture;
#else
global using DynamoDbFixture = GetStock.IntegrationTest.Fixtures.CloudDynamoDbFixture;
#endif

global using Xunit;