using System.Collections.Generic;
using Amazon.Lambda.SQSEvents;

namespace SqsEventHandler.Adapters;

public class SqsEventAdapter : ISqsEventAdapter
{
    private readonly SQSEvent _sqsEvent;
    private List<SQSBatchResponse.BatchItemFailure> _batchItemFailures;
    private readonly SQSBatchResponse _sqsBatchResponse;

    public SqsEventAdapter(SQSEvent sqsEvent)
    {
        _sqsEvent = sqsEvent;
        _sqsBatchResponse = new SQSBatchResponse();
    }

    public SQSBatchResponse GetSqsBatchResponse()
    {
        if (_batchItemFailures != null)
        {
            _sqsBatchResponse.BatchItemFailures = _batchItemFailures;
        }

        return _sqsBatchResponse;
    }

    public List<SQSEvent.SQSMessage> GetSqsBatchMessages()
        => _sqsEvent.Records;

    public void SetSqsBatchItemFailures(List<SQSBatchResponse.BatchItemFailure> batchItemFailures)
        => _batchItemFailures = batchItemFailures;
}