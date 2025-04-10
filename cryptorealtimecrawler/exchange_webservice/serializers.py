from rest_framework import serializers
from .models import (
    Crypto, ExchangeSymbol, CMCMarketData, CMCTag, CMCCryptoTag,
    DailyPrice, FiveMinutePrice, FifteenMinutePrice, OneHourPrice, FourHourPrice
)


class CryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crypto
        fields = '__all__'


class ExchangeSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeSymbol
        fields = '__all__'


class CMCMarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMCMarketData
        fields = '__all__'


class CMCTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMCTag
        fields = '__all__'


class CMCCryptoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMCCryptoTag
        fields = '__all__'


class HistoricalPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrice
        fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'indicators'] 