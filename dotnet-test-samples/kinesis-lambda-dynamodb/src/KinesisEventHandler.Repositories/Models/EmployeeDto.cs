namespace KinesisEventHandler.Repositories.Models;

public record EmployeeDto(
    string EmployeeId,
    string Email,
    string FirstName,
    string LastName,
    DateTime DateOfBirth,
    DateTime DateOfHire
)
{
    public string EmployeeId { get; } = EmployeeId;
    public string Email { get; } = Email;
    public string FirstName { get; } = FirstName;
    public string LastName { get; } = LastName;
    public DateTime DateOfBirth { get; } = DateOfBirth;
    public DateTime DateOfHire { get; } = DateOfHire;
}