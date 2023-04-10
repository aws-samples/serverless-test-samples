from decimal import Decimal
from src.ports import CurrenciesService

from src.ports import StocksService

currencies = ["USD", "CAD", "AUD"]

def retrieveStockValues(stockID):
    try:
        stockValue = StocksService.getStockData(stockID)
        currencyList = CurrenciesService.getCurrenciesData(currencies)
        print("STOCK VALUE", stockValue)
        print("CURRENCY LIST", currencyList)
        
        stockWithCurrencies = {
            "stock": stockValue["Item"]["STOCK_ID"],
            "values": {
                "EUR": float(stockValue["Item"]["Value"])
            }
        }
        print(stockWithCurrencies)
        for currency in currencies:
            print(currencyList[currency])
            stockWithCurrencies["values"][currency] =  float(Decimal(stockValue["Item"]["Value"]) * currencyList[currency])
        print(stockWithCurrencies)
        return stockWithCurrencies
    except ValueError as e:
        print(e)
        raise