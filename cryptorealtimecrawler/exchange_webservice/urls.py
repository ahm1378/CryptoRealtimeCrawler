from django.urls import path
from .apis import (
    CryptoViewSet, ExchangeSymbolViewSet, CMCTagViewSet,
    MarketDataViewSet, HistoricalPriceViewSet
)

urlpatterns = [
    # Crypto endpoints
    path('cryptos/', CryptoViewSet.as_view({'get': 'list', 'post': 'create'}), name='crypto-list'),
    path('cryptos/<int:pk>/', CryptoViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='crypto-detail'),
    path('cryptos/<int:pk>/market-data/', CryptoViewSet.as_view({'get': 'market_data'}), name='crypto-market-data'),
    path('cryptos/<int:pk>/tags/', CryptoViewSet.as_view({'get': 'tags'}), name='crypto-tags'),
    path('cryptos/<int:pk>/exchange-symbols/', CryptoViewSet.as_view({'get': 'exchange_symbols'}), name='crypto-exchange-symbols'),
    path('cryptos/<int:pk>/historical-prices/', CryptoViewSet.as_view({'get': 'historical_prices'}), name='crypto-historical-prices'),
    path('cryptos/<int:pk>/price-statistics/', CryptoViewSet.as_view({'get': 'price_statistics'}), name='crypto-price-statistics'),
    path('cryptos/<int:pk>/price-changes/', CryptoViewSet.as_view({'get': 'price_changes'}), name='crypto-price-changes'),

    # Exchange Symbol endpoints
    path('exchange-symbols/', ExchangeSymbolViewSet.as_view({'get': 'list', 'post': 'create'}), name='exchange-symbol-list'),
    path('exchange-symbols/<int:pk>/', ExchangeSymbolViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='exchange-symbol-detail'),

    # CMC Tag endpoints
    path('cmc-tags/', CMCTagViewSet.as_view({'get': 'list', 'post': 'create'}), name='cmc-tag-list'),
    path('cmc-tags/<int:pk>/', CMCTagViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='cmc-tag-detail'),
    path('cmc-tags/<int:pk>/add-to-crypto/', CMCTagViewSet.as_view({'post': 'add_to_crypto'}), name='cmc-tag-add-to-crypto'),
    path('cmc-tags/<int:pk>/remove-from-crypto/', CMCTagViewSet.as_view({'post': 'remove_from_crypto'}), name='cmc-tag-remove-from-crypto'),

    # Market Data endpoints
    path('market-data/', MarketDataViewSet.as_view({'get': 'list', 'post': 'create'}), name='market-data-list'),
    path('market-data/<int:pk>/', MarketDataViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='market-data-detail'),

    # Historical Price endpoints
    path('historical-prices/top-by-volume/', HistoricalPriceViewSet.as_view({'get': 'top_by_volume'}), name='historical-prices-top-by-volume'),
    path('historical-prices/bulk-save/', HistoricalPriceViewSet.as_view({'post': 'bulk_save'}), name='historical-prices-bulk-save'),
] 