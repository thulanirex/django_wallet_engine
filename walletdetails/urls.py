
from django.contrib import admin
from django.urls import path, include
from .views import  WalletBalanceView,WalletTransactionView,ResourceUsage

urlpatterns = [
    path('getBalance', WalletBalanceView.as_view(), name='walletbalance'),
    path('getTransaction', WalletTransactionView.as_view(), name='transactions'),
    path('transferFund', WalletTransactionView.as_view(), name='fundtransfer'),
    path('getResourceUsage', ResourceUsage.as_view(), name='apiusage'),
]
