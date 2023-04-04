using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.SQSEvents;
using Newtonsoft.Json;
using SqsEventHandler.Adapters;

namespace SqsEventHandler.Triggers;

public abstract class SqsEventTrigger<TMessage> where TMessage : class, new()
{
    /// <summary>
    /// This method is completely abstracted from AWS Infrastructure and is called for every message.
    /// </summary>
    /// <param name="message"></param>
    /// <param name="lambdaContext"></param>
    /// <returns></returns>
    public abstract Task ProcessSqsMessage(TMessage message, ILambdaContext lambdaContext);

    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in an SQS event object and creates
    /// an SQS Event adapter for processing the batch of SQS messages
    /// </summary>
    /// <param name="sqsEvent"></param>
    /// <param name="lambdaContext"></param>
    /// <returns></returns>
    public async Task<SQSBatchResponse> Handler(SQSEvent sqsEvent, ILambdaContext lambdaContext)
    {
        var sqsEventAdapter = new SqsEventAdapter(sqsEvent);
        await ProcessEvent(sqsEventAdapter, lambdaContext);
        return sqsEventAdapter.GetSqsBatchResponse();
    }

    /// <summary>
    /// This method abstracts the SQS Event for downstream processing
    /// </summary>
    /// <param name="sqsEventAdapter"></param>
    /// <param name="lambdaContext"></param>
    private async Task ProcessEvent(ISqsEventAdapter sqsEventAdapter, ILambdaContext lambdaContext)
    {
        var sqsMessages = sqsEventAdapter.GetSqsBatchMessages();
        var sqsMessageFailures = new List<SQSBatchResponse.BatchItemFailure>();

        foreach (var sqsMessage in sqsMessages)
        {
            try
            {
                lambdaContext.Logger.LogLine($"Processing {sqsMessage.EventSource} Message Id: {sqsMessage.MessageId}");

                var message = JsonConvert.DeserializeObject<TMessage>(sqsMessage.Body);
                await ProcessSqsMessage(message, lambdaContext);
            }
            catch (Exception ex)
            {
                lambdaContext.Logger.LogError($"Exception: {ex.Message}");
                sqsMessageFailures.Add(
                    new SQSBatchResponse.BatchItemFailure
                    {
                        ItemIdentifier = sqsMessage.MessageId
                    }
                );
            }
        }

        sqsEventAdapter.SetSqsBatchItemFailures(sqsMessageFailures);
    }
}