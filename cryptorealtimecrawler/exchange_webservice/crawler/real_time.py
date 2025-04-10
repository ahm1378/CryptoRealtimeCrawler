import abc
import time
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from django.db import transaction

from cryptorealtimecrawler.common.redis_db_connection import RedisConnection
from cryptorealtimecrawler.exchange_webservice.crawler.connector import ExchangeConnector
from cryptorealtimecrawler.exchange_webservice.crawler.cmc_crawler import CMCCrawler
from cryptorealtimecrawler.utils.shared_utils import SharedUtils as su
from cryptorealtimecrawler.exchange_webservice.crawler.redis_keys import Coin_REDIS_KEY
from cryptorealtimecrawler.exchange_webservice.models import (
    Crypto, ExchangeSymbol, CMCMarketData, CMCTag, CMCCryptoTag,
    DailyPrice, FiveMinutePrice, FifteenMinutePrice, OneHourPrice, FourHourPrice
)
from cryptorealtimecrawler.utils.crawler.crawler import get_start_time
from config.settings.exchange import API_KEYS, API_SECRETS
from config.settings.redis import REDIS_COINS_HOST, REDIS_COINS_PORT


class BaseCrawler(abc.ABC):
    """Base class for all crawlers with common functionality"""
    
    def __init__(self):
        self._log = su.initialize_log(log_file='tradefai_backend/coin_crawler/logs/events.log')
        self.redis_handler = RedisConnection(host=REDIS_COINS_HOST, port=REDIS_COINS_PORT)
        self.cmc_crawler = CMCCrawler(api_key=API_KEYS['cmc'])
        self.exchange_connector = ExchangeConnector(api_keys=API_KEYS, api_secrets=API_SECRETS)
    
    @abc.abstractmethod
    def get_since_time_frame(self) -> Tuple[Optional[int], str]:
        """Get the since timestamp and timeframe for the crawler"""
        pass
    
    @abc.abstractmethod
    def get_redis_key(self) -> str:
        """Get the Redis key for storing data"""
        pass
    
    def _handle_error(self, message: str, error: Exception) -> None:
        """Handle errors with proper logging"""
        self._log.error(f"{message}: {str(error)}")


class CoinHandler(BaseCrawler):
    """Handler for cryptocurrency data operations"""
    
    Exchanges = ExchangeConnector.Exchanges
    Coins_Limit = 500
    
    def get_save_cmc_coins_data(self) -> None:
        """Fetch and save CMC coins data"""
        try:
            cmc_coins_data = su.retry(self.cmc_crawler.get_cmc_coins_data)
            if isinstance(cmc_coins_data, dict):
                self.redis_handler.set(Coin_REDIS_KEY.CMC_COINS_DATA.value, cmc_coins_data)
                self._save_cmc_coins_to_database(cmc_coins_data)
        except Exception as e:
            self._handle_error("Failed to get CMC coins data", e)
    
    def get_cleaned_cmc_coins_data(self) -> Dict:
        """Get cleaned CMC coins data from Redis"""
        cmc_coins_data = self.redis_handler.get(Coin_REDIS_KEY.CMC_COINS_DATA.value)
        return self.cmc_crawler.remove_stablecoins(cmc_coins_data)
    
    def get_all_exchanges_realtime_data(self) -> Dict[str, Dict]:
        """Get realtime data from all exchanges"""
        symbols_data = {}
        
        for exchange in self.Exchanges:
            try:
                exchange_symbols_data = su.retry(
                    self.exchange_connector.get_symbols_realtime_data,
                    exchange=exchange
                )
                symbols_data[exchange] = exchange_symbols_data
            except Exception as e:
                self._handle_error(f"Failed to get symbols realtime data for exchange {exchange}", e)
        
        return symbols_data
    
    def get_save_tf_coins_data(self) -> None:
        """Get and save TF coins data"""
        try:
            cmc_coins_data = self.get_cleaned_cmc_coins_data()
            tickers_json_data = self.get_all_exchanges_realtime_data()
            
            tf_coins_data = self._prepare_tf_coins_dataframe(cmc_coins_data)
            tf_coins_data = self._process_exchange_data(tf_coins_data, tickers_json_data)
            tf_coins_data = self._remove_tf_coins_data_duplicates(tf_coins_data)
            
            tf_coins_data.drop(['symbol_usdt', 'name_usdt'], axis=1, inplace=True)
            tf_coins_data.dropna(subset=self.Exchanges, how='all', inplace=True)
            
            self._save_tf_coins_to_database(tf_coins_data)
        except Exception as e:
            self._handle_error("Failed to save TF coins data", e)
    
    def _prepare_tf_coins_dataframe(self, cmc_coins_data: Dict) -> pd.DataFrame:
        """Prepare the initial TF coins DataFrame"""
        tf_coins_data = (
            pd.json_normalize(cmc_coins_data.get('data'))
            .loc[:, ['id', 'symbol', 'name']]
            .set_index('id')
        )
        
        platforms = {
            coin_data.get('platform', {}).get('symbol')
            for coin_data in cmc_coins_data.get('data')
            if coin_data.get('platform') is not None
        }
        
        tf_coins_data['symbol_usdt'] = tf_coins_data['symbol'] + '/USDT'
        tf_coins_data['name_usdt'] = tf_coins_data['name'].str.upper() + '/USDT'
        tf_coins_data['is_main'] = tf_coins_data['symbol'].isin(platforms)
        
        return tf_coins_data
    
    def _process_exchange_data(self, tf_coins_data: pd.DataFrame, tickers_json_data: Dict) -> pd.DataFrame:
        """Process exchange data and update DataFrame"""
        for exchange in self.Exchanges:
            tickers_set = set(tickers_json_data.get(exchange, {}).keys())
            tf_coins_data[exchange] = np.nan
            tf_coins_data[exchange] = tf_coins_data[exchange].astype(object)
            
            symbol_match = tf_coins_data['symbol_usdt'].isin(tickers_set)
            name_match = tf_coins_data['name_usdt'].isin(tickers_set) & ~symbol_match
            
            tf_coins_data.loc[symbol_match, exchange] = tf_coins_data.loc[symbol_match, 'symbol_usdt']
            tf_coins_data.loc[name_match, exchange] = tf_coins_data.loc[name_match, 'name_usdt']
        
        return tf_coins_data
    
    def _remove_tf_coins_data_duplicates(self, tf_coins_data: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates in exchange columns"""
        for exchange in self.Exchanges:
            tf_coins_data.loc[
                tf_coins_data.duplicated(subset=exchange, keep='first'),
                exchange
            ] = np.nan
        return tf_coins_data
    
    @transaction.atomic
    def _save_tf_coins_to_database(self, tf_coins_data: pd.DataFrame) -> None:
        """Save TF coins data to database"""
        Crypto.objects.all().delete()
        ExchangeSymbol.objects.all().delete()
        
        for index, row in tf_coins_data.reset_index().iterrows():
            crypto = Crypto.objects.create(
                cmc_id=row['id'],
                name=row['symbol'],
                full_name=row['name'],
                is_main=row['is_main']
            )
            
            for exchange in self.Exchanges:
                if pd.notna(row[exchange]):
                    ExchangeSymbol.objects.create(
                        crypto=crypto,
                        exchange=exchange,
                        symbol=row[exchange]
                    )
    
    @transaction.atomic
    def _save_cmc_coins_to_database(self, cmc_coins_data: Dict) -> None:
        """Save CMC coins data to database"""
        CMCMarketData.objects.all().delete()
        CMCTag.objects.all().delete()
        CMCCryptoTag.objects.all().delete()
        
        for coin_data in cmc_coins_data.get('data', []):
            crypto = Crypto.objects.get(cmc_id=coin_data.get('id'))
            
            CMCMarketData.objects.create(
                crypto=crypto,
                cmc_rank=coin_data.get('cmc_rank'),
                max_supply=coin_data.get('max_supply'),
                circulating_supply=coin_data.get('circulating_supply'),
                total_supply=coin_data.get('total_supply'),
                infinite_supply=coin_data.get('infinite_supply', False),
                num_market_pairs=coin_data.get('num_market_pairs', 0),
                last_updated=coin_data.get('last_updated')
            )
            
            # Save tags
            for tag_name in coin_data.get('tags', []):
                tag, _ = CMCTag.objects.get_or_create(name=tag_name)
                CMCCryptoTag.objects.create(crypto=crypto, tag=tag)
            
            self.redis_handler.set(f"{coin_data.get('symbol')}_CMCData", coin_data)
    
    def get_save_realtime_data(self) -> int:
        """Get and save realtime data"""
        try:
            tickers_json_data = self.get_all_exchanges_realtime_data()
            tf_coins_data = self._load_coins_data_from_database()
            real_time_data = {}
            error_symbols = set()
            
            tf_exchange_symbols = tf_coins_data.loc[:, self.Exchanges]
            
            for coin_id, exchange_symbols in tf_exchange_symbols.iterrows():
                coin_symbol = tf_coins_data.loc[coin_id, 'symbol']
                
                for exchange, symbol in exchange_symbols.dropna().items():
                    try:
                        symbol_data = tickers_json_data.get(exchange, {}).get(symbol)
                        if symbol_data:
                            symbol_data['exchange'] = exchange
                            real_time_data[coin_symbol] = symbol_data
                            self.redis_handler.set(f'{coin_symbol}_RealTime', symbol_data)
                            break
                    except Exception as e:
                        self._handle_error(f'Failed to get realtime data for {coin_symbol} from {exchange}', e)
                        error_symbols.add(coin_symbol)
            
            if real_time_data:
                self.redis_handler.set(Coin_REDIS_KEY.REAL_TIME_DATA.value, real_time_data)
            
            return len(error_symbols)
        except Exception as e:
            self._handle_error("Failed to save realtime data", e)
            return 0
    
    def _load_coins_data_from_database(self) -> pd.DataFrame:
        """Load coins data from database"""
        query_set = Crypto.objects.all()
        query_data = list(query_set.values())
        tf_coins_data = pd.DataFrame(query_data)
        
        exchange_symbols = ExchangeSymbol.objects.all()
        for exchange in self.Exchanges:
            tf_coins_data[exchange] = np.nan
            for symbol in exchange_symbols.filter(exchange=exchange):
                tf_coins_data.loc[tf_coins_data['cmc_id'] == symbol.crypto.cmc_id, exchange] = symbol.symbol
        
        return tf_coins_data.replace("nan", np.nan)
    
    def get_save_orderbook_data(self, limit: int = 500) -> int:
        """Get and save orderbook data"""
        try:
            tf_coins_data = self._load_coins_data_from_database()
            order_book_data = {}
            error_symbols = set()
            
            tf_exchange_symbols = tf_coins_data.loc[:, self.Exchanges]
            
            for coin_id, exchange_symbols in tf_exchange_symbols.iloc[:self.Coins_Limit].iterrows():
                coin_symbol = tf_coins_data.loc[coin_id, 'name']
                
                for exchange, symbol in exchange_symbols.dropna().items():
                    try:
                        symbol_order_book_data = su.retry(
                            self.exchange_connector.get_order_book_data,
                            symbol=symbol,
                            limit=limit if exchange != 'coinex' else None,
                            exchange=exchange
                        )
                        
                        if symbol_order_book_data is not None:
                            order_book_data[coin_symbol] = symbol_order_book_data
                            break
                    except Exception as e:
                        self._handle_error(f'Failed to get orderbook data for {coin_symbol}', e)
                        error_symbols.add(coin_symbol)
                        time.sleep(5)
                time.sleep(0.1)
            
            self.redis_handler.set(Coin_REDIS_KEY.ORDER_BOOK_DATA.value, order_book_data)
            return len(error_symbols)
        except Exception as e:
            self._handle_error("Failed to save orderbook data", e)
            return 0
    
    def get_all_coins_ohlcv_data(self, timeframe: str, limit: int) -> Tuple[Dict, Set]:
        """Get OHLCV data for all coins"""
        try:
            tf_coins_data = self._load_coins_data_from_database()
            ohlcv_data = {}
            error_symbols = set()
            
            tf_exchange_symbols = tf_coins_data.loc[:, self.Exchanges]
            
            for coin_id, exchange_symbols in tf_exchange_symbols.iloc[:self.Coins_Limit].iterrows():
                coin_symbol = tf_coins_data.loc[coin_id, 'name']
                crypto = Crypto.objects.get(name=coin_symbol)
                
                for exchange, symbol in exchange_symbols.dropna().items():
                    try:
                        symbol_ohlcv_data = su.retry(
                            self.exchange_connector.get_ohlcv_data,
                            symbol=symbol,
                            timeframe=timeframe,
                            limit=limit,
                            exchange=exchange
                        )
                        
                        if symbol_ohlcv_data and isinstance(symbol_ohlcv_data, list):
                            ohlcv_data[coin_symbol] = symbol_ohlcv_data
                            self.redis_handler.set(f"{coin_symbol}_{timeframe}", symbol_ohlcv_data)
                            self._save_ohlcv_to_database(crypto, symbol_ohlcv_data, timeframe)
                            
                        if self.redis_handler.get(f"{coin_symbol}_{timeframe}"):
                            break
                    except Exception as e:
                        self._handle_error(f'Failed to get OHLCV {timeframe} data for {coin_symbol} from {exchange}', e)
                        error_symbols.add(f'{exchange}_{coin_symbol}')
                time.sleep(0.1)
            
            return ohlcv_data, error_symbols
        except Exception as e:
            self._handle_error("Failed to get OHLCV data", e)
            return {}, set()
    
    @transaction.atomic
    def _save_ohlcv_to_database(self, crypto: Crypto, ohlcv_data: List[List], timeframe: str) -> None:
        """Save OHLCV data to the appropriate database table"""
        # Map timeframe to model class
        timeframe_model_map = {
            '5m': FiveMinutePrice,
            '15m': FifteenMinutePrice,
            '1h': OneHourPrice,
            '4h': FourHourPrice,
            '1d': DailyPrice
        }
        
        model_class = timeframe_model_map.get(timeframe)
        if not model_class:
            self._handle_error(f"Invalid timeframe: {timeframe}", ValueError(f"Invalid timeframe: {timeframe}"))
            return
        
        # Delete existing data for this crypto and timeframe
        model_class.objects.filter(crypto=crypto).delete()
        
        # Prepare data for bulk create
        records = []
        for data in ohlcv_data:
            if len(data) >= 6:  # Ensure we have all required fields
                records.append(
                    model_class(
                        crypto=crypto,
                        timestamp=data[0],  # Unix timestamp
                        open=data[1],      # Open price
                        high=data[2],      # High price
                        low=data[3],       # Low price
                        close=data[4],     # Close price
                        volume=data[5]     # Volume
                    )
                )
        
        # Bulk create records
        if records:
            model_class.objects.bulk_create(records, batch_size=1000)
    
    def run_save_ohlcv_redis(self) -> int:
        """Run and save OHLCV data to Redis"""
        try:
            since, timeframe = self.get_since_time_frame()
            ohlcv_data, error_symbols = self.get_all_coins_ohlcv_data(
                timeframe=timeframe,
                limit=201
            )
            
            if ohlcv_data:
                redis_key = self.get_redis_key()
                self.redis_handler.set(redis_key, ohlcv_data)
            
            return len(error_symbols)
        except Exception as e:
            self._handle_error("Failed to run OHLCV crawler", e)
            return 0
    
    def get_coins_ohlcv_data(self, coins: Optional[List[str]] = None, timeframe: Optional[str] = None) -> Dict:
        """Get OHLCV data for specific coins"""
        try:
            if timeframe is None:
                _, timeframe = self.get_since_time_frame()
            
            if coins is None:
                redis_key = self.get_redis_key()
                coins = self.redis_handler.get(f"{redis_key}_coins")
                if not coins:
                    return {}
            
            redis_keys = [f"{coin}_{timeframe}" for coin in coins]
            return self.redis_handler.bulk_get(redis_keys)
        except Exception as e:
            self._handle_error("Failed to get coins OHLCV data", e)
            return {}


class TimeFrameCrawler(CoinHandler):
    """Base class for timeframe-specific crawlers"""
    
    def __init__(self, timeframe: str):
        super().__init__()
        self.timeframe = timeframe
    
    def get_since_time_frame(self) -> Tuple[Optional[int], str]:
        since = get_start_time(timeframe=self.timeframe)
        return since, self.timeframe


class FiveMinuteCrawler(TimeFrameCrawler):
    def __init__(self):
        super().__init__('5m')
    
    def get_redis_key(self) -> str:
        return Coin_REDIS_KEY.FIVE_MINUTE.value


class FifteenMinutesCrawler(TimeFrameCrawler):
    def __init__(self):
        super().__init__('15m')
    
    def get_redis_key(self) -> str:
        return Coin_REDIS_KEY.FIFTEEN_MINUTES.value


class OneHourCrawler(TimeFrameCrawler):
    def __init__(self):
        super().__init__('1h')
    
    def get_redis_key(self) -> str:
        return Coin_REDIS_KEY.ONE_HOUR.value


class FourHourCrawler(TimeFrameCrawler):
    def __init__(self):
        super().__init__('4h')
    
    def get_redis_key(self) -> str:
        return Coin_REDIS_KEY.FOUR_HOUR.value


class DailyCrawler(TimeFrameCrawler):
    def __init__(self):
        super().__init__('1d')
    
    def get_since_time_frame(self) -> Tuple[None, str]:
        return None, self.timeframe
    
    def get_redis_key(self) -> str:
        return Coin_REDIS_KEY.DAILY.value


class WeeklyCrawler(TimeFrameCrawler):
    def __init__(self):
        super().__init__('1w')
    
    def get_since_time_frame(self) -> Tuple[None, str]:
        return None, self.timeframe
    
    def get_redis_key(self) -> str:
        return Coin_REDIS_KEY.WEEKLY.value
