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
        for currency in currencies:
            stockWithCurrencies["values"][currency] =  float(Decimal(stockValue["Item"]["Value"]) * currencyList[currency])
        return stockWithCurrencies
    except ValueError as e:
        print("retrieveStockValues Error:" + str(e) + " : " + str(type(e)))
        raise e