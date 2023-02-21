using Amazon.Lambda.Core;

namespace ServerlessTestApi.Infrastructure;

public static class LambdaContextExtensions
{
    public static CancellationTokenSource GetCancellationTokenSource(this ILambdaContext context, TimeSpan beforeAbort = default)
    {
        const double PercentOfRemaining = 0.0025;
        var cts = new CancellationTokenSource();
        var remaining = context.RemainingTime;

        if (beforeAbort == default)
        {
            // RemainingTime is the amount of time before Lambda terminates the function.
            // we don't want to go right to the end so we pad the end. if not otherwise
            // specified, use 0.25% of the remaining time. this ensures gives a relative
            // amount of time to gracefully cancel before we are destructively aborted.
            // adjust to your needs accordinginly
            beforeAbort = TimeSpan.FromSeconds(remaining.TotalSeconds * PercentOfRemaining);
        }

        if (beforeAbort > remaining)
        {
            cts.CancelAfter(remaining.Subtract(beforeAbort));
        }

        return cts;
    }
}
