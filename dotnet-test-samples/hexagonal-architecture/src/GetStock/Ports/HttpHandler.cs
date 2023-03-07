using HexagonalArchitecture.Domains;

namespace HexagonalArchitecture.Ports
{
    public interface IHttpHandler
    {
        Task<StockWithCurrencies> RetrieveStockValues(string stockId);
    }

    internal class HttpHandler : IHttpHandler
    {
        private readonly StockLogic _stockLogic;

        public HttpHandler(StockLogic stockLogic)
        {
            _stockLogic = stockLogic;
        }

        public async Task<StockWithCurrencies> RetrieveStockValues(string stockId)
        {
            var stockValue = await _stockLogic.RetrieveStockValues(stockId);

            return stockValue;
        }
    }
}
