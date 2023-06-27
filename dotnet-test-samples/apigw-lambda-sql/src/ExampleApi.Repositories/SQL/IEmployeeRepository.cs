using ExampleApi.Repositories.Mappers;
using ExampleApi.Repositories.Models;

namespace ExampleApi.Repositories.Sql
{
    public interface IEmployeeRepository
    {
        Task<EmployeeDto> GetEmployee(string employeeId, CancellationToken token);
        Task<UpsertResult> PutEmployee(EmployeeDto employeeDto, CancellationToken token);
    }
}
