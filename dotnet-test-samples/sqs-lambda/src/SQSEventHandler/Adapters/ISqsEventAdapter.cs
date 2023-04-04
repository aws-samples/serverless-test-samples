using System.Collections.Generic;
using Amazon.Lambda.SQSEvents;

namespace SqsEventHandler.Adapters;

public interface ISqsEventAdapter
{
    SQSBatchResponse GetSqsBatchResponse();
    List<SQSEvent.SQSMessage> GetSqsBatchMessages();
    void SetSqsBatchItemFailures(List<SQSBatchResponse.BatchItemFailure> batchItemFailures);
}