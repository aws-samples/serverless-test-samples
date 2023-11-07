using Xunit.Abstractions;
using Xunit.Sdk;

namespace ApiTests.IntegrationTest;

// REF: https://github.com/xunit/samples.xunit/blob/main/TestOrderExamples/TestCaseOrdering/PriorityOrderer.cs
public sealed class TestOrderer : ITestCaseOrderer
{
    public IEnumerable<TTestCase> OrderTestCases<TTestCase>(IEnumerable<TTestCase> testCases)
        where TTestCase : ITestCase
    {
        var assemblyName = typeof(TestOrderAttribute).AssemblyQualifiedName;
        var sortedMethods = new SortedList<int, SortedList<string, TTestCase>>();

        foreach (var testCase in testCases)
        {
            var method = testCase.TestMethod.Method;
            var attribute = method.GetCustomAttributes(assemblyName).FirstOrDefault();
            var order = attribute?.GetNamedArgument<int>(nameof(TestOrderAttribute.Order)) ?? 0;

            if (!sortedMethods.TryGetValue(order, out var group))
            {
                sortedMethods.Add(order, group = new());
            }

            group.Add(method.Name, testCase);
        }

        var groups = sortedMethods.Values;

        for (var i = 0; i < groups.Count; i++)
        {
            var items = groups[i].Values;

            for (var j = 0; j < items.Count; j++)
            {
                yield return items[j];
            }
        }
    }
}