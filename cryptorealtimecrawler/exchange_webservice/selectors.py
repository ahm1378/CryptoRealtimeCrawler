from typing import List, Optional, Dict, Any
from django.db.models import Q, F, Max, Min, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Crypto, ExchangeSymbol, CMCMarketData, CMCTag, CMCCryptoTag,
    DailyPrice, FiveMinutePrice, FifteenMinutePrice, OneHourPrice, FourHourPrice
)


def get_crypto(cmc_id: Optional[int] = None, name: Optional[str] = None) -> Crypto:
    """Get a cryptocurrency by CMC ID or name"""
    query = Q()
    if cmc_id:
        query |= Q(cmc_id=cmc_id)
    if name:
        query |= Q(name=name)
    
    return Crypto.objects.get(query)


def get_crypto_list(
    is_main: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Crypto]:
    """Get list of cryptocurrencies with optional filters"""
    query = Q()
    
    if is_main is not None:
        query &= Q(is_main=is_main)
    
    if search:
        query &= (
            Q(name__icontains=search) |
            Q(full_name__icontains=search)
        )
    
    return list(Crypto.objects.filter(query)[offset:offset + limit])


def get_crypto_market_data(crypto: Crypto) -> CMCMarketData:
    """Get market data for a cryptocurrency"""
    return crypto.cmc_data


def get_crypto_tags(crypto: Crypto) -> List[CMCTag]:
    """Get tags associated with a cryptocurrency"""
    return list(crypto.cmc_tags.all())


def get_exchange_symbols(
    crypto: Optional[Crypto] = None,
    exchange: Optional[str] = None,
    is_active: bool = True
) -> List[ExchangeSymbol]:
    """Get exchange symbols with optional filters"""
    query = Q(is_active=is_active)
    
    if crypto:
        query &= Q(crypto=crypto)
    if exchange:
        query &= Q(exchange=exchange)
    
    return list(ExchangeSymbol.objects.filter(query))


def get_historical_prices(
    crypto: Crypto,
    timeframe: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """Get historical price data for a cryptocurrency"""
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
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    query = Q(crypto=crypto)
    if start_time:
        query &= Q(timestamp__gte=start_time)
    if end_time:
        query &= Q(timestamp__lte=end_time)
    
    return list(
        model_class.objects
        .filter(query)
        .order_by('-timestamp')
        .values(
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'indicators'
        )[:limit]
    )


def get_price_statistics(
    crypto: Crypto,
    timeframe: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> Dict[str, Any]:
    """Get price statistics for a cryptocurrency"""
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
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    query = Q(crypto=crypto)
    if start_time:
        query &= Q(timestamp__gte=start_time)
    if end_time:
        query &= Q(timestamp__lte=end_time)
    
    stats = model_class.objects.filter(query).aggregate(
        max_price=Max('high'),
        min_price=Min('low'),
        avg_price=Avg('close'),
        max_volume=Max('volume'),
        min_volume=Min('volume'),
        avg_volume=Avg('volume')
    )
    
    return {
        'price': {
            'max': stats['max_price'],
            'min': stats['min_price'],
            'average': stats['avg_price']
        },
        'volume': {
            'max': stats['max_volume'],
            'min': stats['min_volume'],
            'average': stats['avg_volume']
        }
    }


def get_top_cryptos_by_volume(
    timeframe: str,
    limit: int = 10,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get top cryptocurrencies by trading volume"""
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
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    query = Q()
    if start_time:
        query &= Q(timestamp__gte=start_time)
    if end_time:
        query &= Q(timestamp__lte=end_time)
    
    return list(
        model_class.objects
        .filter(query)
        .values('crypto__name', 'crypto__full_name')
        .annotate(total_volume=Avg('volume'))
        .order_by('-total_volume')[:limit]
    )


def get_crypto_price_changes(
    crypto: Crypto,
    timeframe: str,
    periods: List[int] = [1, 7, 30]
) -> Dict[str, float]:
    """Get price changes for different time periods"""
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
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    changes = {}
    for period in periods:
        end_time = int(timezone.now().timestamp() * 1000)
        start_time = end_time - (period * 24 * 60 * 60 * 1000)  # Convert days to milliseconds
        
        prices = model_class.objects.filter(
            crypto=crypto,
            timestamp__gte=start_time,
            timestamp__lte=end_time
        ).order_by('timestamp')
        
        if prices.exists():
            first_price = prices.first().close
            last_price = prices.last().close
            change = ((last_price - first_price) / first_price) * 100
            changes[f'{period}d'] = change
    
    return changes 