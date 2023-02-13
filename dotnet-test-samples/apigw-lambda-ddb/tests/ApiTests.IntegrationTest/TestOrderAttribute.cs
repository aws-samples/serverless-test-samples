namespace ApiTests.IntegrationTest;

// REF: https://github.com/xunit/samples.xunit/blob/main/TestOrderExamples/TestCaseOrdering/TestPriorityAttribute.cs
[AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
public sealed class TestOrderAttribute : Attribute
{
    public TestOrderAttribute(int order) => Order = order;

    public int Order { get; }
}