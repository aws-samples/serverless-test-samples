"""
Stock Port
"""
from src.domains import stock

def retrieve_stock(stock_id):
    """
    retrieve_stock: Fetch a stock
    """
    try:
        stock_with_currencies = stock.retrieve_stock_values(stock_id)
        return stock_with_currencies
    except Exception as err:
        print("retrieve_stock Error:" + str(err) + " : " + str(type(err)))
        raise err
    