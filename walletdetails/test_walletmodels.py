
from django.test import TestCase
import decimal
from .models import  WalletTransaction, Wallet, WalletHistory
from django.apps import apps
from rest_framework.authtoken.models import Token


from rest_framework.test import APIClient

wallet_user_model = apps.get_model('user', 'WalletUser')

class WalletTest(TestCase):

    def setUp(self):
        fields= {'is_staff': False, 'is_superuser': True, 'is_active': True, 'user_type': 'SUPER_USER','email_id':'xxxxx@gmail.com'}
        wallet_user_model.objects.create_user(mobileno='+6510001000', password='YYY',**fields)

        fields = {'is_staff': False, 'is_superuser': True, 'is_active': True, 'user_type': 'ADMIN','email_id': 'xxxxx@gmail.com'}
        wallet_user_model.objects.create_user(mobileno='+6520002000', password='YYY', **fields)

        fields = {'is_staff': False, 'is_superuser': True, 'is_active': True, 'user_type': 'USER','email_id': 'xxxxx@gmail.com'}
        wallet_user_model.objects.create_user(mobileno='+6530003000', password='YYY', **fields)

        fields = {'is_staff': False, 'is_superuser': True, 'is_active': False, 'user_type': 'USER','email_id': 'xxxxx@gmail.com'}
        wallet_user_model.objects.create_user(mobileno='+6540004000', password='YYY', **fields)


    def test_create_walletuser_pass(self):
        ## creating wallet user with SGD
        Wallet.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='SGD')
        created_obj = Wallet.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550')
        self.assertTrue(created_obj is not None)

        ## creating wallet user with INR
        created_obj = Wallet.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550').values()[0]
        Wallet.objects.create(user_hash='36eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='INR')
        self.assertTrue(created_obj is not None)

    def test_create_walletuser_fail(self):
        Wallet.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='SGD')
        created_obj = Wallet.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550')
        self.assertTrue(created_obj is not None)

        ## creating wallet user with INR - expecting error
        with self.assertRaises(Exception) as context:
            Wallet.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='SGD')
            created_obj = Wallet.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550').values()[0]
            self.assertTrue('Exception should be raised' in context.exception)

    def test_create_wallethistory_pass(self):
        ## creating wallet user with SGD
        WalletHistory.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='SGD')
        created_obj = WalletHistory.objects.all().filter(user_hash='16eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550')
        self.assertTrue(created_obj is not None)

        ## creating wallet user with SGD
        WalletHistory.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='INR')
        created_obj = WalletHistory.objects.all().filter(user_hash='16eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550')
        self.assertTrue(created_obj is not None)

    def test_create_wallethistory_fail(self):
        ## creating wallet user with SGD
        Wallet.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='SGD')
        created_obj = Wallet.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550')
        self.assertTrue(created_obj is not None)

        ## creating wallet user with INR - expecting error
        with self.assertRaises(Exception) as context:
            Wallet.objects.create(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550',currency='SGD')
            created_obj = Wallet.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550').values()[0]
            self.assertTrue('Exception should be raised' in context.exception)

    def test_create_walletransaction_pass(self):
        ## creating wallet user with SGD
        created_id = WalletTransaction.objects.create(user_hash='26eeae01d2f27458d448cc7d08b3fc46a391943d66f88af7109981e41fee550', currency='SGD',transaction_type='CREDIT', transaction_status='SUCCESS', recipient='XXX', reason='EMI',amount=decimal.Decimal(100))
        created_obj = WalletTransaction.objects.all().filter(user_hash='26eeae01d2f274c58d448cc7d08b3fc46a391943d66f88af7109981e41fee550')
        self.assertTrue(created_obj is not None)

    def test_get_usage_report_pass(self):
        user = wallet_user_model.objects.get(mobileno='+6510001000')
        token, created = Token.objects.get_or_create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('http://localhost:8000/transfer/getResourceUsage',{"filter" : {"method": "POST", "remote_addr":"127.0.0.1","path": "/transfer/getBalance"}})
        assert response.status_code==200

    def test_get_transaction_pass(self):
        user = wallet_user_model.objects.get(mobileno='+6530003000')
        token, created = Token.objects.get_or_create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('http://localhost:8000/transfer/getTransaction',{ "mobileno":'+6530003000', 'currency':'SGD'})
        assert response.status_code==200

    def test_get_transaction_fail(self):
        client = APIClient()
        response = client.post('http://localhost:8000/transfer/getTransaction',{ "mobileno":'+6530003000', 'currency':'SGD'})
        assert response.status_code!=200

    def test_get_balance_pass(self):
        user = wallet_user_model.objects.get(mobileno='+6510001000')
        token, created = Token.objects.get_or_create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('http://localhost:8000/transfer/getBalance',{ "currency":'SGD'})
        assert response.status_code==200

    def test_get_balance_fail(self):
        client = APIClient()
        response = client.post('http://localhost:8000/transfer/getBalance',{ "currency":'SGD'})
        assert response.status_code!=200

    def test_get_usage_report_fail(self):
        client = APIClient()
        response = client.post('http://localhost:8000/transfer/getResourceUsage',{"filter" : {"method": "POST", "remote_addr":"127.0.0.1","path": "/transfer/getBalance"}})
        assert response.status_code!=200

    def test_transfer_fund_fail(self):
        sender = wallet_user_model.objects.get(mobileno='+6520002000')
        wallet_user_model.objects.get(mobileno='+6520002000')
        token, created = Token.objects.get_or_create(user=sender)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('http://localhost:8000/transfer/transferFunds',{"recipient": "+6530003000", "transaction_type": "CREDIT" , "amount": "10" ,"currency":"SGD" , "reason":"EMI" } )
        assert response.status_code!=200

    def test_transfer_fund_pass(self):
        sender = wallet_user_model.objects.get(mobileno='+6520002000')
        sender.name='XXX'
        sender.email='xxx@gmail.com'
        sender.save()
        wallet_user_model.objects.get(mobileno='+6520002000')
        token, created = Token.objects.get_or_create(user=sender)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('http://localhost:8000/transfer/transferFunds',{"recipient": "+6530003000", "transaction_type": "CREDIT" , "amount": "10" ,"currency":"SGD" , "reason":"EMI" } )
        assert response.status_code!=200
