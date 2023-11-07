using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using Amazon.Kinesis;
using Amazon.Lambda.KinesisEvents;
using KinesisEventHandler.Models;

namespace KinesisEventHandler.UnitTests.Utilities;

public class KinesisEventBuilder
{
    private readonly KinesisEvent _kinesisEvent;

    public KinesisEventBuilder()
    {
        _kinesisEvent = new KinesisEvent
        {
            Records = new List<KinesisEvent.KinesisEventRecord>()
        };
    }

    public KinesisEvent WithEmployees(IEnumerable<Employee> employees)
    {
        foreach (var employee in employees)
        {
            _kinesisEvent.Records.Add(new KinesisEvent.KinesisEventRecord
            {
                Kinesis = new KinesisEvent.Record
                {
                    Data = new MemoryStream(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(employee))),
                    EncryptionType = EncryptionType.NONE,
                    PartitionKey = "partitionKey-03",
                    SequenceNumber = Guid.NewGuid().ToString(),
                    ApproximateArrivalTimestamp = DateTime.Now,
                    KinesisSchemaVersion = "1.0"
                },
                AwsRegion = "us-east-1",
                EventId = $"shardId-000000000000:{Guid.NewGuid().ToString()}",
                EventName = "aws:kinesis:record",
                EventSource = "aws:kinesis",
                EventVersion = "1.0",
                InvokeIdentityArn = "arn:aws:kinesis:EXAMPLE",
                EventSourceARN = "arn:aws:kinesis:EXAMPLE"
            });
        }

        return _kinesisEvent;
    }

    public KinesisEvent WithoutEmployees()
    {
        _kinesisEvent.Records.Add(new KinesisEvent.KinesisEventRecord
        {
            Kinesis = new KinesisEvent.Record
            {
                Data = new MemoryStream(),
                EncryptionType = EncryptionType.NONE,
                PartitionKey = "partitionKey-03",
                SequenceNumber = Guid.NewGuid().ToString(),
                ApproximateArrivalTimestamp = DateTime.Now,
                KinesisSchemaVersion = "1.0"
            },
            AwsRegion = "us-east-1",
            EventId = $"shardId-000000000000:{Guid.NewGuid().ToString()}",
            EventName = "aws:kinesis:record",
            EventSource = "aws:kinesis",
            EventVersion = "1.0",
            InvokeIdentityArn = "arn:aws:kinesis:EXAMPLE",
            EventSourceARN = "arn:aws:kinesis:EXAMPLE"
        });

        return _kinesisEvent;
    }

    public KinesisEvent Build()
    {
        return _kinesisEvent;
    }
}