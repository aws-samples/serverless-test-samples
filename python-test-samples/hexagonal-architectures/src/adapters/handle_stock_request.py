"""
Stock Request DB Adapter
"""
import json
from src.ports import http_handler

def get_stocks_request(stock_id):
    """
    get_stocks_request - retrieve a stock from the DB
    """
    try:
        stock_data = http_handler.retrieve_stock(stock_id)
        print("Stock Data", stock_data)
        response = {
        'statusCode': 200,
            'body': json.dumps({
                "message": stock_data,
            })
        }
        return response
    except Exception as err:
        print("get_stocks_request Error:" + str(err) + " : " + str(type(err)))
        raise err
