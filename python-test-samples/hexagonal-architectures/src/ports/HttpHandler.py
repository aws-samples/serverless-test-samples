from src.domains import stock

def retrieveStock(stockID):
    try:
        stockWithCurrencies = stock.retrieveStockValues(stockID)
        return stockWithCurrencies
    except Exception as e:
        print("retrieveStock Error:" + str(e) + " : " + str(type(e)))
        raise e