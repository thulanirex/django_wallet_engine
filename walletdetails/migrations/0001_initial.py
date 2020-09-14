# Generated by Django 2.2.12 on 2020-09-10 07:14

import datetime
from django.db import migrations, models
from django.utils import timezone
import django

# def return_date_time():
#     now = timezone.now()
#     return now


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_hash', models.CharField(max_length=200, unique=True)),
                ('currency', models.CharField(choices=[('INR', 'INR'), ('SGD', 'SGD')], default='SGD', max_length=5, unique=True)),
                ('balance', models.DecimalField(decimal_places=2, default='0', max_digits=9)),
                ('last_updated_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'wallet',
            },
        ),
        migrations.CreateModel(
            name='WalletHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_hash', models.CharField(max_length=200, unique=True)),
                ('currency', models.CharField(max_length=5, unique=True)),
                ('old_balance', models.DecimalField(decimal_places=2, default='0', max_digits=9)),
                ('new_balance', models.DecimalField(decimal_places=2, default='0', max_digits=9)),
                ('last_updated_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'wallethistory',
            },
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_hash', models.CharField(max_length=200)),
                ('transaction_type', models.CharField(choices=[('CREDIT', 'Credited'), ('DEBIT', 'Debited')], max_length=10)),
                ('transaction_status', models.CharField(choices=[('SUCCESS', 'Completed Successfully'), ('IN_PROGRESS', 'Transaction is in Progress'), ('FAILED', 'Transaction failed'), ('TIMEOUT', 'TimeOut Occured'), ('INSUFFICIENT BALANCE', 'Insufficient Balance'), ('INVALID_RECEIVER', 'Receiver is not Active')], max_length=30)),
                ('recipient', models.CharField(max_length=30)),
                ('reason', models.CharField(max_length=50)),
                ('currency', models.CharField(choices=[('INR', 'INR'), ('SGD', 'SGD')], max_length=5)),
                ('amount', models.DecimalField(decimal_places=2, default='0', max_digits=9)),
                ('transaction_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'wallettransaction',
            },
        ),
    ]
