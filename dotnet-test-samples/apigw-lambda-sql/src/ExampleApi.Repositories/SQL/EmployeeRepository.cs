using System.Data;
using System.Data.SqlClient;
using AWS.Lambda.Powertools.Tracing;
using Microsoft.Extensions.Options;
using Dapper;
using ExampleApi.Repositories.Helpers;
using ExampleApi.Repositories.Mappers;
using ExampleApi.Repositories.Models;

namespace ExampleApi.Repositories.Sql
{
    [Tracing(SegmentName = "EmployeeRepository")]
    public class EmployeeRepository : IEmployeeRepository
    {
        private readonly string _sqlConnection;

        public EmployeeRepository(IOptions<SqlServerOptions> options)
        {
            _sqlConnection = SecretsManagerHelper
                .GetSecretValue(options.Value.SqlConnectionStringSecretName).Result;
            if (_sqlConnection == null)
                throw new ArgumentNullException("Connection string argument is empty");
        }

        public Task<EmployeeDto> GetEmployee(string employeeId, CancellationToken token)
        {
            using IDbConnection connection = new SqlConnection(_sqlConnection);

            connection.QueryAsync("", token);

            return Task.FromResult(new EmployeeDto(employeeId, "", "", "", DateTime.Now, DateTime.Now));
        }

        public Task<UpsertResult> PutEmployee(EmployeeDto employeeDto, CancellationToken token)
        {
            using IDbConnection connection = new SqlConnection(_sqlConnection);

            connection.ExecuteAsync("", token);

            return Task.FromResult(UpsertResult.Inserted);
        }
    }
}