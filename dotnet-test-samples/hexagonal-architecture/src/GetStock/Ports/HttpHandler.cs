using HexagonalArchitecture.Domains;

namespace HexagonalArchitecture.Ports
{
    internal class HttpHandler
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
