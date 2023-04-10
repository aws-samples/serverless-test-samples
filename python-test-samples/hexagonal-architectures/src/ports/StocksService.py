from src.adapters import StocksDB

def getStockData(stockID):
    try:
        data = StocksDB.getStockValue(stockID)
        return data
    except Exception as e:
        print(e)
        raise