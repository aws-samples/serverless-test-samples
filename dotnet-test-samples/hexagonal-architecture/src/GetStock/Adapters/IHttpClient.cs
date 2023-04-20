namespace GetStock.Adapters;

public interface IHttpClient : IDisposable
{
    Task<string> GetAsync(string url);
}