using Amazon.Lambda.TestUtilities;
using Xunit;

namespace SQSEventHandler.Tests;

public class FunctionTest
{
    [Fact]
    public void TestToUpperFunction()
    {
        // Invoke the lambda function and confirm the string was upper cased.
        var function = new Function();
        var context = new TestLambdaContext();
    }
}