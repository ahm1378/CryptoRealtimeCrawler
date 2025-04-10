import pandas as pd
import ccxt


class ExchangeConnector:
    Exchanges = ['bingx', 'xt', 'lbank', 'coinex']
    _instance = None

    def __new__(cls, api_keys: dict, api_secrets: dict):
        if cls._instance is None:

            cls._instance = super(ExchangeConnector, cls).__new__(cls)

            cls._instance.connector = {}

            for exchange in ExchangeConnector.Exchanges:
                exchange_class = getattr(ccxt, exchange)
                cls._instance.connector[exchange] = exchange_class({
                'apiKey': api_keys[exchange],
                'apiSecret': api_secrets[exchange],
            })

        return cls._instance

    def get_symbols_realtime_data(self, exchange: str,
                        market_type: str = 'spot',
                        *args, **kwargs):
        return self.connector[exchange].fetch_tickers(params = {'type': market_type})

    def get_order_book_data(self, symbol: str, limit: str, exchange: str, **params):
        order_book_data = self.connector[exchange].fetch_order_book(symbol = symbol, limit = limit, **params)
        order_book_data['exchnage'] = exchange

        return order_book_data

    def get_ohlcv_data(self, symbol: str, timeframe: str, limit: int, 
                       exchange: str, start: str = None, end: str = None,
                       paginate: bool = False, pagination_calls: int = 10, *args, **kwargs):

        start_timestamp = int(pd.to_datetime(start).timestamp() * 1000) if start is not None else None
        end_timestamp = int(pd.to_datetime(end).timestamp() * 1000) if end is not None else None

        ohlcv_data = self.connector[exchange].fetch_ohlcv(symbol = symbol, timeframe = timeframe, limit = limit,
                                                          since = start_timestamp, params = {"until": end_timestamp,
                                                                                            "paginate": paginate,
                                                                                            "paginationCalls": pagination_calls})
  
        return ohlcv_data


