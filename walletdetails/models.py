from django.db import models
from django.contrib import admin
from django_prices.models import MoneyField, TaxedMoneyField, Money
from django.utils.timezone import get_current_timezone
from django.utils import timezone
from datetime import datetime


# Create your models here.

CURRENCY_CHOICES = (
    ('ZMW', 'ZMW'),
    ('USD', 'USD')
)

TRANSACTION_TYPES = (
    ('CREDIT', 'Credited'),
    ('DEBIT', 'Debited')
)

TRANSACTION_STATUS = (
    ('SUCCESS', 'Completed Successfully'),
    ('IN_PROGRESS', 'Transaction is in Progress'),
    ('FAILED', 'Transaction failed'),('TIMEOUT','TimeOut Occured'), ('INSUFFICIENT BALANCE', 'Insufficient Balance'),
    ('INVALID_RECEIVER','Receiver is not Active')
)


class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    user_hash = models.CharField(max_length=200, unique=True)
    currency = models.CharField(max_length=5, default="ZMW", choices=CURRENCY_CHOICES , unique=True)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default="0")
    current_balance = MoneyField(amount_field="balance", currency_field="currency")
    # last_updated_time = models.DateTimeField(default=datetime.now(tz=get_current_timezone()))

    class Meta:
        db_table = "wallet"

class WalletHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user_hash = models.CharField(max_length=200, unique=True)
    currency = models.CharField(max_length=5, unique=True)
    old_balance = models.DecimalField(max_digits=9, decimal_places=2, default="0")
    previous_balance = MoneyField(amount_field="old_balance", currency_field="currency")
    new_balance = models.DecimalField(max_digits=9, decimal_places=2, default="0")
    current_balance = MoneyField(amount_field="new_balance", currency_field="currency")
    #last_updated_time = models.DateTimeField(auto_now_add=True)
    # last_updated_time = models.DateTimeField(default=datetime.now(tz=get_current_timezone()))

    class Meta:
        db_table = "wallethistory"


class WalletTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    user_hash = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_TYPES)
    transaction_status = models.CharField(max_length=30,choices=TRANSACTION_STATUS)
    recipient = models.CharField(max_length=30)
    reason = models.CharField(max_length=50 )
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default="0")
    transaction_amount = MoneyField(amount_field="amount", currency_field="currency")
    # transaction_date =models.DateTimeField(default=datetime.now(tz=get_current_timezone()))

    class Meta:
        db_table = "wallettransaction"

admin.site.register(WalletTransaction)
admin.site.register(Wallet)
admin.site.register(WalletHistory)