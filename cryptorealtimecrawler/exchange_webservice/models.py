from django.db import models
from django.core.validators import MinValueValidator

from cryptorealtimecrawler.common.models import BaseModel


class Crypto(BaseModel):
    """Base cryptocurrency information"""
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    cmc_id = models.IntegerField(unique=True, primary_key=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = 'crypto'
        verbose_name_plural = 'cryptocurrencies'

    def __str__(self):
        return f"{self.name} ({self.full_name})"


class ExchangeSymbol(BaseModel):
    """Mapping of cryptocurrency symbols across different exchanges"""
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, related_name='exchange_symbols')
    exchange = models.CharField(max_length=50)  # e.g., 'bingx', 'xt', 'lbank', 'coinex'
    symbol = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'exchange_symbol'
        unique_together = [['crypto', 'exchange']]
        indexes = [
            models.Index(fields=['exchange', 'symbol']),
        ]


class CMCMarketData(BaseModel):
    """CoinMarketCap market data for cryptocurrencies"""
    crypto = models.OneToOneField(Crypto, on_delete=models.CASCADE, related_name='cmc_data')
    cmc_rank = models.IntegerField(validators=[MinValueValidator(1)])
    max_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    circulating_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    total_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    infinite_supply = models.BooleanField(default=False)
    num_market_pairs = models.IntegerField(default=0)
    last_updated = models.DateTimeField()

    class Meta:
        db_table = 'cmc_market_data'
        verbose_name = 'CMC Market Data'


class CMCTag(BaseModel):
    """Tags associated with cryptocurrencies on CoinMarketCap"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'cmc_tag'

    def __str__(self):
        return self.name


class CMCCryptoTag(BaseModel):
    """Mapping between cryptocurrencies and their tags"""
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, related_name='cmc_tags')
    tag = models.ForeignKey(CMCTag, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cmc_crypto_tag'
        unique_together = [['crypto', 'tag']]


class HistoricalPrice(BaseModel):
    """Abstract base model for historical price data"""
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, related_name='%(class)s')
    timestamp = models.BigIntegerField()
    open = models.DecimalField(max_digits=30, decimal_places=8)
    close = models.DecimalField(max_digits=30, decimal_places=8)
    high = models.DecimalField(max_digits=30, decimal_places=8)
    low = models.DecimalField(max_digits=30, decimal_places=8)
    volume = models.DecimalField(max_digits=30, decimal_places=8)
    indicators = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True
        unique_together = [['crypto', 'timestamp']]
        indexes = [
            models.Index(fields=['crypto', 'timestamp']),
        ]


class DailyPrice(HistoricalPrice):
    """Daily historical price data"""
    class Meta:
        db_table = 'daily_price'


class FiveMinutePrice(HistoricalPrice):
    """5-minute historical price data"""
    class Meta:
        db_table = 'five_minute_price'


class FifteenMinutePrice(HistoricalPrice):
    """15-minute historical price data"""
    class Meta:
        db_table = 'fifteen_minute_price'


class OneHourPrice(HistoricalPrice):
    """1-hour historical price data"""
    class Meta:
        db_table = 'one_hour_price'


class FourHourPrice(HistoricalPrice):
    """4-hour historical price data"""
    class Meta:
        db_table = 'four_hour_price'
