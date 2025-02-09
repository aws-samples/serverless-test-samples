"""
Stock Service Port
"""
from src.adapters import stocks_db

def get_stock_data(stock_id):
    """
    get_stock_data: Retrieve a stock from the stock db adapter
    """
    try:
        data = stocks_db.get_stock_value(stock_id)
        return data
    except Exception as err:
        print("get_stock_data Error:" + str(err) + " : " + str(type(err)))
        raise err
    