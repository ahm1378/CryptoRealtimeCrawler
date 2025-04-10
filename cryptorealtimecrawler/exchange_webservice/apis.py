from typing import List, Optional, Dict, Any
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import (
    Crypto, ExchangeSymbol, CMCMarketData, CMCTag, CMCCryptoTag,
    DailyPrice, FiveMinutePrice, FifteenMinutePrice, OneHourPrice, FourHourPrice
)
from .serializers import (
    CryptoSerializer, ExchangeSymbolSerializer, CMCMarketDataSerializer,
    CMCTagSerializer, CMCCryptoTagSerializer, HistoricalPriceSerializer
)
from .services import (
    create_crypto, update_crypto, create_cmc_market_data, update_cmc_market_data,
    create_exchange_symbol, update_exchange_symbol, create_cmc_tag,
    add_crypto_tag, remove_crypto_tag, save_historical_price, bulk_save_historical_prices
)
from .selectors import (
    get_crypto, get_crypto_list, get_crypto_market_data,
    get_crypto_tags, get_exchange_symbols, get_historical_prices,
    get_price_statistics, get_top_cryptos_by_volume, get_crypto_price_changes
)


class CryptoViewSet(viewsets.ModelViewSet):
    """API endpoint for managing cryptocurrencies"""
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Crypto.objects.all()
        
        # Filter by main status
        is_main = self.request.query_params.get('is_main')
        if is_main is not None:
            queryset = queryset.filter(is_main=is_main.lower() == 'true')
        
        # Search by name or full name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(full_name__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['get'])
    def market_data(self, request, pk=None):
        """Get market data for a cryptocurrency"""
        crypto = self.get_object()
        market_data = get_crypto_market_data(crypto)
        serializer = CMCMarketDataSerializer(market_data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tags(self, request, pk=None):
        """Get tags for a cryptocurrency"""
        crypto = self.get_object()
        tags = get_crypto_tags(crypto)
        serializer = CMCTagSerializer(tags, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def exchange_symbols(self, request, pk=None):
        """Get exchange symbols for a cryptocurrency"""
        crypto = self.get_object()
        symbols = get_exchange_symbols(crypto=crypto)
        serializer = ExchangeSymbolSerializer(symbols, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historical_prices(self, request, pk=None):
        """Get historical prices for a cryptocurrency"""
        crypto = self.get_object()
        timeframe = request.query_params.get('timeframe', '1d')
        limit = int(request.query_params.get('limit', 100))
        
        prices = get_historical_prices(crypto, timeframe, limit)
        serializer = HistoricalPriceSerializer(prices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def price_statistics(self, request, pk=None):
        """Get price statistics for a cryptocurrency"""
        crypto = self.get_object()
        timeframe = request.query_params.get('timeframe', '1d')
        
        stats = get_price_statistics(crypto, timeframe)
        return Response(stats)

    @action(detail=True, methods=['get'])
    def price_changes(self, request, pk=None):
        """Get price changes for different time periods"""
        crypto = self.get_object()
        
        changes = get_crypto_price_changes(crypto)
        return Response(changes)


class ExchangeSymbolViewSet(viewsets.ModelViewSet):
    """API endpoint for managing exchange symbols"""
    queryset = ExchangeSymbol.objects.all()
    serializer_class = ExchangeSymbolSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ExchangeSymbol.objects.all()
        
        # Filter by crypto
        crypto_id = self.request.query_params.get('crypto_id')
        if crypto_id:
            queryset = queryset.filter(crypto_id=crypto_id)
        
        # Filter by exchange
        exchange = self.request.query_params.get('exchange')
        if exchange:
            queryset = queryset.filter(exchange=exchange)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class CMCTagViewSet(viewsets.ModelViewSet):
    """API endpoint for managing CMC tags"""
    queryset = CMCTag.objects.all()
    serializer_class = CMCTagSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_to_crypto(self, request, pk=None):
        """Add tag to a cryptocurrency"""
        tag = self.get_object()
        crypto_id = request.data.get('crypto_id')
        
        if not crypto_id:
            return Response(
                {'error': 'crypto_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crypto = Crypto.objects.get(id=crypto_id)
            add_crypto_tag(crypto, tag)
            return Response(status=status.HTTP_201_CREATED)
        except Crypto.DoesNotExist:
            return Response(
                {'error': 'Cryptocurrency not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_from_crypto(self, request, pk=None):
        """Remove tag from a cryptocurrency"""
        tag = self.get_object()
        crypto_id = request.data.get('crypto_id')
        
        if not crypto_id:
            return Response(
                {'error': 'crypto_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crypto = Crypto.objects.get(id=crypto_id)
            remove_crypto_tag(crypto, tag)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Crypto.DoesNotExist:
            return Response(
                {'error': 'Cryptocurrency not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarketDataViewSet(viewsets.ModelViewSet):
    """API endpoint for managing market data"""
    queryset = CMCMarketData.objects.all()
    serializer_class = CMCMarketDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CMCMarketData.objects.all()
        
        # Filter by crypto
        crypto_id = self.request.query_params.get('crypto_id')
        if crypto_id:
            queryset = queryset.filter(crypto_id=crypto_id)
        
        # Filter by rank range
        min_rank = self.request.query_params.get('min_rank')
        max_rank = self.request.query_params.get('max_rank')
        if min_rank:
            queryset = queryset.filter(cmc_rank__gte=min_rank)
        if max_rank:
            queryset = queryset.filter(cmc_rank__lte=max_rank)
        
        return queryset


class HistoricalPriceViewSet(viewsets.ViewSet):
    """API endpoint for managing historical prices"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def top_by_volume(self, request):
        """Get top cryptocurrencies by volume"""
        timeframe = request.query_params.get('timeframe', '1d')
        limit = int(request.query_params.get('limit', 10))
        
        top_cryptos = get_top_cryptos_by_volume(timeframe, limit)
        return Response(top_cryptos)

    @action(detail=False, methods=['post'])
    def bulk_save(self, request):
        """Bulk save historical prices"""
        crypto_id = request.data.get('crypto_id')
        timeframe = request.data.get('timeframe')
        price_data = request.data.get('price_data')
        
        if not all([crypto_id, timeframe, price_data]):
            return Response(
                {'error': 'crypto_id, timeframe, and price_data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crypto = Crypto.objects.get(id=crypto_id)
            bulk_save_historical_prices(crypto, timeframe, price_data)
            return Response(status=status.HTTP_201_CREATED)
        except Crypto.DoesNotExist:
            return Response(
                {'error': 'Cryptocurrency not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 