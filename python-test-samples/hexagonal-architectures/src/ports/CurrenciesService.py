from src.adapters import CurrencyExchangeDB

def getCurrenciesData(currencies):
    try:
        data = CurrencyExchangeDB.getCurrencies(currencies)
        return data
    except Exception as e:
        print(e)