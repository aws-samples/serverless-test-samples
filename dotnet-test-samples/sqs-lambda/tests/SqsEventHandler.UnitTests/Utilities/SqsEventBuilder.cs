using System;
using System.Collections.Generic;
using System.Text.Json;
using Amazon.Lambda.SQSEvents;
using SqsEventHandler.Models;

namespace SqsEventHandler.UnitTests.Utilities;

public class SqsEventBuilder
{
    private readonly SQSEvent _sqsEvent;

    public SqsEventBuilder()
    {
        _sqsEvent = new SQSEvent
        {
            Records = new List<SQSEvent.SQSMessage>()
        };
    }

    public SQSEvent WithEmployees(IEnumerable<Employee> employees)
    {
        foreach (var employee in employees)
        {
            _sqsEvent.Records.Add(new SQSEvent.SQSMessage
            {
                MessageId = Guid.NewGuid().ToString(),
                Body = JsonSerializer.Serialize(employee),
                EventSource = "aws:sqs"
            });
        }

        return _sqsEvent;
    }

    public SQSEvent WithoutEmployees()
    {
        _sqsEvent.Records.Add(new SQSEvent.SQSMessage
        {
            MessageId = Guid.NewGuid().ToString(),
            Body = null,
            EventSource = "aws:sqs"
        });

        return _sqsEvent;
    }

    public SQSEvent Build()
    {
        return _sqsEvent;
    }
}