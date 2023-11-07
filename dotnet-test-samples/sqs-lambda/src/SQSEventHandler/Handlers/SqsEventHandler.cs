using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.SQSEvents;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Metrics;
using AWS.Lambda.Powertools.Tracing;
using SqsEventHandler.Infrastructure;

namespace SqsEventHandler.Handlers;

/// <summary>
/// This class abstracts the AWS interaction between Amazon Simple Queue Service (SQS) & AWS Lambda Function.
/// </summary>
/// <typeparam name="TMessage">A generic SQS Message Model Type</typeparam>
public abstract class SqsEventHandler<TMessage> where TMessage : class, new()
{
    protected readonly IServiceProvider ServiceProvider;
    private List<SQSBatchResponse.BatchItemFailure> _batchItemFailures;
    private readonly SQSBatchResponse _sqsBatchResponse;

    protected SqsEventHandler() : this(Startup.ServiceProvider)
    {
        _sqsBatchResponse = new SQSBatchResponse();
    }

    private SqsEventHandler(IServiceProvider serviceProvider)
    {
        ServiceProvider = serviceProvider;
    }

    /// <summary>
    /// This method is completely abstracted from AWS Infrastructure and is called for every message.
    /// </summary>
    /// <param name="message">SQS Message Object</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns></returns>
    public abstract Task ProcessSqsMessage(TMessage message, ILambdaContext lambdaContext);

    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in an SQS event object and creates
    /// an SQS Event adapter for processing the batch of SQS messages.
    /// </summary>
    /// <param name="sqsEvent">SQS Event received by the function handler</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns></returns>
    [Logging(LogEvent = true, ClearState = true)]
    [Metrics(Namespace = "SqsEventHandler", CaptureColdStart = true)]
    [Tracing(Namespace = "SqsEventHandler", SegmentName = "SqsEventHandler")]
    public async Task<SQSBatchResponse> Handler(SQSEvent sqsEvent, ILambdaContext lambdaContext)
    {
        await ProcessEvent(sqsEvent, lambdaContext);

        // Set BatchItemFailures if any
        if (_batchItemFailures != null)
        {
            _sqsBatchResponse.BatchItemFailures = _batchItemFailures;
        }

        return _sqsBatchResponse;
    }

    /// <summary>
    /// This method abstracts the SQS Event for downstream processing.
    /// </summary>
    /// <param name="sqsEvent">SQS Event received by the function handler</param>
    /// <param name="lambdaContext">Lambda Context</param>
    [Tracing(SegmentName = "ProcessEvent")]
    private async Task ProcessEvent(SQSEvent sqsEvent, ILambdaContext lambdaContext)
    {
        var sqsMessages = sqsEvent.Records;
        var batchItemFailures = new List<SQSBatchResponse.BatchItemFailure>();

        foreach (var sqsMessage in sqsMessages)
        {
            try
            {
                var message = JsonSerializer.Deserialize<TMessage>(sqsMessage.Body);

                // This abstract method is implemented by the concrete classes i.e. ProcessEmployeeFunction.
                await ProcessSqsMessage(message, lambdaContext);
            }
            catch (Exception ex)
            {
                Logger.LogError(ex);
                batchItemFailures.Add(
                    new SQSBatchResponse.BatchItemFailure
                    {
                        ItemIdentifier = sqsMessage.MessageId
                    }
                );
            }
        }

        _batchItemFailures = batchItemFailures;
    }
}