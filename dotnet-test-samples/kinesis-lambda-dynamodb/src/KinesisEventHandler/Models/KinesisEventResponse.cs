using System.Collections.Generic;
using System.Runtime.Serialization;
using System.Text.Json.Serialization;

namespace KinesisEventHandler.Models;

/// <summary>
/// This class is used as the return type for AWS Lambda functions that are invoked by Kinesis to report batch item failures.
/// </summary>
[DataContract]
public class KinesisEventResponse
{
    /// <summary>
    /// A list of records which failed processing. Returning the first record which failed would retry all remaining records from the batch.
    /// </summary>
    [DataMember(EmitDefaultValue = false, Name = "batchItemFailures")]
    [JsonPropertyName("batchItemFailures")]
    public IList<BatchItemFailure> BatchItemFailures { get; set; }

    /// <summary>The class representing the BatchItemFailure.</summary>
    [DataContract]
    public class BatchItemFailure
    {
        /// <summary>
        /// Sequence number of the record which failed processing.
        /// </summary>
        [DataMember(EmitDefaultValue = false, Name = "itemIdentifier")]
        [JsonPropertyName("itemIdentifier")]
        public string ItemIdentifier { get; set; }
    }
}