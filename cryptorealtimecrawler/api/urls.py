from django.urls import path, include

urlpatterns = [
    path('users/', include(('cryptorealtimecrawler.users.urls', 'users'))),
    path('auth/', include(('cryptorealtimecrawler.authentication.urls', 'auth'))),
    path('exchange-webservice/', include(('cryptorealtimecrawler.exchange_webservice.urls', 'exchange_webservice'))),
]
