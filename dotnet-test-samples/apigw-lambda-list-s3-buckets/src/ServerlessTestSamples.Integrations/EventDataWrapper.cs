using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ServerlessTestSamples.Integrations
{
    public class EventDataWrapper<T>
    {
        public EventDataWrapper(T data)
        {
            Data = data;
            Metadata = new SqsMetadata();
        }

        public SqsMetadata Metadata { get; set; }

        public T Data { get; set; }
    }

    public class SqsMetadata
    {
        public SqsMetadata()
        {
            SentAt = DateTime.Now;
            ServiceName = Environment.GetEnvironmentVariable("SERVICE_NAME");
            SentBy = $"com.{Environment.GetEnvironmentVariable("ENV")}.order-api";
        }

        public string SentBy { get; set; }

        public string ServiceName { get; set; }

        public DateTime SentAt { get; set; }
    }
}
