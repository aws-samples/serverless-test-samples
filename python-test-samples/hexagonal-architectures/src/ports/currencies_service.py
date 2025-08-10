"""
Currency Exchange DB Port
"""
from src.adapters import currency_exchange_db

def get_currencies_data(currencies):
    """
    get_currencies_data: Retrieve Currencies
    """
    try:
        data = currency_exchange_db.get_currencies(currencies)
        return data
    except Exception as err:
        print("get_currencies_data Error:" + str(err) + " : " + str(type(err)))
        raise err
    