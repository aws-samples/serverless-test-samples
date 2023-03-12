using Amazon.Lambda.Core;
using System.Runtime.CompilerServices;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]
[assembly: InternalsVisibleTo("GetStock.UnitTest")]
[assembly: InternalsVisibleTo("GetStock.IntegrationTest")]
