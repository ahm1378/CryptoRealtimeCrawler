from typing import List, Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    Crypto, ExchangeSymbol, CMCMarketData, CMCTag, CMCCryptoTag,
    DailyPrice, FiveMinutePrice, FifteenMinutePrice, OneHourPrice, FourHourPrice
)
from .selectors import (
    get_crypto, get_crypto_list, get_crypto_market_data,
    get_crypto_tags, get_exchange_symbols
)


@transaction.atomic
def create_crypto(
    name: str,
    full_name: str,
    cmc_id: int,
    is_main: bool = False
) -> Crypto:
    """Create a new cryptocurrency"""
    return Crypto.objects.create(
        name=name,
        full_name=full_name,
        cmc_id=cmc_id,
        is_main=is_main
    )


@transaction.atomic
def update_crypto(
    crypto: Crypto,
    name: Optional[str] = None,
    full_name: Optional[str] = None,
    is_main: Optional[bool] = None
) -> Crypto:
    """Update cryptocurrency information"""
    if name:
        crypto.name = name
    if full_name:
        crypto.full_name = full_name
    if is_main is not None:
        crypto.is_main = is_main
    
    crypto.save()
    return crypto


@transaction.atomic
def create_cmc_market_data(
    crypto: Crypto,
    cmc_rank: int,
    max_supply: Optional[float] = None,
    circulating_supply: Optional[float] = None,
    total_supply: Optional[float] = None,
    infinite_supply: bool = False,
    num_market_pairs: int = 0,
    last_updated: Optional[str] = None
) -> CMCMarketData:
    """Create CMC market data for a cryptocurrency"""
    return CMCMarketData.objects.create(
        crypto=crypto,
        cmc_rank=cmc_rank,
        max_supply=max_supply,
        circulating_supply=circulating_supply,
        total_supply=total_supply,
        infinite_supply=infinite_supply,
        num_market_pairs=num_market_pairs,
        last_updated=last_updated
    )


@transaction.atomic
def update_cmc_market_data(
    market_data: CMCMarketData,
    cmc_rank: Optional[int] = None,
    max_supply: Optional[float] = None,
    circulating_supply: Optional[float] = None,
    total_supply: Optional[float] = None,
    infinite_supply: Optional[bool] = None,
    num_market_pairs: Optional[int] = None,
    last_updated: Optional[str] = None
) -> CMCMarketData:
    """Update CMC market data"""
    if cmc_rank is not None:
        market_data.cmc_rank = cmc_rank
    if max_supply is not None:
        market_data.max_supply = max_supply
    if circulating_supply is not None:
        market_data.circulating_supply = circulating_supply
    if total_supply is not None:
        market_data.total_supply = total_supply
    if infinite_supply is not None:
        market_data.infinite_supply = infinite_supply
    if num_market_pairs is not None:
        market_data.num_market_pairs = num_market_pairs
    if last_updated is not None:
        market_data.last_updated = last_updated
    
    market_data.save()
    return market_data


@transaction.atomic
def create_exchange_symbol(
    crypto: Crypto,
    exchange: str,
    symbol: str,
    is_active: bool = True
) -> ExchangeSymbol:
    """Create a new exchange symbol"""
    return ExchangeSymbol.objects.create(
        crypto=crypto,
        exchange=exchange,
        symbol=symbol,
        is_active=is_active
    )


@transaction.atomic
def update_exchange_symbol(
    exchange_symbol: ExchangeSymbol,
    symbol: Optional[str] = None,
    is_active: Optional[bool] = None
) -> ExchangeSymbol:
    """Update exchange symbol information"""
    if symbol:
        exchange_symbol.symbol = symbol
    if is_active is not None:
        exchange_symbol.is_active = is_active
    
    exchange_symbol.save()
    return exchange_symbol


@transaction.atomic
def create_cmc_tag(name: str) -> CMCTag:
    """Create a new CMC tag"""
    return CMCTag.objects.create(name=name)


@transaction.atomic
def add_crypto_tag(crypto: Crypto, tag: CMCTag) -> CMCCryptoTag:
    """Add a tag to a cryptocurrency"""
    return CMCCryptoTag.objects.create(crypto=crypto, tag=tag)


@transaction.atomic
def remove_crypto_tag(crypto: Crypto, tag: CMCTag) -> None:
    """Remove a tag from a cryptocurrency"""
    CMCCryptoTag.objects.filter(crypto=crypto, tag=tag).delete()


@transaction.atomic
def save_historical_price(
    crypto: Crypto,
    timeframe: str,
    timestamp: int,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    volume: float,
    indicators: Optional[Dict[str, Any]] = None
) -> None:
    """Save historical price data"""
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
    
    model_class.objects.create(
        crypto=crypto,
        timestamp=timestamp,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=volume,
        indicators=indicators
    )


@transaction.atomic
def bulk_save_historical_prices(
    crypto: Crypto,
    timeframe: str,
    price_data: List[Dict[str, Any]]
) -> None:
    """Bulk save historical price data"""
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
    
    # Delete existing data for this crypto and timeframe
    model_class.objects.filter(crypto=crypto).delete()
    
    # Prepare data for bulk create
    records = []
    for data in price_data:
        records.append(
            model_class(
                crypto=crypto,
                timestamp=data['timestamp'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                volume=data['volume'],
                indicators=data.get('indicators')
            )
        )
    
    # Bulk create records
    if records:
        model_class.objects.bulk_create(records, batch_size=1000) 