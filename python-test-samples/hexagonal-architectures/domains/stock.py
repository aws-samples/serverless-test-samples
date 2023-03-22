from ports import CurrenciesService

from ports import StocksService

currencies = ["USD", "CAD", "AUD"]

def retrieveStockValues(stockID):
    try:
        stockValue = StocksService.getStockData(stockID)
        currencyList = CurrenciesService.getCurrenciesData(currencies)
        print(stockValue)
        print(currencyList)
        stockWithCurrencies = {
            "stock": stockValue["STOCK_ID"],
            "values": {
                "EUR": stockValue["VALUE"]
            }
        }
        for currency in currencyList["rates"]:
            stockWithCurrencies["values"][currency] =  round(stockValue["VALUE"] * currencyList["rates"][currency], 3)
        
        return stockWithCurrencies
    except Exception as e:
        print(e)