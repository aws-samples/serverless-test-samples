from src.ports import HttpHandler
import json

def getStocksRequest(stockID):
    try:
        stockData = HttpHandler.retrieveStock(stockID)
        print("Stock Data", stockData)
        response = {
        'statusCode': 200,
            'body': json.dumps({
                "message": stockData,
            })
        }
        return response
    except Exception as e:
        print(e)
        raise
