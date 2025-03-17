"""
Stock Domain
"""
from decimal import Decimal
from src.ports import currencies_service
from src.ports import stocks_service

currencies = ["USD", "CAD", "AUD"]


def retrieve_stock_values(stock_id):
    """
    retrieve_stock_values: fetch stock in multiple currencies
    """
    try:
        stock_value = stocks_service.get_stock_data(stock_id)
        currency_list = currencies_service.get_currencies_data(currencies)
        print("STOCK VALUE", stock_value)
        print("CURRENCY LIST", currency_list)

        stock_with_currencies = {
            "stock": stock_value["Item"]["STOCK_ID"],
            "values": {
                "EUR": float(stock_value["Item"]["Value"])
            }
        }
        for currency in currencies:
            stock_with_currencies["values"][currency] = \
                float(Decimal(stock_value["Item"]["Value"]) * currency_list[currency])
        return stock_with_currencies
    except ValueError as err:
        print("retrieve_stock_values Error:" + str(err) + " : " + str(type(err)))
        raise err
    