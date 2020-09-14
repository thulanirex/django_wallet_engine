# import the logging library
import logging

import json
import decimal
from datetime import datetime
from datetime import timedelta
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework_tracking.models import APIRequestLog
from .walletpermission import *
from .utils import HelperUtils
from django.apps import apps
from .models import Wallet, WalletTransaction,WalletHistory
from . import Constants as const
from . import MailUtils

permission_classes = (IsAuthenticated, IsUserActive, isResourceAccessAllowed)

# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


class ParentView(LoggingMixin, generics.GenericAPIView):
    """
    wallet balance views..
    """

    def _get_view_name(self, request):
        return ""

    def _get_user(self, request):
        return None

    def _get_view_method(self, request):
        return ""

    def should_log(self, request, response):
        should_log_method = super(ParentView, self).should_log(request, response)

        if not should_log_method:
            return False
        return response.status_code >= 200

    def _clean_data(self, data):
        pass


class WalletBalanceView(ParentView):

    def post(self, request):
        """
        deals with request of walletbalance
        """
        user_obj = request.user
        currency = decode_request_body(request).get(const.CURRENCY,None)
        if not currency:
            return Response({"Reason": "Specify Wallet Currency Type"})
        hashing_val = HelperUtils.get_user_hash(user_obj,currency)
        balance = self.get_wallet_balance(hashing_val,currency)
        if balance is None:
            return Response({"Reason": const.NO_ACTIVE_WALLET})
        return Response(balance)

    def get_wallet_balance(self, hash_key,currency):
        """
        get wallet balance
        """
        balance_data= None
        wallet_data = Wallet.objects.all().filter(user_hash=hash_key,currency=currency).values()
        if not wallet_data:
            wallet_data, created = Wallet.objects.get_or_create(user_hash=hash_key,currency=currency)
            if created:
                return None
        if wallet_data:
            wallet_data = wallet_data[0]
            balance_data = [{const.CURRENT_BAL: wallet_data.get(const.BALANCE) , const.CURRENCY: wallet_data.get(const.CURRENCY)}]
        return balance_data

    def update_wallet_balance(self, hash_key, amount, type=const.CREDIT,update_history=True,currency='SGD'):
        """
        update wallet balance accordingly
        """
        try:
            wallet_obj = Wallet.objects.get(user_hash=hash_key,currency=currency)
            if not isinstance(amount,decimal.Decimal):
                amount = decimal.Decimal(amount)
            cur_balance = wallet_obj.current_balance.amount
            new_balance = wallet_obj.balance + amount if type == const.CREDIT else wallet_obj.balance - amount
            Wallet.objects.filter(user_hash= hash_key, currency=currency).update(balance = new_balance)
            if update_history:
                self.update_wallet_history(hash_key, cur_balance, new_balance)
            return True
        except Exception as e:
          print("Error in Updating Wallet Balance",e)
        return False

    def update_wallet_history(self,hash_key,old_balance, new_balance):
        try:
            WalletHistory.objects.create(user_hash=hash_key,old_balance= old_balance, new_balance = new_balance)
        except Exception as e:
            print(e)


class WalletTransactionView(ParentView):


    def post(self, request):
        """
        deals with wallet transaction
        """
        user_obj = request.user
        currency = decode_request_body(request).get(const.CURRENCY,None)
        hashing_val = HelperUtils.get_user_hash(user_obj, currency)
        status = self.transfer_fund({const.USERNAME:user_obj.mobileno, const.HASH_KEY: hashing_val , const.EMAIL: user_obj.email_id, const.NAME:user_obj.name, const.CURRENCY: currency},request)
        return Response(status)

    def get_recipient_details(self,sender, request):
        logger.info("Get Recipient details..")
        body = json.loads(request.body.decode('utf-8'))
        mobileno = body.get(const.RECIPIENT)
        wallet_model = apps.get_model(const.WALLET_USER, const.MODEL_WALLET_USER)
        data = wallet_model.objects.all().filter(mobileno= mobileno).values()
        data = data[0] if data else []
        recipient_user=  data.get(const.USERNAME,'')
        if recipient_user:
            if recipient_user != sender:
                hash_key = HelperUtils.get_user_hash(recipient_user,currency=body.get(const.CURRENCY,''))
                wallet_data = Wallet.objects.get(user_hash=hash_key,currency=body.get(const.CURRENCY,''))
                if not wallet_data:
                    raise Exception("Receiver Wallet Account Status : "+const.NO_ACTIVE_WALLET)
                if not check_if_active_user(recipient_user):
                        raise Exception(const.RECIPIENT_USER_NOT_ACTIVE)
                logger.info("validation completed")
                return {const.USERNAME: recipient_user, const.HASH_KEY: hash_key, const.NAME: data.get(const.NAME), const.EMAIL : data.get(const.EMAIL)}
            else:
                raise Exception(const.SENDER_RECIPIENT_MATCHED)
        else:
            raise Exception(const.RECIPIENT_USER_NOT_FOUND)

    def pre_validation(self,sender_info,request_info):
        """

        """
        amount_to_transfer, currency = request_info.get(const.AMOUNT), request_info.get(const.CURRENCY)
        wallet_balance = WalletBalanceView().get_wallet_balance(hash_key=sender_info.get(const.HASH_KEY,0),currency= sender_info.get(const.CURRENCY))
        if wallet_balance is None:
            logging.error("No Active Wallet Account Found for Sender")
            raise Exception(const.NO_ACTIVE_WALLET)
        wallet_balance = wallet_balance[0]
        avail_balance, avail_currency_type = wallet_balance.get(const.CURRENT_BAL,0), wallet_balance.get(const.CURRENCY)
        amount_to_transfer = decimal.Decimal(amount_to_transfer)
        if amount_to_transfer < decimal.Decimal(0):
            raise Exception(const.INVALID_AMOUNT_TRANSFER)
        if avail_currency_type != currency:
            raise Exception(const.MISMATCH_WALLET_CURRENCY_TRANSFER)
        if avail_balance >= amount_to_transfer:
            return True
        else:
            raise Exception(const.INSUFFICIENT_BALANCE)

    def add_transaction_entry(self,wallet_obj,auto_commit=False):
        obj_id = -1
        try:
            wallet_obj = WalletTransaction.objects.create(**wallet_obj)
            if auto_commit:
                wallet_obj.save()
            obj_id = wallet_obj.id
        except Exception as e:
            logger.error("Error in Initiating transaction..{0}".format(e))
        return obj_id

    def update_transaction_status(self,trans_id,status,auto_commit=False):
        """
        
        """""
        try:
            wallet_obj = WalletTransaction.objects.get(pk=trans_id)
            wallet_obj.transaction_status = status
            if auto_commit:
                wallet_obj.save()
        except Exception as e:
            logger.error("Error in updating status of transaction:{0}".format(e))

    def atomic_transaction(self,sender_info,receiver_info,request_info,receiver_wallet_trans_obj):
        is_trans_completed= False
        recipient_trans_id= None
        with transaction.atomic():
            try:
                    amount_to_update, currency_type = decimal.Decimal(request_info.get(const.AMOUNT)), request_info.get(const.CURRENCY)
                    if WalletBalanceView().update_wallet_balance(sender_info.get(const.HASH_KEY), amount_to_update, type=const.DEBIT, update_history= True):
                        if WalletBalanceView().update_wallet_balance(receiver_info.get(const.HASH_KEY), amount_to_update , type=const.CREDIT,update_history=True):
                            recipient_trans_id = self.add_transaction_entry(receiver_wallet_trans_obj)
                            is_trans_completed= True
                            logging.info("Transaction is Completed...")
                    else:
                        raise Exception(const.WALLET_BALANCE_UPDATE_FAILED)
            except Exception as e:
                transaction.set_rollback(True)
                logger.error("Transaction flow.... interrupted..: {0} ".format(e))
        return is_trans_completed , recipient_trans_id

    def initiate_transfer(self,sender_info, receiver_info, request_info):
        sender_wallet_trans_obj = {const.user_hash: sender_info.get(const.HASH_KEY),
                            const.TRANSACTION_TYPE: const.DEBIT,
                            const.TRANSACTION_STATUS: const.INPROGRESS,
                            const.RECIPIENT: receiver_info.get(const.USERNAME), const.REASON: request_info.get(const.REASON),
                            const.CURRENCY: request_info.get(const.CURRENCY), const.AMOUNT: request_info.get(const.AMOUNT),
                                   const.NAME: sender_info.get(const.NAME,''),
                                   const.EMAIL: sender_info.get(const.EMAIL,'') }

        receiver_wallet_trans_obj = {const.user_hash: receiver_info.get(const.HASH_KEY),
                            const.TRANSACTION_TYPE: const.CREDIT,const.TRANSACTION_STATUS: const.SUCCESS,const.RECIPIENT: receiver_info.get(const.USERNAME),
                                     const.REASON: request_info.get(const.REASON),
                            const.CURRENCY: request_info.get(const.CURRENCY), const.AMOUNT: request_info.get(const.AMOUNT),
                                     const.NAME:receiver_info.get(const.NAME), const.EMAIL:receiver_info.get(const.EMAIL)}
        sender_trans_id = self.add_transaction_entry(sender_wallet_trans_obj,auto_commit=True)
        is_completed, recipient_trans_id = self.atomic_transaction(sender_info,receiver_info,request_info,receiver_wallet_trans_obj)
        self.update_transaction_status(sender_trans_id, status=const.SUCCESS if is_completed else const.FAILED,auto_commit=True)
        self.prepare_notification(sender_wallet_trans_obj, receiver_wallet_trans_obj, is_completed)
        return is_completed

    def prepare_notification(self,sender_wallet_trans_obj,receiver_wallet_trans_obj, is_completed):
        """
        prepare mail content..
        """
        if is_completed:
            wallet_balance = WalletBalanceView().get_wallet_balance(sender_wallet_trans_obj.get(const.user_hash,''),sender_wallet_trans_obj.get(const.CURRENCY))
            wallet_balance = wallet_balance[0]
            avail_balance, avail_currency_type = wallet_balance.get(const.CURRENT_BAL,0), wallet_balance.get(const.CURRENCY)
            sender_mail_body = """ Hi {0}, \n Your MobileWallet2020 has been {1} with amount {2}{3}. Updated Balance is :{4}{5}""".\
                format(sender_wallet_trans_obj.get(const.NAME,''),sender_wallet_trans_obj.get(const.TRANSACTION_TYPE,'')+'ED',
                       sender_wallet_trans_obj.get(const.AMOUNT), sender_wallet_trans_obj.get(const.CURRENCY),
                       avail_balance, avail_currency_type)

            MailUtils.send_notification(subject='MobileWallet2020 Transaction Account Status', body_content=sender_mail_body, recipients=[sender_wallet_trans_obj.get(const.EMAIL,'')])

            wallet_balance = WalletBalanceView().get_wallet_balance(receiver_wallet_trans_obj.get(const.user_hash,''), receiver_wallet_trans_obj.get(const.CURRENCY))
            wallet_balance = wallet_balance[0]
            avail_balance, avail_currency_type = wallet_balance.get(const.CURRENT_BAL,0), wallet_balance.get(const.CURRENCY)
            recipient_mail_body = """ Hi {0}, \n Your MobileWallet2020 has been {1} with amount {2}{3}. Updated Balance is :{4}{5}""". \
                format(receiver_wallet_trans_obj.get(const.NAME,''),receiver_wallet_trans_obj.get(const.TRANSACTION_TYPE, '') + 'ED',
                       receiver_wallet_trans_obj.get(const.AMOUNT), receiver_wallet_trans_obj.get(const.CURRENCY),
                       avail_balance, avail_currency_type)

            MailUtils.send_notification(subject='MobileWallet2020 Transaction Account Status',
                                        body_content=recipient_mail_body,
                                        recipients=[receiver_wallet_trans_obj.get(const.EMAIL, '')])

    def transfer_fund(self, sender_info, request):
        """
        transfer funds between wallets.
        """
        logger.info("Triggering Transaction...")
        response_status = {const.TRANSACTION_STATUS: ""}
        try:
            request_info = decode_request_body(request)
            logger.info("Start validation...")
            if self.pre_validation(sender_info,request_info):
                logger.info("validation Completed....")
                receiver_info = self.get_recipient_details(sender_info[const.USERNAME], request) ## validation completed ..
                logger.info("Initiate Transaction....")
                status = self.initiate_transfer(sender_info, receiver_info, request_info)
                logger.info("Transaction over.. checking status")
                response_status[const.TRANSACTION_STATUS] = const.SUCCESS if status else const.FAILED
        except Exception as e:
            response_status[const.TRANSACTION_STATUS] = const.FAILED
            response_status[const.REASON] = str(e)
            logger.error(response_status)
        return response_status


class WalletHistoryView(ParentView):

    def post(self, request):
        """

        """
        user_obj = request.user
        currency = decode_request_body(request).get(const.CURRENCY,None)
        hashing_val = HelperUtils.get_user_hash(user_obj,currency)
        req_body = decode_request_body(request)
        balance = self.getTransaction(hashing_val,user_obj.mobileno, req_body)
        return Response(balance)

    def get_date_range(self, req_body):
        try:
            start_date, end_date = req_body.get(const.STARTDATE), req_body.get(const.ENDDATE)
            if not (start_date and end_date):
                return False, None, None
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            today_date = datetime.strptime(datetime.today().strftime('%d-%m-%Y'), '%d-%m-%Y').date()
            print(start_date, end_date, today_date)
            if start_date > today_date or start_date > end_date or end_date > today_date:
                raise Exception(const.NOT_VALID_DATE_RANGE)
            end_date += timedelta(days=1)
            end_date = end_date.strftime('%d-%m-%Y')
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            return True, start_date, end_date
        except Exception as e:
            logger.error("Error in Date Range Request Param parsing..",e)
            raise Exception(const.NOT_VALID_DATE_RANGE)

    def getTransaction(self, hash_key,mobileno,req_body):
        """
        reterive transaction details for the given user.
        """
        transaction_data = []
        if mobileno != req_body.get(const.USERNAME):
            return {'Request Failed': const.MOBILE_NO_NOT_BELONGS_TO_CURRENT_USER}
            #raise Exception(const.MOBILE_NO_NOT_BELONGS_TO_CURRENT_USER)
        is_range_provided , start_date, end_date = self.get_date_range(req_body)
        if is_range_provided:
            wallet_data = WalletTransaction.objects.all().filter(user_hash=hash_key, transaction_date__range=(start_date,end_date)).values()
        else:
            wallet_data = WalletTransaction.objects.all().filter(user_hash=hash_key).values()
        #header = wallet_data[0].keys() if wallet_data else []
        export_data =[]
        for data in wallet_data:
            data_to_update= {const.SENDER:str(mobileno.country_code)+"-" + str(mobileno.national_number),
                             const.TRANSACTION_DATE: data.get(const.TRANSACTION_DATE),
                             const.TRANSACTION_TYPE: data.get(const.TRANSACTION_TYPE),
                             const.AMOUNT: data.get(const.AMOUNT),
                             const.CURRENCY: data.get(const.CURRENCY),
                             const.RECIPIENT: data.get(const.RECIPIENT),
                             const.TRANSACTION_STATUS: data.get(const.TRANSACTION_STATUS),
                             const.REASON: data[const.REASON]}
            transaction_data.append(data_to_update)
        return transaction_data

def decode_request_body(request):
    body = json.loads(request.body.decode('utf-8'))
    logger.info("Getting Request params")
    return body


def check_if_active_user(recipient_user):
    mymodel = apps.get_model(const.WALLET_USER, const.MODEL_WALLET_USER)
    user_obj = mymodel.objects.all().filter(mobileno=recipient_user, is_active= True).values()
    if not user_obj:
        logger.error("User is not active, could not process any request..")
        raise Exception(const.USER_IS_NOT_ACTIVE)
    return True


class ResourceUsage(APIView):
    """
    resource usage data
    """
    def post(self, request):
        body = decode_request_body(request)
        filter_params = body.get('filter',{})
        if not filter_params:
            logging.info("Specified path is not specified. Hence , Retrieve Usage report of all transfer Api Calls..")
            usage_data = APIRequestLog.objects.all().values().values('path','method','remote_addr','status_code','requested_at','response_ms')
        else:
            usage_data = APIRequestLog.objects.all().filter(**filter_params).values('path','method','remote_addr','status_code','requested_at','response_ms')
        if not usage_data:
            return Response({"Response: No Resource Usage Data found for the given path"})
        return Response({'Data': usage_data})
