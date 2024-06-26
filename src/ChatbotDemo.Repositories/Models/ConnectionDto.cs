namespace ChatbotDemo.Repositories.Models;

public record ConnectionDto(string? ConnectionId)
{
    public string? ConnectionId { get; } = ConnectionId;
}